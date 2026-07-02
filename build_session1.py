"""Builds session1_rag_foundations_en.ipynb"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s))
code = lambda s: C.append(nbf.v4.new_code_cell(s))

# ---------------------------------------------------------------- title
md("""<div style="background: linear-gradient(120deg,#0f172a,#1e3a5f); border-radius:16px; padding:36px 40px; color:#e2e8f0;">
<h1 style="margin:0; font-size:2.1em; color:#ffffff;">⚡ RAG Foundations</h1>
<h3 style="margin:6px 0 0 0; font-weight:400; color:#93c5fd;">Session 1 of 4 — Why retrieval exists, and where it breaks</h3>
<p style="margin-top:18px; color:#cbd5e1;">NordWind Energy Workshop Series · Retrieval, Vectors & Graphs</p>
</div>""")

# ---------------------------------------------------------------- agenda
md("""## 🗺️ Today's journey

We climb a ladder. Each rung creates the *need* for the next one — by the end, RAG won't feel like a recipe someone handed you. It will feel **inevitable**.

* **🔤 Tokens** — what an LLM actually reads. Live demo: tokenize the same sentence in English and Japanese and compare the counts (spoiler: Japanese pays a token tax).
* **🧠 The context window** — the model's working memory. We measure the entire NordWind corpus in tokens against Claude's window — then scale up to a real company wiki and watch *that* overflow by 200×.
* **📉 Why not just make the window bigger?** — attention cost, and the *lost in the middle* problem. We hide a fact in a long context and watch recall wobble depending on **where** we hid it.
* **🎓 Why not fine-tuning?** — cost, staleness, no citations. A 5-minute honest discussion, no demo needed.
* **🔍 Therefore: retrieval** — we build a complete, naive RAG pipeline from scratch in ~40 lines. Chunk → embed → search → generate. And it *works*.
* **💥 The failure** — we ask our shiny new RAG system one specific question... and it faceplants. Understanding *why* is the door to Sessions 2, 3 and 4.

> **The world we'll live in for all four sessions:** *NordWind Energy* — a fictional power utility with 8 teams, 30 engineers, 15 services, 20 incidents, and 65 internal documents. Everything you build today gets reused, upgraded, and eventually turned into a knowledge graph.""")

# ---------------------------------------------------------------- setup
md("""## 0 · Setup

Two dependencies and one dataset. Run this and stretch while it installs (~1 min on Colab).""")

code("""%pip -q install anthropic sentence-transformers tiktoken matplotlib
print("✅ Dependencies installed")""")

code("""# --- Download the NordWind dataset -------------------------------------
# Replace ORG/REPO once the workshop repo is published.
import json, urllib.request, pathlib

DATA_URL = "https://raw.githubusercontent.com/ORG/nordwind-workshop/main/dataset/documents.jsonl"
LOCAL = pathlib.Path("documents.jsonl")

if not LOCAL.exists():
    try:
        urllib.request.urlretrieve(DATA_URL, LOCAL)
    except Exception:
        print("⚠️ Could not download — upload documents.jsonl manually via the Files panel ⬅️")

docs = [json.loads(line) for line in LOCAL.read_text().splitlines()]
print(f"📚 Loaded {len(docs)} NordWind documents")
from collections import Counter
print(Counter(d['doc_type'] for d in docs))""")

code("""# --- Anthropic API key ---------------------------------------------------
# In Colab: click the 🔑 icon in the left sidebar → add secret ANTHROPIC_API_KEY
import os
try:
    from google.colab import userdata
    os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
    print("🔑 API key loaded from Colab secrets")
except Exception:
    print("⚠️ No Colab secret found — LLM cells will be skipped gracefully")

import anthropic
MODEL = "claude-sonnet-4-6"   # switch to a smaller model to reduce cost
client = anthropic.Anthropic() if os.environ.get("ANTHROPIC_API_KEY") else None

def ask_claude(prompt, system="You are a helpful assistant.", max_tokens=600):
    if client is None:
        return "[LLM skipped — no API key configured]"
    r = client.messages.create(model=MODEL, max_tokens=max_tokens,
                               system=system,
                               messages=[{"role": "user", "content": prompt}])
    return r.content[0].text""")

md("""Let's peek at one document so the corpus feels real before we start measuring it:""")

