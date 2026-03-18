"""Load sample JSON data and ingest into Neocortex memory namespaces."""

import json
import time
from pathlib import Path

from tinyhumansai import TinyHumanMemoryClient, MemoryItem

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NAMESPACES = [
    "community-solutions",
    "resolved-tickets",
    "knowledge-base",
]


def _load_json(filename: str) -> list[dict]:
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def _make_items(records: list[dict], namespace: str) -> list[MemoryItem]:
    now = time.time()
    items = []
    for r in records:
        items.append(
            MemoryItem(
                key=r["key"],
                content=r["content"],
                namespace=namespace,
                metadata=r.get("metadata", {}),
                created_at=now,
                updated_at=now,
            )
        )
    return items


def seed_community(client: TinyHumanMemoryClient) -> dict:
    records = _load_json("community_posts.json")
    items = _make_items(records, "community-solutions")
    result = client.ingest_memories(items=items)
    return {"namespace": "community-solutions", "count": len(records), "result": result}


def seed_tickets(client: TinyHumanMemoryClient) -> dict:
    records = _load_json("resolved_tickets.json")
    items = _make_items(records, "resolved-tickets")
    result = client.ingest_memories(items=items)
    return {"namespace": "resolved-tickets", "count": len(records), "result": result}


def seed_kb(client: TinyHumanMemoryClient) -> dict:
    records = _load_json("kb_articles.json")
    items = _make_items(records, "knowledge-base")
    result = client.ingest_memories(items=items)
    return {"namespace": "knowledge-base", "count": len(records), "result": result}


def seed_customers(client: TinyHumanMemoryClient) -> dict:
    customers = _load_json("customers.json")
    total = 0
    results = []
    for cust in customers:
        ns = f"customer:{cust['id']}"
        items = []
        now = time.time()
        # Ingest customer profile
        profile_content = (
            f"Customer: {cust['name']}\n"
            f"Plan: {cust['plan']} ({cust['seats']} seats)\n"
            f"Contact: {cust['contact']['name']} — {cust['contact']['role']}\n"
            f"Email: {cust['contact']['email']}\n"
            f"Preferred channel: {cust['contact']['preferred_channel']}\n"
            f"Notes: {cust['notes']}"
        )
        items.append(
            MemoryItem(
                key=f"{cust['id']}-profile",
                content=profile_content,
                namespace=ns,
                metadata={"type": "profile", "plan": cust["plan"]},
                created_at=now,
                updated_at=now,
            )
        )
        # Ingest interactions
        for ix in cust.get("interactions", []):
            items.append(
                MemoryItem(
                    key=ix["key"],
                    content=f"[{ix['date']}] ({ix['type']}): {ix['summary']}",
                    namespace=ns,
                    metadata={"type": "interaction", "date": ix["date"], "interaction_type": ix["type"]},
                    created_at=now,
                    updated_at=now,
                )
            )
        result = client.ingest_memories(items=items)
        total += len(items)
        results.append({"namespace": ns, "count": len(items), "result": result})
    return {"total_customer_items": total, "details": results}


def seed_all(client: TinyHumanMemoryClient) -> dict:
    return {
        "community": seed_community(client),
        "tickets": seed_tickets(client),
        "kb": seed_kb(client),
        "customers": seed_customers(client),
    }


def clear_all(client: TinyHumanMemoryClient) -> dict:
    deleted = {}
    for ns in NAMESPACES:
        try:
            resp = client.delete_memory(namespace=ns, delete_all=True)
            deleted[ns] = resp.deleted
        except Exception:
            deleted[ns] = 0

    # Clear customer namespaces
    customers = _load_json("customers.json")
    for cust in customers:
        ns = f"customer:{cust['id']}"
        try:
            resp = client.delete_memory(namespace=ns, delete_all=True)
            deleted[ns] = resp.deleted
        except Exception:
            deleted[ns] = 0
    return deleted
