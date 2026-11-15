"""
Generator for synthetic next_offer test data.

Usage (inside container or local venv):
    python scripts/generate_data.py --clients 100 --transactions 1000
"""

import argparse
import os
from sqlalchemy import create_engine, text


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clients", type=int, default=20)
    parser.add_argument("--transactions", type=int, default=200)
    parser.add_argument(
        "--database-url",
        default=os.getenv(
            "DATABASE_URL", "postgresql+psycopg://next_offer:change_me@localhost:5432/next_offer"
        ),
    )
    return parser.parse_args()


def generate(engine, clients_count: int, transactions_count: int):
    with engine.connect() as conn:
        # TODO: implement synthetic data generation
        result = conn.execute(text("SELECT COUNT(*) FROM clients")).scalar()
        print(f"Current clients count: {result}")
        print(f"Would generate {clients_count} clients and {transactions_count} transactions")
        conn.commit()


def main():
    args = parse_args()
    engine = create_engine(args.database_url)
    generate(engine, args.clients, args.transactions)


if __name__ == "__main__":
    main()
