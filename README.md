# ⚡ NordWind Energy — RAG, Vectors & Graphs Workshop

A 4-session hands-on workshop for developers: Retrieval-Augmented Generation,
embeddings & vector databases, graph databases (Neo4j), and GraphRAG — all built
on one coherent fictional company, **NordWind Energy** (staffed, for reasons of
morale, entirely by anime characters).

## Sessions (90 minutes each)

| # | Session | Notebook |
|---|---------|----------|
| 1 | **RAG Foundations** — tokens, context windows, naive RAG, and the question that breaks it | [![EN](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session1_rag_foundations_en.ipynb) [🇯🇵 日本語版](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session1_rag_foundations_ja.ipynb) |
| 2 | **Embeddings & Vector Databases** — the geometry of meaning | [![EN](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session2_vectors_en.ipynb) [🇯🇵 日本語版](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session2_vectors_ja.ipynb) |
| 3 | **Graph Databases** — Cypher, Neo4j, the Graph Navigator, and the RAG autopsy · **[⚠️ Aura setup first](AURA_SETUP.md)** | [![EN](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session3_graphs_en.ipynb) [🇯🇵 日本語版](https://colab.research.google.com/github/noctetemp/nordwind-workshop/blob/main/session3_graphs_ja.ipynb) |
| 4 | **GraphRAG** — vectors + graphs, full circle | _coming soon_ |

## 🛰️ The Graph Navigator — sci-fi navigation of a LIVE Neo4j

**[Open the Navigator](https://raw.githack.com/noctetemp/nordwind-workshop/main/nordwind_3d.html)**
(or download [`nordwind_3d.html`](nordwind_3d.html) and double-click it).

Establish an **uplink to your own Neo4j Aura instance** (the one you load in Session 3)
and navigate the graph like a ship's computer:

- **Click any node** → its neighborhood is fetched live from the database and materializes in 3D
- **Cypher console** → type any query, watch its results appear, with record counts and ms timing
- **⚡ TRACE IMPACT** → runs the workshop's hard question as a real path query and lights every
  evidence path in gold
- No database handy? **SNAPSHOT MODE** loads a static copy so the visuals still work.

How it works and how it was tested: [`GRAPH_NAVIGATOR.md`](GRAPH_NAVIGATOR.md).

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
