"""
Export service: converts transaction records to CSV or JSON bytes.
Kept as pure functions so they're easy to unit-test independently.
"""

import csv
import io
import json
from datetime import date, datetime
from typing import Literal

from ..models import Transaction


def _tx_to_dict(tx: Transaction) -> dict:
    return {
        "id":         tx.id,
        "amount":     tx.amount,
        "type":       tx.type.value,
        "category":   tx.category,
        "date":       str(tx.date),
        "notes":      tx.notes or "",
        "user_id":    tx.user_id,
        "created_at": str(tx.created_at),
    }


def to_csv(transactions: list[Transaction]) -> bytes:
    """Serialize transactions to UTF-8 encoded CSV bytes."""
    output  = io.StringIO()
    writer  = csv.DictWriter(
        output,
        fieldnames=["id", "amount", "type", "category", "date", "notes", "user_id", "created_at"],
    )
    writer.writeheader()
    for tx in transactions:
        writer.writerow(_tx_to_dict(tx))
    return output.getvalue().encode("utf-8")


def to_json(transactions: list[Transaction]) -> bytes:
    """Serialize transactions to pretty-printed JSON bytes."""
    data = [_tx_to_dict(tx) for tx in transactions]
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
