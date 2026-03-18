"""Page 4 — UC3: Knowledge Base Evolution (deprecate / reinforce / add)."""

import json
import os
import time
from pathlib import Path

import streamlit as st
from tinyhumansai import MemoryItem

from lib.client import get_client

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

st.header("Knowledge Base Evolution")
st.caption(
    "Demonstrate how knowledge naturally evolves: stale articles get pruned, "
    "good articles get reinforced, and new knowledge is added."
)

# Load KB articles for reference
with open(DATA_DIR / "kb_articles.json") as f:
    kb_articles = json.load(f)

# Show article inventory
st.subheader("Article Inventory")
for art in kb_articles:
    meta = art["metadata"]
    status_icon = "deprecated" if meta.get("status") == "deprecated" else "current"
    cols = st.columns([3, 1, 1, 1])
    cols[0].write(f"**{art['key']}**")
    cols[1].write(f"Version: {meta.get('version', '?')}")
    cols[2].write(f"Status: {status_icon}")
    cols[3].write(f"Category: {meta.get('category', '?')}")

st.divider()

# Query interface
st.subheader("Query the Knowledge Base")

EXAMPLE_QUERIES = [
    "How do I authenticate with the API?",
    "How do I set up desktop sync?",
    "How do I share files externally?",
    "How do I manage users and roles?",
    "Backup and disaster recovery options",
]

selected = st.selectbox("Example queries", ["(type your own)"] + EXAMPLE_QUERIES)
query = st.text_input(
    "Search knowledge base",
    value="" if selected == "(type your own)" else selected,
    placeholder="e.g., How do I authenticate with the API?",
)

if st.button("Search KB", type="primary") and query:
    client = get_client()

    with st.spinner("Recalling from knowledge-base..."):
        ctx = client.recall_memory(
            namespace="knowledge-base",
            prompt=query,
            num_chunks=5,
        )

    st.subheader(f"Found {ctx.count} articles")
    st.session_state["kb_results"] = ctx

    for idx, item in enumerate(ctx.items):
        meta = item.metadata
        is_deprecated = meta.get("status") == "deprecated"
        label = f"{'DEPRECATED — ' if is_deprecated else ''}{item.key} (v{meta.get('version', '?')})"

        with st.expander(label, expanded=not is_deprecated):
            st.markdown(item.content)
            st.caption(
                f"Category: {meta.get('category', '?')} | "
                f"Created: {meta.get('created_date', '?')} | "
                f"Updated: {meta.get('last_updated', meta.get('deprecated_date', '?'))}"
            )

            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if is_deprecated:
                    if st.button("Remove deprecated article", key=f"deprecate-{idx}"):
                        with st.spinner("Deleting..."):
                            client.delete_memory(namespace="knowledge-base", key=item.key)
                        st.success(f"Deleted `{item.key}` from knowledge base.")
                        st.info("Re-run the query to see updated results.")
                else:
                    if st.button("Reinforce (mark as reliable)", key=f"reinforce-{idx}"):
                        new_meta = dict(meta)
                        new_meta["reinforced_at"] = time.strftime("%Y-%m-%d")
                        new_meta["reinforcement_count"] = meta.get("reinforcement_count", 0) + 1
                        with st.spinner("Reinforcing..."):
                            client.ingest_memory(
                                item=MemoryItem(
                                    key=item.key,
                                    content=item.content,
                                    namespace="knowledge-base",
                                    metadata=new_meta,
                                    updated_at=time.time(),
                                )
                            )
                        st.success(f"Reinforced `{item.key}` — updated timestamp and reinforcement count.")

    # LLM answer
    st.divider()
    st.subheader("AI Answer")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        st.error("Set OPENAI_API_KEY in .env to enable LLM responses.")
    elif ctx.count > 0:
        with st.spinner("Generating answer..."):
            llm_resp = client.recall_with_llm(
                prompt=query,
                provider="openai",
                model="gpt-4o-mini",
                api_key=openai_key,
                context=ctx.context,
            )
        st.markdown(llm_resp.text)

st.divider()

# Add new article
st.subheader("Add New KB Article")
with st.form("add_article"):
    new_key = st.text_input("Article key", placeholder="kb-new-feature-guide")
    new_content = st.text_area("Article content (Markdown)", height=200)
    new_category = st.selectbox("Category", ["api", "features", "desktop", "mobile", "admin", "security"])
    new_version = st.text_input("Version", value="v2")
    submitted = st.form_submit_button("Add Article")

    if submitted and new_key and new_content:
        client = get_client()
        now = time.time()
        with st.spinner("Ingesting new article..."):
            client.ingest_memory(
                item=MemoryItem(
                    key=new_key,
                    content=new_content,
                    namespace="knowledge-base",
                    metadata={
                        "version": new_version,
                        "status": "current",
                        "category": new_category,
                        "created_date": time.strftime("%Y-%m-%d"),
                        "last_updated": time.strftime("%Y-%m-%d"),
                    },
                    created_at=now,
                    updated_at=now,
                )
            )
        st.success(f"Article `{new_key}` added to knowledge base!")