code("""sample = next(d for d in docs if d['doc_id'] == 'PM-INC-2102')
print(sample['text'][:900])""")

# ---------------------------------------------------------------- rung 1
md("""---
## 1 · 🔤 Tokens — what the model actually reads

LLMs don't read characters or words. They read **tokens** — chunks from a fixed vocabulary learned from training data. Everything about cost, speed, and memory is counted in tokens.

Frequent English words are usually 1 token. Rare words get split. And languages underrepresented in the tokenizer's training data pay a **token tax** — let's see it.""")

code("""import tiktoken
# We use a well-known open tokenizer to demonstrate the concept.
# Every model family (Claude, GPT, Llama...) has its own tokenizer, but the behaviour is universal.
enc = tiktoken.get_encoding("cl100k_base")

pairs = [
    ("English",  "The payment gateway timed out during the evening peak."),
    ("Japanese", "決済ゲートウェイは夜間のピーク時にタイムアウトしました。"),
]
for lang, sentence in pairs:
    toks = enc.encode(sentence)
    print(f"{lang:9s} | {len(sentence):3d} chars → {len(toks):3d} tokens")
    print("          |", [enc.decode([t]) for t in toks][:14], "…\\n")""")

md("""**Discussion point for the room:** the Japanese sentence says the same thing but costs roughly 2× the tokens. For a bilingual organisation, this affects context budgets, latency and cost — it's not academic trivia.

Now the question that drives this entire workshop: *how much can the model read at once?*""")

# ---------------------------------------------------------------- rung 2
md("""---
## 2 · 🧠 The context window — working memory, not knowledge

The **context window** is the maximum number of tokens the model can attend to in a single request — prompt *and* response combined. Think of it as working memory (a desk), not long-term knowledge (the library).

Claude's window is ~**200K tokens**. Sounds enormous. Let's measure our tiny fictional company against it.""")

code("""corpus_tokens = sum(len(enc.encode(d['text'])) for d in docs)
print(f"NordWind corpus: {len(docs)} docs, {corpus_tokens:,} tokens")

CLAUDE_WINDOW = 200_000
REAL_CONFLUENCE = 40_000_000   # a realistic internal wiki for a 150-engineer org

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 3.2))
bars = [("NordWind corpus\\n(65 docs)", corpus_tokens, "#34d399"),
        ("Claude context window", CLAUDE_WINDOW, "#60a5fa"),
        ("A real company wiki", REAL_CONFLUENCE, "#f87171")]
ax.barh([b[0] for b in bars], [b[1] for b in bars], color=[b[2] for b in bars])
ax.set_xscale("log"); ax.set_xlabel("tokens (log scale!)")
for i, (_, v, _) in enumerate(bars):
    ax.text(v, i, f"  {v:,}", va="center")
ax.set_title("Working memory vs. what you actually know")
plt.tight_layout(); plt.show()""")

md("""Read that chart carefully — the axis is **logarithmic**. Our toy corpus fits in the window (barely leaving room to think). A *real* knowledge base is **200× the window**. It does not fit. It will never fit.

So the naive plan — *"just paste everything into the prompt"* — is dead on arrival for real organisations. But wait, windows keep growing... why not just wait for a 40M-token window?""")

# ---------------------------------------------------------------- rung 3
md("""---
## 3 · 📉 Why "just make it bigger" doesn't save you

Two hard problems:

1. **Cost & latency scale with context.** Attention over N tokens costs O(N²) in the worst case — and you pay for every input token on *every single request*. Shipping 40M tokens to answer "when is the invoice due?" is like mailing the whole library to someone who asked for one quote.
2. **Lost in the middle.** Even when content fits, models recall information near the **start** and **end** of the context better than information buried in the **middle**. Retrieval quality degrades exactly where you can't see it.

Let's test #2 live on our own corpus: we hide one specific fact inside a big blob of NordWind documents — at the start, middle, and end — and ask Claude to find it.""")

