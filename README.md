# ⚡ NordWind Energy — RAG, Vectors & Graphs Workshop

A 4-session hands-on workshop for developers: Retrieval-Augmented Generation,
embeddings & vector databases, graph databases (Neo4j), and GraphRAG — all built
on one coherent fictional company, **NordWind Energy** (staffed, for reasons of
morale, entirely by anime characters).

## Sessions (90 minutes each)

| # | Session | Notebook |
|---|---------|----------|
| 1 | **RAG Foundations** — tokens, context windows, naive RAG, and the question that breaks it | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session1_rag_foundations_en.ipynb) |
| 2 | **Embeddings & Vector Databases** — the geometry of meaning | _coming soon_ |
| 3 | **Graph Databases** — Cypher, Neo4j, and seeing your knowledge as a network | _coming soon_ |
| 4 | **GraphRAG** — vectors + graphs, full circle | _coming soon_ |

## Setup for participants

1. Open the session notebook via its Colab badge above.
2. In Colab, click the 🔑 **Secrets** icon (left sidebar) and add a secret named
   `ANTHROPIC_API_KEY` with the key provided by the facilitator. Enable notebook access.
3. Runtime → Run all. The dataset downloads automatically from this repo.

## The NordWind world

- 8 teams · 30 engineers · 15 services · 20 incidents · 65 documents
  (postmortems, ADRs, runbooks, Slack threads, onboarding docs)
- `dataset/ground_truth.json` holds canonical answers to the workshop's key questions
  (spoilers — don't read before Session 1! 😄)

*NordWind Energy is fictional. Character names are affectionate references used
as internal easter eggs.*
