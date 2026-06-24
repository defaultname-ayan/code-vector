# ProductsDB — CodeVector Product API

FastAPI backend with cursor-based pagination over 200K products, served with a vanilla HTML/JS frontend.

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and route handlers
│   ├── database.py      # SQLAlchemy engine and session setup
│   ├── models.py        # Product ORM model with indexes
│   ├── schemas.py       # Pydantic response schemas
│   └── cursor.py        # Cursor encoding/decoding for keyset pagination
├── static/
│   └── index.html       # Frontend UI
├── scripts/
│   ├── __init__.py
│   └── seed.py          # Bulk-insert 200K products via PostgreSQL COPY
├── .env.example         # Template for environment variables
├── .gitignore
├── requirements.txt     # Python dependencies
└── README.md
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and set your PostgreSQL connection string:

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 3. Seed the database (200K products)

```bash
python -m scripts.seed
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API Endpoints

| Method | Path                  | Description                              |
|--------|-----------------------|------------------------------------------|
| GET    | `/`                   | Serves the frontend UI                   |
| GET    | `/health`             | Health check                             |
| GET    | `/categories`         | List all valid categories                |
| GET    | `/products`           | Paginated product list (cursor-based)    |
| GET    | `/products/new-count` | Count of products added after a timestamp|

## How Pagination Works

This API uses **keyset (cursor-based) pagination** instead of OFFSET/LIMIT:

- **First request**: No cursor. The server timestamps the session and returns page 1.
- **Next pages**: Pass `next_cursor` from the previous response. The cursor encodes the session start time plus the position of the last item.
- **Back navigation**: The frontend caches pages locally. Going back renders from cache.
- **No duplicates, no skips**: The session timestamp freezes the result set. New inserts after the session started are invisible until the user refreshes.
- **Live polling**: The frontend polls `/products/new-count` every 15 seconds and shows a banner when new products are detected.