code("""# --- Needle in a haystack ------------------------------------------------
NEEDLE = ("INTERNAL MEMO: The NordWind disaster-recovery passphrase rotation "
          "is scheduled for the 14th of every month at 03:00 UTC.")
QUESTION = "When is the disaster-recovery passphrase rotation scheduled?"

haystack = "\\n\\n".join(d['text'] for d in docs if d['doc_type'] in ('runbook','overview','adr'))
print(f"Haystack size: {len(enc.encode(haystack)):,} tokens")

def hide_needle(position):
    if position == "start":  return NEEDLE + "\\n\\n" + haystack
    if position == "end":    return haystack + "\\n\\n" + NEEDLE
    half = len(haystack) // 2
    return haystack[:half] + "\\n\\n" + NEEDLE + "\\n\\n" + haystack[half:]

for pos in ["start", "middle", "end"]:
    context = hide_needle(pos)
    answer = ask_claude(
        f"Answer strictly from the documents below.\\n\\n<documents>\\n{context}\\n</documents>\\n\\nQuestion: {QUESTION}",
        max_tokens=100)
    print(f"[needle at {pos:6s}] → {answer.strip()[:140]}")""")

md("""> 🎤 **Facilitator note:** modern models often *pass* this small test — that's fine, and say so honestly. The documented effect grows with context length and distractor density; the demo's job is to plant the intuition that **position and noise matter**, and that stuffing is a strategy you can't monitor. If it wobbles live: even better.

So: everything doesn't fit, and even when it fits, recall isn't uniform. What about baking knowledge into the weights instead?""")

# ---------------------------------------------------------------- rung 4
md("""---
## 4 · 🎓 Why not fine-tuning?

Fine-tuning changes the model's **weights**. It's the right tool for changing *behaviour* — tone, format, domain style. It's the wrong tool for injecting *facts*:

| | Fine-tuning | Retrieval |
|---|---|---|
| New document arrives | Retrain (hours, $$) | Index it (seconds) |
| "Where did that answer come from?" | 🤷 no provenance | Cites the exact chunk |
| Delete/correct a fact | Nearly impossible | Delete/update the chunk |
| Access control per user | No | Filter at query time |
| Hallucination on missing knowledge | Confidently wrong | Can say "not found" |

For **knowledge**, we want it *outside* the model, in a store we control — fetched at question time.

That word — *fetched* — is the whole idea. Welcome to **Retrieval-Augmented Generation**.""")

# ---------------------------------------------------------------- rung 5
md("""---
## 5 · 🔍 Building naive RAG from scratch

The pipeline, which we will refine for three more sessions:

```
 ingest → chunk → embed → index → RETRIEVE → augment prompt → generate
```

Today we build the simplest honest version:
- **Chunk**: split each document into overlapping windows
- **Embed**: turn each chunk into a vector with a local model (no API needed)
- **Index**: a plain numpy matrix 😄 (Session 2 explains why this breaks at scale)
- **Retrieve**: cosine similarity, top-k
- **Generate**: Claude answers *using only the retrieved chunks*""")

code("""# --- Chunking ------------------------------------------------------------
def chunk_text(text, size=800, overlap=150):
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return chunks

chunks, meta = [], []
for d in docs:
    for j, ch in enumerate(chunk_text(d['text'])):
        chunks.append(ch)
        meta.append({"doc_id": d['doc_id'], "title": d['title'], "chunk": j})

print(f"{len(docs)} documents → {len(chunks)} chunks")""")

code("""# --- Embedding (local, free, no API key) ----------------------------------
from sentence_transformers import SentenceTransformer
import numpy as np

embedder = SentenceTransformer("all-MiniLM-L6-v2")   # 384 dimensions, ~90MB
E = embedder.encode(chunks, normalize_embeddings=True, show_progress_bar=True)
print("Embedding matrix:", E.shape)  # (n_chunks, 384)""")

code("""# --- Retrieval: cosine similarity = dot product on normalized vectors -----
def retrieve(query, k=4):
    q = embedder.encode([query], normalize_embeddings=True)
    scores = (E @ q.T).ravel()
    top = np.argsort(-scores)[:k]
    return [(scores[i], meta[i], chunks[i]) for i in top]

for score, m, ch in retrieve("Why did payments time out in the evening?"):
    print(f"{score:.3f}  {m['doc_id']:12s} {m['title'][:60]}")""")

md("""👀 Look at those hits — the retriever found the INC-2102 postmortem and the payment-gateway runbook from a *paraphrased* question that shares almost no keywords with the documents. That's semantic search. Now wire it into generation:""")

