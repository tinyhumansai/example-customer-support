"""Page 5 — UC4: Personalized Customer Support Chat."""

import json
import os
import time
from pathlib import Path

import streamlit as st
from tinyhumansai import MemoryItem

from lib.client import get_client
from lib.support_agent import generate_support_response

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.header("Customer Context")
st.caption(
    "Personalized support — the agent remembers past interactions, plan details, "
    "and preferences for each customer."
)

# Load customers for selector
with open(DATA_DIR / "customers.json") as f:
    customers_data = json.load(f)

customer_map = {c["name"]: c for c in customers_data}
selected_name = st.selectbox("Select customer", list(customer_map.keys()))
customer = customer_map[selected_name]

# Show customer profile
with st.expander("Customer Profile", expanded=True):
    col1, col2, col3 = st.columns(3)
    col1.metric("Plan", customer["plan"])
    col2.metric("Seats", customer["seats"])
    col3.metric("Preferred Channel", customer["contact"]["preferred_channel"])
    st.write(f"**Contact**: {customer['contact']['name']} — {customer['contact']['role']}")
    st.write(f"**Email**: {customer['contact']['email']}")
    st.caption(customer["notes"])

# Show past interactions from memory
st.divider()
st.subheader("Past Interactions (from memory)")

client = get_client()
try:
    past_ctx = client.recall_memory(
        namespace=f"customer:{customer['id']}",
        prompt="all past interactions and customer details",
        num_chunks=10,
    )
    if past_ctx.count > 0:
        for item in past_ctx.items:
            meta = item.metadata
            if meta.get("type") == "profile":
                continue
            st.markdown(f"- {item.content}")
    else:
        st.info("No past interactions found. Seed data first from the Seed Data page.")
except Exception:
    st.info("No past interactions found. Seed data first from the Seed Data page.")

# Chat interface
st.divider()
st.subheader("Support Chat")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Display chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input(f"Message as {customer['contact']['name']}..."):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_support_response(
                client=client,
                query=prompt,
                customer_id=customer["id"],
            )
        st.markdown(response.answer)

        # Show context sources in collapsible
        with st.expander("Context sources used"):
            if response.kb_context and response.kb_context.count > 0:
                st.caption(f"KB articles: {response.kb_context.count}")
            if response.ticket_context and response.ticket_context.count > 0:
                st.caption(f"Similar tickets: {response.ticket_context.count}")
            if response.community_context and response.community_context.count > 0:
                st.caption(f"Community posts: {response.community_context.count}")
            if response.customer_context and response.customer_context.count > 0:
                st.caption(f"Customer history items: {response.customer_context.count}")

    st.session_state.chat_messages.append({"role": "assistant", "content": response.answer})

    # Ingest this interaction back into customer memory
    now = time.time()
    try:
        client.ingest_memory(
            item=MemoryItem(
                key=f"{customer['id']}-chat-{int(now)}",
                content=f"[{time.strftime('%Y-%m-%d')}] (support-chat): Customer asked: {prompt}\n\nAgent response: {response.answer[:500]}",
                namespace=f"customer:{customer['id']}",
                metadata={"type": "interaction", "date": time.strftime("%Y-%m-%d"), "interaction_type": "support-chat"},
                created_at=now,
                updated_at=now,
            )
        )
    except Exception:
        pass  # Don't break chat if memory ingestion fails
