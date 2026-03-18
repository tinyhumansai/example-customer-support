# Robylon.ai x Neocortex — Customer Support POC

AI-powered customer support demo using the **Neocortex Memory SDK** (`tinyhumansai`). Built for the Robylon.ai pitch to demonstrate how memory-backed AI agents handle real support scenarios for a fictional SaaS product, **CloudSync Pro**.

## Use Cases

| # | Page | What it shows |
|---|---|---|
| 1 | **Seed Data** | Load/clear sample data into Neocortex namespaces |
| 2 | **Community Knowledge** | Semantic search over forum/Discord solutions — no curation needed |
| 3 | **Ticket Resolution** | Find similar past tickets + reinforce good solutions (re-ingest with fresh timestamp) |
| 4 | **KB Evolution** | Deprecate outdated articles, reinforce current ones, add new content |
| 5 | **Customer Context** | Personalized chat — agent recalls past interactions, plan details, preferences |

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                    │
│  (Seed Data | Community | Tickets | KB | Chat)  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │  support_agent.py │  ← multi-namespace recall + LLM
        └─────────┬─────────┘
                  │
    ┌─────────────┴─────────────┐
    │  Neocortex Memory SDK     │
    │  (tinyhumansai)           │
    │                           │
    │  Namespaces:              │
    │  ├─ community-solutions   │
    │  ├─ resolved-tickets      │
    │  ├─ knowledge-base        │
    │  └─ customer:{id}         │
    └─────────────┬─────────────┘
                  │
          ┌───────┴───────┐
          │  OpenAI API   │  ← response generation via recall_with_llm
          └───────────────┘
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/tinyhumansai/example-customer-support.git
cd example-customer-support

# 2. Install dependencies
pip install tinyhumansai streamlit python-dotenv

# 3. Configure API keys
cp .env.example .env
```

Open `.env` and fill in your keys:

| Variable | Where to get it |
|---|---|
| `TINYHUMANS_TOKEN` | [app.tinyhumans.ai](https://app.tinyhumans.ai) → Settings → API Keys → Generate |
| `TINYHUMANS_MODEL_ID` | Same page — copy the Model ID for your project |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

> **Note**: `OPENAI_API_KEY` is only needed for pages that generate LLM responses (pages 2–5). Seeding data (page 1) works without it.

```bash
# 4. Run
streamlit run app.py
```

Then:
1. Go to **Seed Data** page and click **Seed All Data**
2. Explore each use-case page

## Key Concepts

### Reinforcement = Re-ingestion
The SDK upserts on `(namespace, key)`. Re-ingesting an item with a fresh `updated_at` timestamp naturally reinforces it — the item becomes more prominent in recall results.

### Decay = Deletion
`delete_memory` removes outdated content. In production, Robylon could automate this based on article age, negative feedback count, or content freshness scores.

### Namespace Isolation
Each use case has its own namespace. Customer data is further isolated per customer (`customer:acme-corp`). The support agent can recall across all namespaces simultaneously for comprehensive answers.

## Sample Data

All in `data/`:
- `community_posts.json` — 15 forum/Discord solutions (sync, API, SSO, mobile, etc.)
- `resolved_tickets.json` — 10 historical tickets with full issue→diagnosis→resolution
- `kb_articles.json` — 8 KB articles including deprecated v1 and current v2 versions
- `customers.json` — 3 customers (Acme Corp, TechStart Inc, Global Media) with interaction histories

## Next Steps

- **LangChain/LangGraph integration** — the SDK supports `TinyHumanStore` for LangChain vector store compatibility
- **Automated decay** — scheduled jobs to deprecate low-performing content
- **Feedback loop** — track resolution success rates to auto-reinforce effective solutions
- **Multi-language support** — the SDK handles embedding-based recall, so multilingual content works out of the box
