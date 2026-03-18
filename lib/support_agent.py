"""Multi-namespace recall and LLM response generation for support agent."""

import os
from dataclasses import dataclass, field

from tinyhumansai import TinyHumanMemoryClient, GetContextResponse, LLMQueryResponse


SYSTEM_PROMPT = """You are a senior support agent for CloudSync Pro, a cloud file sync and storage platform.

Guidelines:
- Be helpful, concise, and technically accurate.
- Reference specific settings paths (e.g., Admin > Storage > Dedup) when applicable.
- If the context includes past interactions with the customer, personalize your response.
- If you find conflicting information (e.g., deprecated vs current docs), prefer the current version.
- If you're not sure, say so — don't guess.
- Format your response with clear steps when providing instructions."""


@dataclass
class SupportResponse:
    """Response from the support agent with context sources."""

    answer: str
    community_context: GetContextResponse | None = None
    ticket_context: GetContextResponse | None = None
    kb_context: GetContextResponse | None = None
    customer_context: GetContextResponse | None = None


def _recall_safe(
    client: TinyHumanMemoryClient, namespace: str, prompt: str, num_chunks: int = 5
) -> GetContextResponse | None:
    """Recall memory, returning None on error instead of raising."""
    try:
        return client.recall_memory(namespace=namespace, prompt=prompt, num_chunks=num_chunks)
    except Exception:
        return None


def generate_support_response(
    client: TinyHumanMemoryClient,
    query: str,
    customer_id: str | None = None,
) -> SupportResponse:
    """Recall from all relevant namespaces and generate a support response via LLM."""

    community_ctx = _recall_safe(client, "community-solutions", query, 3)
    ticket_ctx = _recall_safe(client, "resolved-tickets", query, 3)
    kb_ctx = _recall_safe(client, "knowledge-base", query, 3)

    customer_ctx = None
    if customer_id:
        customer_ctx = _recall_safe(client, f"customer:{customer_id}", query, 5)

    # Build combined context
    parts = [SYSTEM_PROMPT, ""]
    if kb_ctx and kb_ctx.context:
        parts.append("=== KNOWLEDGE BASE ===")
        parts.append(kb_ctx.context)
        parts.append("")
    if ticket_ctx and ticket_ctx.context:
        parts.append("=== SIMILAR RESOLVED TICKETS ===")
        parts.append(ticket_ctx.context)
        parts.append("")
    if community_ctx and community_ctx.context:
        parts.append("=== COMMUNITY SOLUTIONS ===")
        parts.append(community_ctx.context)
        parts.append("")
    if customer_ctx and customer_ctx.context:
        parts.append("=== CUSTOMER HISTORY ===")
        parts.append(customer_ctx.context)
        parts.append("")

    combined_context = "\n".join(parts)

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        return SupportResponse(
            answer="Error: OPENAI_API_KEY not set. Add it to your .env file.",
            community_context=community_ctx,
            ticket_context=ticket_ctx,
            kb_context=kb_ctx,
            customer_context=customer_ctx,
        )

    llm_resp = client.recall_with_llm(
        prompt=query,
        provider="openai",
        model="gpt-4o-mini",
        api_key=openai_key,
        context=combined_context,
    )

    return SupportResponse(
        answer=llm_resp.text,
        community_context=community_ctx,
        ticket_context=ticket_ctx,
        kb_context=kb_ctx,
        customer_context=customer_ctx,
    )
