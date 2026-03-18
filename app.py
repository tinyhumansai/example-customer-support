"""Streamlit entrypoint — Robylon.ai Customer Support POC."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Robylon.ai x Neocortex — Customer Support",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Robylon.ai x Neocortex")
st.sidebar.caption(
    "Customer support POC powered by [Neocortex Memory SDK](https://github.com/tinyhumansai). "
    "Each page demonstrates a real use case for AI-powered support."
)
st.sidebar.divider()
st.sidebar.markdown(
    """
**Use Cases**
1. Seed Data — load sample data
2. Community Knowledge — search crowd-sourced fixes
3. Ticket Resolution — find & reinforce past solutions
4. KB Evolution — deprecate/reinforce articles
5. Customer Context — personalized support chat
"""
)

st.title("Robylon.ai x Neocortex — Customer Support POC")
st.markdown(
    """
Welcome! This app demonstrates how **Neocortex Memory SDK** solves core challenges
in high-volume customer support:

| Challenge | Solution |
|---|---|
| Community knowledge scattered across forums/Discord | **Instant semantic search** over ingested posts |
| Repeating past ticket investigations | **Similar ticket recall** with reinforcement |
| Outdated KB articles causing wrong answers | **Knowledge evolution** — deprecate stale, reinforce current |
| No memory of past customer interactions | **Per-customer context** for personalized support |

### Getting Started

1. Navigate to **Seed Data** in the sidebar to load sample data.
2. Explore each use-case page to see the SDK in action.

---

*Built for the Robylon.ai pitch — demonstrating Neocortex Memory SDK capabilities.*
"""
)