code("""# --- The full RAG loop -----------------------------------------------------
def rag_answer(question, k=4, show_sources=True):
    hits = retrieve(question, k)
    context = "\\n\\n---\\n\\n".join(
        f"[Source: {m['doc_id']} — {m['title']}]\\n{ch}" for _, m, ch in hits)
    answer = ask_claude(
        f"Answer using ONLY the sources below. Cite source ids. "
        f"If the sources are insufficient, say so.\\n\\n{context}\\n\\nQuestion: {question}")
    if show_sources:
        print("Retrieved:", ", ".join(m['doc_id'] for _, m, _ in hits), "\\n")
    return answer

print(rag_answer("What was the root cause of the payment gateway timeouts, and what actions were taken?"))""")

md("""✅ **That's a working RAG system in ~40 lines.** It retrieves the right postmortem, answers grounded in it, and cites its source. For single-fact questions over unstructured text, this pattern is genuinely production-shaped (Session 2 adds the engineering that makes it robust).

Time to break it. 😈""")

# ---------------------------------------------------------------- rung 6
md("""---
## 6 · 💥 The question that breaks everything

Some questions aren't about *finding a passage*. They're about **connecting facts across documents**. Try this one — read it slowly, because answering it requires:

1. knowing which services **depend on** `payment-gateway` (that fact lives in an ADR and a service-catalog page)
2. finding all incidents that **affected those services** (scattered across 20 postmortems)
3. **aggregating** every responder from those postmortems into one list

No single chunk contains the answer. The answer *is a join*.""")

code("""HARD_QUESTION = ("Which engineers have responded to incidents affecting services "
                 "that depend on payment-gateway? List all of them.")

print(rag_answer(HARD_QUESTION, k=6))""")

code("""# --- Ground truth reveal ----------------------------------------------------
GROUND_TRUTH = ['Bulma', 'Kakashi Hatake', 'Light Yagami', 'Mikasa Ackerman',
                'Misato Katsuragi', 'Nico Robin', 'Olivier Armstrong', 'Roronoa Zoro',
                'Shinji Ikari', 'Winry Rockbell']
print(f"The complete correct answer is {len(GROUND_TRUTH)} engineers "
      f"across 6 incidents and 6 different teams:\\n")
for name in GROUND_TRUTH:
    print("  •", name)""")

md("""Compare Claude's answer to the ground truth. Typically the RAG answer is **partial** (it found 2–3 postmortems and listed their responders), **unaware of what it's missing**, and — worst of all — **confident**.

This is not a prompt problem. It's not a model problem. Retrieval by *similarity* fetched chunks that *sound like* the question. But the question needed chunks *related by structure*: dependency edges, incident links, membership. **Semantic similarity is not relationship traversal.**

Write that sentence down. It's the thesis of this entire workshop.""")

# ---------------------------------------------------------------- outro
md("""---
## 🏁 What you learned today

- LLMs read **tokens**; context windows are **working memory**, not knowledge
- Stuffing doesn't scale (cost, and *lost in the middle*), fine-tuning doesn't inject facts
- **RAG** = fetch the right things at question time — and you built one from scratch
- Naive RAG shines on *lookup* questions and fails on *relationship* questions

## 📝 Before next session
The practice notebook has 5 exercises on this pipeline — including making the chunker smarter and finding **another** question that breaks naive RAG (there are several hiding in NordWind...).

---

<div style="background: linear-gradient(120deg,#1e1b4b,#312e81); border-radius:16px; padding:30px 36px; color:#e2e8f0;">
<h2 style="margin:0; color:#ffffff;">⏭️ To be continued...</h2>
<p style="font-size:1.05em; margin-top:14px;">Our retriever compared the question against <b>every one of our chunks</b>, one by one. Fine for 500 chunks. Your production corpus has <b>5 million</b>.</p>
<p style="font-size:1.05em;">Next session: what an embedding <i>really</i> is (we will <b>see</b> semantic space with our own eyes), how vector databases search millions of vectors in milliseconds without comparing against all of them, and the engineering — hybrid search, filtering, reranking — that separates a demo from a product.</p>
<h3 style="color:#93c5fd; margin-bottom:0;">Session 2: Embeddings & Vector Databases — <i>the geometry of meaning</i> 🌌</h3>
</div>""")

nb["cells"] = C
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}, "colab": {"provenance": []}}
nbf.write(nb, "/home/claude/nordwind/session1_rag_foundations_en.ipynb")
print("cells:", len(C))
