"""Page 2 — UC1: Community Knowledge Search."""

import os

import streamlit as st
from lib.client import get_client

st.header("Community Knowledge")
st.caption(
    "Search crowd-sourced solutions from forums and Discord — "
    "instantly findable without manual curation."
)

EXAMPLE_QUERIES = [
    "How do I fix sync conflicts?",
    "API rate limit workaround",
    "SSO setup with Azure AD",
    "Mobile app keeps crashing",
    "Webhook delivery failures",
    "How to reduce desktop client CPU usage",
    "Migrating from Dropbox",
    "Shared link security best practices",
]

selected = st.selectbox("Example queries", ["(type your own)"] + EXAMPLE_QUERIES)
query = st.text_input(
    "Ask a question",
    value="" if selected == "(type your own)" else selected,
    placeholder="e.g., How do I fix sync conflicts?",
)

num_chunks = st.slider("Number of results to recall", 1, 10, 5)

if st.button("Search", type="primary") and query:
    client = get_client()

    # Step 1: Recall from community namespace
    with st.spinner("Recalling from community-solutions..."):
        ctx = client.recall_memory(
            namespace="community-solutions",
            prompt=query,
            num_chunks=num_chunks,
        )

    st.subheader(f"Recalled {ctx.count} community solutions")

    for item in ctx.items:
        meta = item.metadata
        with st.expander(f"{item.key} — {meta.get('source', '?')} / {meta.get('channel', '?')}"):
            cols = st.columns(3)
            cols[0].caption(f"Author: {meta.get('author', 'unknown')}")
            cols[1].caption(f"Upvotes: {meta.get('upvotes', 0)}")
            cols[2].caption(f"Date: {meta.get('date', '?')}")
            st.markdown(item.content)

    st.divider()

    # Step 2: Generate synthesized answer via LLM
    st.subheader("AI-Generated Answer")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        st.error("Set OPENAI_API_KEY in .env to enable LLM responses.")
    else:
        with st.spinner("Generating response..."):
            llm_resp = client.recall_with_llm(
                prompt=query,
                provider="openai",
                model="gpt-4o-mini",
                api_key=openai_key,
                context=ctx.context,
            )
        st.markdown(llm_resp.text)
