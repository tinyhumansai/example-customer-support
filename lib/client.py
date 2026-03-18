"""Cached Neocortex Memory SDK client for Streamlit."""

import os

import streamlit as st
from tinyhumansai import TinyHumanMemoryClient


@st.cache_resource
def get_client() -> TinyHumanMemoryClient:
    """Return a singleton TinyHumanMemoryClient, cached across Streamlit reruns."""
    token = os.environ.get("TINYHUMANS_TOKEN", "")
    model_id = os.environ.get("TINYHUMANS_MODEL_ID", "")
    if not token:
        st.error("Missing TINYHUMANS_TOKEN — add it to your .env file.")
        st.stop()
    if not model_id:
        st.error("Missing TINYHUMANS_MODEL_ID — add it to your .env file.")
        st.stop()
    return TinyHumanMemoryClient(token=token, model_id=model_id)
