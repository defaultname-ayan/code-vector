import os
import random
import time
from datetime import datetime, timedelta, timezone
from io import StringIO
import csv

import psycopg2
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = [
    "Electronics", "Clothing", "Books", "Home & Kitchen",
    "Sports", "Toys", "Beauty", "Automotive", "Grocery", "Music"
]

ADJECTIVES = [
    "Premium", "Pro", "Ultra", "Classic", "Smart", "Lite", "Max",
    "Mini", "Plus", "Elite", "Basic", "Advanced", "Compact", "Deluxe",
    "Portable", "Wireless", "Organic", "Vintage", "Modern", "Eco"
]

NOUNS = {
    "Electronics":    ["Laptop", "Phone", "Tablet", "Headphones", "Camera", "Speaker", "Monitor", "Keyboard", "Mouse", "Charger"],
    "Clothing":       ["Jacket", "Shirt", "Jeans", "Sneakers", "Hoodie", "Dress", "Shorts", "Socks", "Cap", "Belt"],
    "Books":          ["Novel", "Textbook", "Journal", "Diary", "Atlas", "Cookbook", "Guide", "Manual", "Biography", "Comic"],
    "Home & Kitchen": ["Blender", "Toaster", "Pan", "Knife Set", "Lamp", "Cushion", "Mug", "Towel", "Shelf", "Clock"],
    "Sports":         ["Dumbbell", "Yoga Mat", "Racket", "Gloves", "Bottle", "Bag", "Shoes", "Jersey", "Helmet", "Cycle"],
    "Toys":           ["Lego Set", "Puzzle", "Doll", "Car", "Board Game", "Kite", "Train", "Robot", "Ball", "Blocks"],
    "Beauty":         ["Serum", "Moisturizer", "Lipstick", "Foundation", "Perfume", "Shampoo", "Mask", "Toner", "Oil", "Brush"],
    "Automotive":     ["Charger", "Cover", "Wiper", "Polish", "Mat", "Lock", "Mirror", "Filter", "Cable", "Pump"],
    "Grocery":        ["Oats", "Coffee", "Tea", "Honey", "Nuts", "Pasta", "Rice", "Oil", "Sauce", "Spice"],
    "Music":          ["Guitar", "Ukulele", "Drum Kit", "Keyboard", "Microphone", "Cable", "Pick", "Stand", "Strap", "Tuner"],
}

TOTAL = 200_000
BATCH_SIZE = 10_000


def random_name(category: str) -> str:
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS[category])
    return f"{adj} {noun}"


def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def seed():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          BIGSERIAL PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            price       NUMERIC(10, 2) NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_products_cursor
            ON products (created_at DESC, id DESC);

        CREATE INDEX IF NOT EXISTS idx_products_category_cursor
            ON products (category, created_at DESC, id DESC);

        CREATE INDEX IF NOT EXISTS idx_products_created_at
            ON products (created_at);
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM products")
    existing = cur.fetchone()[0]
    if existing >= TOTAL:
        print(f"Already have {existing:,} products. Skipping seed.")
        cur.close()
        conn.close()
        return

    to_insert = TOTAL - existing
    print(f"Inserting {to_insert:,} products in batches of {BATCH_SIZE:,}...")

    start_dt = datetime.now(timezone.utc) - timedelta(days=365 * 2)
    end_dt = datetime.now(timezone.utc)

    inserted = 0
    t0 = time.time()

    while inserted < to_insert:
        batch_count = min(BATCH_SIZE, to_insert - inserted)

        buf = StringIO()
        writer = csv.writer(buf)
        for _ in range(batch_count):
            category = random.choice(CATEGORIES)
            name = random_name(category)
            price = round(random.uniform(9.99, 4999.99), 2)
            created_at = random_datetime(start_dt, end_dt)
            updated_at = random_datetime(created_at, end_dt)
            writer.writerow([name, category, price, created_at.isoformat(), updated_at.isoformat()])

        buf.seek(0)
        cur.copy_expert(
            "COPY products (name, category, price, created_at, updated_at) FROM STDIN WITH CSV",
            buf
        )
        conn.commit()

        inserted += batch_count
        elapsed = time.time() - t0
        rate = inserted / elapsed
        eta = (to_insert - inserted) / rate if rate > 0 else 0
        print(f"  {inserted:>7,} / {to_insert:,} inserted  ({rate:,.0f} rows/s)  ETA: {eta:.0f}s")

    total_time = time.time() - t0
    print(f"\nDone! {to_insert:,} products inserted in {total_time:.1f}s")

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed()