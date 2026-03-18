"""Page 3 — UC2: Ticket Resolution with Reinforcement."""

import os
import time

import streamlit as st
from tinyhumansai import MemoryItem

from lib.client import get_client

st.header("Ticket Resolution")
st.caption(
    "Find similar past tickets to speed up resolution. "
    "Reinforce good solutions so they rank higher over time."
)

EXAMPLE_TICKETS = {
    "(type your own)": "",
    "503 errors during peak hours": (
        "Customer is reporting intermittent 503 Service Unavailable errors "
        "when their engineering team accesses shared folders between 9-11 AM EST. "
        "They have automation scripts running during this window."
    ),
    "SSO broken after migration": (
        "All users are getting 'SAML Response Invalid' errors after we migrated "
        "our Azure AD to a new tenant. Nobody can log in."
    ),
    "Files showing as 0 bytes": (
        "Files uploaded via our Python integration are showing as 0 bytes in "
        "the web UI, but the API returns success. Affects files over 2GB."
    ),
    "Webhooks not firing for deletes": (
        "Our webhook endpoint receives file.created and file.updated events fine, "
        "but file.deleted events never arrive. We checked our endpoint logs."
    ),
}

selected = st.selectbox("Example incoming tickets", list(EXAMPLE_TICKETS.keys()))
ticket_text = st.text_area(
    "Incoming ticket description",
    value=EXAMPLE_TICKETS[selected],
    height=150,
    placeholder="Describe the customer's issue...",
)

if st.button("Find Similar Resolutions", type="primary") and ticket_text:
    client = get_client()

    with st.spinner("Searching resolved tickets..."):
        ctx = client.recall_memory(
            namespace="resolved-tickets",
            prompt=ticket_text,
            num_chunks=5,
        )

    st.subheader(f"Found {ctx.count} similar tickets")

    for idx, item in enumerate(ctx.items):
        meta = item.metadata
        with st.expander(
            f"{item.key} — {meta.get('category', '?')} | Priority: {meta.get('priority', '?')} | "
            f"Satisfaction: {meta.get('satisfaction_score', '?')}/5"
        ):
            st.markdown(item.content)
            st.caption(
                f"Customer: {meta.get('customer_id', '?')} | "
                f"Resolved: {meta.get('resolved_date', '?')} | "
                f"Time: {meta.get('resolution_time_hours', '?')}h"
            )

            # Reinforcement controls
            st.divider()
            reinforce_count = meta.get("reinforcement_count", 0)
            st.caption(f"Reinforcement count: {reinforce_count}")

            col_up, col_down = st.columns(2)
            with col_up:
                if st.button("Reinforce (this helped)", key=f"reinforce-{idx}"):
                    new_meta = dict(meta)
                    new_meta["reinforcement_count"] = reinforce_count + 1
                    with st.spinner("Reinforcing..."):
                        client.ingest_memory(
                            item=MemoryItem(
                                key=item.key,
                                content=item.content,
                                namespace="resolved-tickets",
                                metadata=new_meta,
                                updated_at=time.time(),
                            )
                        )
                    st.success(
                        f"Reinforced! Count: {reinforce_count + 1}. "
                        "This solution will rank higher in future searches."
                    )
            with col_down:
                if st.button("Not helpful", key=f"downvote-{idx}"):
                    st.info("Negative feedback recorded. This won't affect ranking yet — decay/downranking coming soon.")

    # Generate suggested response
    st.divider()
    st.subheader("Suggested Response")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        st.error("Set OPENAI_API_KEY in .env to enable LLM responses.")
    elif ctx.count > 0:
        with st.spinner("Drafting response based on similar tickets..."):
            llm_resp = client.recall_with_llm(
                prompt=(
                    f"A customer submitted this ticket:\n\n{ticket_text}\n\n"
                    "Based on the similar resolved tickets in context, draft a helpful support response. "
                    "Reference specific resolution steps that worked before."
                ),
                provider="openai",
                model="gpt-4o-mini",
                api_key=openai_key,
                context=ctx.context,
            )
        st.markdown(llm_resp.text)
