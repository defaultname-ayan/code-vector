from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timezone
import os

from app.database import get_db, engine
from app.models import Base, Product
from app.schemas import ProductsResponse, ProductOut, NewCountResponse
from app.cursor import encode_cursor, decode_cursor, now_utc

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeVector Product API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

VALID_CATEGORIES = [
    "Electronics", "Clothing", "Books", "Home & Kitchen",
    "Sports", "Toys", "Beauty", "Automotive", "Grocery", "Music"
]

PAGE_SIZE = 20


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"), media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def get_categories():
    return {"categories": VALID_CATEGORIES}


@app.get("/products", response_model=ProductsResponse)
def get_products(
    cursor: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    if cursor is None:
        session_start = now_utc()

        query = db.query(Product).filter(Product.created_at <= session_start)

        if category:
            query = query.filter(Product.category == category)

        total = query.count()

        products = (
            query
            .order_by(Product.created_at.desc(), Product.id.desc())
            .limit(PAGE_SIZE)
            .all()
        )

        if not products:
            return ProductsResponse(
                data=[],
                next_cursor=None,
                has_more=False,
                total_in_session=0,
            )

        last = products[-1]
        next_cur = encode_cursor(session_start, last.created_at, last.id) if len(products) == PAGE_SIZE else None

        return ProductsResponse(
            data=[ProductOut.model_validate(p) for p in products],
            next_cursor=next_cur,
            has_more=next_cur is not None,
            total_in_session=total,
        )

    try:
        session_start, last_created_at, last_id = decode_cursor(cursor)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cursor")

    if session_start.tzinfo is None:
        session_start = session_start.replace(tzinfo=timezone.utc)
    if last_created_at.tzinfo is None:
        last_created_at = last_created_at.replace(tzinfo=timezone.utc)

    keyset_filter = text(
        "(created_at, id) < (:last_created_at, :last_id)"
    ).bindparams(last_created_at=last_created_at, last_id=last_id)

    query = (
        db.query(Product)
        .filter(Product.created_at <= session_start)
        .filter(keyset_filter)
    )

    if category:
        query = query.filter(Product.category == category)

    total_query = db.query(Product).filter(Product.created_at <= session_start)
    if category:
        total_query = total_query.filter(Product.category == category)
    total = total_query.count()

    products = (
        query
        .order_by(Product.created_at.desc(), Product.id.desc())
        .limit(PAGE_SIZE)
        .all()
    )

    if not products:
        return ProductsResponse(
            data=[],
            next_cursor=None,
            has_more=False,
            total_in_session=total,
        )

    last = products[-1]
    next_cur = encode_cursor(session_start, last.created_at, last.id) if len(products) == PAGE_SIZE else None

    return ProductsResponse(
        data=[ProductOut.model_validate(p) for p in products],
        next_cursor=next_cur,
        has_more=next_cur is not None,
        total_in_session=total,
    )


@app.get("/products/new-count", response_model=NewCountResponse)
def get_new_count(
    since: str = Query(...),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        since_dt = datetime.fromisoformat(since)
        if since_dt.tzinfo is None:
            since_dt = since_dt.replace(tzinfo=timezone.utc)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid since timestamp")

    query = db.query(Product).filter(Product.created_at > since_dt)

    if category:
        query = query.filter(Product.category == category)

    return NewCountResponse(count=query.count())
