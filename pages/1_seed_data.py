"""Page 1 — Seed & manage sample data."""

import json
from pathlib import Path

import streamlit as st
from lib.client import get_client
from lib.seed import seed_all, clear_all

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.header("Seed Data")
st.caption("Load sample data into Neocortex memory namespaces for the demo.")

# Show data summary
col1, col2, col3, col4 = st.columns(4)
with open(DATA_DIR / "community_posts.json") as f:
    community = json.load(f)
with open(DATA_DIR / "resolved_tickets.json") as f:
    tickets = json.load(f)
with open(DATA_DIR / "kb_articles.json") as f:
    kb = json.load(f)
with open(DATA_DIR / "customers.json") as f:
    customers = json.load(f)

col1.metric("Community Posts", len(community))
col2.metric("Resolved Tickets", len(tickets))
col3.metric("KB Articles", len(kb))
customer_interactions = sum(len(c.get("interactions", [])) for c in customers)
col4.metric("Customers / Interactions", f"{len(customers)} / {customer_interactions}")

st.divider()

# Namespace details
with st.expander("Namespace mapping"):
    st.markdown("""
| Namespace | Source | Purpose |
|---|---|---|
| `community-solutions` | `community_posts.json` | Forum/Discord crowd-sourced fixes |
| `resolved-tickets` | `resolved_tickets.json` | Historical ticket resolutions |
| `knowledge-base` | `kb_articles.json` | Official KB articles (incl. deprecated) |
| `customer:{id}` | `customers.json` | Per-customer profile + interaction history |
""")

st.divider()

# Actions
left, right = st.columns(2)

with left:
    if st.button("Seed All Data", type="primary", use_container_width=True):
        client = get_client()
        with st.spinner("Ingesting data into Neocortex..."):
            results = seed_all(client)
        st.success("Data seeded successfully!")

        for label, data in results.items():
            if label == "customers":
                st.write(f"**Customers**: {data['total_customer_items']} items across {len(data['details'])} namespaces")
                for d in data["details"]:
                    r = d["result"]
                    st.caption(f"  `{d['namespace']}`: {d['count']} items — ingested={r.ingested}, updated={r.updated}")
            else:
                r = data["result"]
                st.write(f"**{label}** (`{data['namespace']}`): {data['count']} items — ingested={r.ingested}, updated={r.updated}")

with right:
    if st.button("Clear All Data", type="secondary", use_container_width=True):
        client = get_client()
        with st.spinner("Deleting all namespaces..."):
            deleted = clear_all(client)
        st.warning("All data cleared.")
        for ns, count in deleted.items():
            st.caption(f"`{ns}`: {count} deleted")
