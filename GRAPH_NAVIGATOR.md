# 🛰️ The NordWind Graph Navigator — how it works, how it was built, how it was tested

**Live URL:** https://raw.githack.com/noctetemp/nordwind-workshop/main/nordwind_3d.html
**Source:** `nordwind_3d.html` in this repository (one file, ~19 KB)

---

## 1. What it is

A single HTML page that connects **directly from the browser to a Neo4j database** and lets you
navigate the graph in 3D, styled like a starship's tactical display. It contains **no data**.
Every node and relationship you see was returned by a Cypher query moments earlier — the page is a
sci-fi frontend for the database, nothing more.

Its job in the workshop: after participants load NordWind into their own Neo4j Aura instance
(Session 3, section 3), the Navigator makes the abstract idea of "traversing a graph" *physical* —
you click a node, the database is asked for its neighbors, and they materialize in space.

---

## 2. Architecture

```
┌──────────────────────────────┐        bolt+s:// (TLS websocket, port 7687)
│  nordwind_3d.html            │ ─────────────────────────────────────────▶ ┌─────────────────────┐
│  (runs in the browser)       │                                            │ Neo4j Aura Free     │
│                              │ ◀───────── records: nodes / rels / paths ──│ (your own instance) │
│  • neo4j-driver (browser)    │                                            │ loaded by Session 3 │
│  • 3d-force-graph + three.js │                                            │ notebook            │
│  • bloom, starfield, HUD     │                                            └─────────────────────┘
│                              │
│  fallback only: ─────────────│──── https GET ───▶ raw.githubusercontent.com/.../dataset/*.json
└──────────────────────────────┘                    (SNAPSHOT MODE — static copy, no DB)
```

**There is no server of ours anywhere.** GitHub hosts the HTML file (and the JSON fallback),
CDNs serve the JavaScript libraries, and the database is whichever Neo4j the user points the page at.

### The libraries and how they load

| Library | Role | How it's loaded |
|---|---|---|
| `neo4j-driver` 5.28 (browser build) | Talks bolt to Neo4j from the browser | plain `<script>` tag from unpkg → global `neo4j` |
| `3d-force-graph` 1.77 | Force-directed 3D layout, camera, picking, edge particles | ES module via esm.sh with `?external=three` |
| `three` 0.180 | WebGL rendering (used by the graph lib and by us for stars/lights) | ES module via importmap → esm.sh |
| `UnrealBloomPass` (three addon) | The hologram glow | ES module, same three instance |

The importmap is the load-bearing trick: it maps `three`, `three/webgpu`, `three/tsl`,
`three/addons/` and `three/examples/jsm/` to one pinned esm.sh version, so the graph library,
the bloom pass and our own code all share **one** three.js instance. See section 7 for why every
one of those five entries exists.

---

## 3. How each feature works

### 🔌 Uplink
`neo4j.driver(uri, neo4j.auth.basic('neo4j', password))` → `driver.verifyConnectivity()` →
open a session. The URI is the `neo4j+s://…databases.neo4j.io` from your Aura credentials file.
On success the panel disappears, the Cypher console is enabled, and one **seed query** runs:

```cypher
MATCH (s:Service {name:'payment-gateway'}) RETURN s
```

If it returns nothing, the log tells you the database is empty — load it via the notebook first.

### 🖱 Click a node → expand from the database
Each node carries the `elementId` Neo4j gave it. Clicking runs:

```cypher
MATCH (n) WHERE elementId(n) = $id
MATCH (n)-[r]-(m)
RETURN n, r, m
```

Whatever comes back is merged into the scene. Nodes already present keep their position (same
JavaScript objects are reused), so the neighborhood *grows around* the clicked node rather than
re-laying-out everything. The camera also flies to the node.

### 📥 Ingest — turning driver records into a scene
`ingest(records)` walks every value in every record and handles three shapes:
- a **Node** (`labels` + `elementId` + `properties`) → sphere, colored by first label, sized by type
- a **Relationship** (`type`, `startNodeElementId`, `endNodeElementId`) → link
- a **Path** (`segments[]`) → all of its nodes and relationships
- arrays of any of the above (e.g. `collect(...)`)

It runs **two passes** — nodes first, then relationships — so a relationship never arrives before
its endpoints exist. Everything is deduplicated by `elementId`, so re-running a query is harmless.

### ⌨️ Cypher console
Type any query, press Enter. The result is ingested into the scene and the log prints
`↳ N records · +x nodes +y rels · NN ms`. Scalar results (counts, names) are printed inline.
↑/↓ recall history. Queries that return a path variable `p` are auto-highlighted (gold).

### ⚡ TRACE IMPACT
Runs the workshop's hard question **as a real path query against the database**:

```cypher
MATCH p = (e:Engineer)-[:RESPONDED_TO]->(i:Incident)
          -[:AFFECTED]->(d:Service)-[:DEPENDS_ON]->(:Service {name:'payment-gateway'})
RETURN p
```

Every node and relationship on a returned path goes into a highlight set; everything else is
dimmed to dark slate. Result: 17 paths → 18 lit nodes, 24 gold edges, the 10 correct engineers.
`◌ CLEAR TRACE` restores normal view.

### 📼 Snapshot mode (no database)
Loads the five static JSON files from the repo and builds the same scene locally. TRACE still
works in this mode, computed in-memory with the same 3-hop set logic. The Cypher console is
disabled (nothing to query). Status line makes the mode unmistakable so nobody confuses it with
live navigation.

### Other controls
`⬇ LOAD ALL` (`MATCH (n) OPTIONAL MATCH (n)-[r]->() RETURN n, r`), `⟲ RESET` (clear scene,
re-seed), `◉ ORBIT` (cinematic auto-rotation).

---

## 4. Suggested Session 3 choreography

1. Participants run the notebook's load cell → their Aura now holds 73 nodes / 153 rels.
2. Projector: open the Navigator, **UPLINK** with your own instance. One green node in the void.
3. **Click payment-gateway.** "Every sphere appearing right now is a Cypher result — look at the
   milliseconds in the log." Click billing-engine. Click an incident. Two or three hops out.
4. Take a request from the room: *"show Levi Ackerman"* →
   `MATCH (e:Engineer {name:'Levi Ackerman'})-[r]-(m) RETURN e,r,m` in the console.
5. Type the hard-question query live (or press **⚡ TRACE**) → the golden web.
   Same answer they just got in Colab, now as light.
6. **The RAG autopsy** (Session 3, section 5b): with TRACE lit, paste
   `MATCH (i:Incident) WHERE i.id IN ['INC-2117','INC-2107','INC-2113'] MATCH (i)-[r]-(m) RETURN i, r, m`
   — Session 1's wrong answers appear touching the hub but on no golden path.
7. Close with `⟲ RESET` → one node again. "Everything you saw was pulled on demand.
   The graph database is what made that instant."

Keep the Aura console's **Query** tab open in another window as a second proof point.

---

## 5. Security notes — read before projecting

- Credentials are typed into a browser page and held **in memory only** — nothing is stored,
  nothing leaves the browser except the bolt connection to your database.
- Use it **only with your own throwaway workshop instance**. Never paste production credentials
  into any single-file HTML page, this one included.
- Don't share a page with credentials pre-filled. Each person connects to their own Aura.
- Aura Free auto-pauses after ~3 days idle; resume it the morning of the session.
- Corporate networks sometimes block port 7687; a phone hotspot is the fallback.

---

## 6. How it was validated — and what was *not*

Being precise here matters more than sounding confident.

### What was tested, and how
**A. The database logic — against a real Neo4j, but a local one.**
No cloud account was created (Claude cannot create accounts or enter credentials, and none were
needed). Instead, **Neo4j Community Edition 5.26 was installed from the official tarball inside
Claude's sandbox environment**, started locally on `bolt://localhost:7687`, and loaded with the
NordWind dataset using the *same* `UNWIND`/`MERGE` statements the Session 3 notebook uses.
Then the page's **exact JavaScript** (the `ingest` function and every Cypher string, copied
verbatim) was executed in Node.js through the official `neo4j-driver`. Results:

| Operation | Query | Result |
|---|---|---|
| Seed | `MATCH (s:Service {name:'payment-gateway'}) RETURN s` | 1 node |
| Click-expand | `MATCH (n) WHERE elementId(n)=$id MATCH (n)-[r]-(m) RETURN n,r,m` | 7 nodes, 6 rels |
| TRACE | the 4-hop path query | 17 paths → 18 nodes, 24 rels, exactly the 10 correct engineers |
| LOAD ALL | `MATCH (n) OPTIONAL MATCH (n)-[r]->() RETURN n,r` | 73 nodes, 153 rels |
| RAG autopsy | `EXISTS { … DEPENDS_ON → payment-gateway }` for INC-2117/2107/2113 | all three `false` |

This proves the Cypher is correct and the record-parsing handles nodes, relationships and paths
the way the real driver emits them. Aura runs Neo4j 5.x, so Cypher semantics and `elementId()`
behave identically. (Every query in the Session 3 notebook was verified the same way.)

**B. The page itself — in a real Chrome, via browser automation, on the deployed URL.**
Loaded from GitHub through a CDN exactly as participants will: HUD renders, no console errors,
SNAPSHOT MODE fetches the JSON and renders 73/153, offline TRACE lights 10 engineers · 6 incidents,
bloom/starfield/particles/orbit all work.

### What was NOT tested (needs a real Aura instance and your credentials)
- The **actual bolt+s connection from a browser to Aura** — TLS websocket handshake, Aura's
  network path, the browser driver bundle talking to a cloud instance rather than Node talking
  to localhost. This is the one integration seam that remains unverified by execution.
- Latency/feel of click-expand over the internet (localhost is unrealistically fast).

Why it is nevertheless very likely to work: the browser bundle is Neo4j's official build for
exactly this use; `neo4j+s://` URIs are its documented Aura path; bolt protocol 5.x is supported
by both ends. Remaining realistic failure modes are environmental — a paused instance, a mistyped
URI, port 7687 blocked by a firewall — all of which surface as a readable error in the uplink
panel rather than a blank screen.

**Action for the facilitator:** the first UPLINK with real Aura credentials is the final
acceptance test. It takes 30 seconds.

---

## 7. Engineering notes — the module-resolution saga

The first version showed a black canvas. Five distinct problems were found by loading the deployed
page in Chrome and reading the console after each fix. Recorded here because anyone building a
single-file three.js page will hit the same ones:

| # | Console error | Cause | Fix |
|---|---|---|---|
| 1 | `Failed to resolve "three/webgpu"` | graph lib imports three subpaths; importmap only mapped `three` | map `three/webgpu`, `three/tsl` |
| 2 | `Failed to resolve "three-forcegraph"` | unpkg's `.mjs` is not self-contained; its deps are bare imports | let esm.sh resolve the whole tree (`?external=three`) |
| 3 | `Failed to resolve "three/examples/jsm/…DragControls"` | `external=three` also externalizes deep paths | prefix-map `three/examples/jsm/` and `three/addons/` |
| 4 | fix "didn't work" | githack's CDN served the stale file for minutes | test with **commit-SHA-pinned** URLs, never `main` |
| 5 | `'three' does not provide an export named 'Timer'` | three 0.169 predates `Timer` in core; render lib needs it | pin **three 0.180** |

Two aesthetic passes followed: bloom 1.6→1.05 (supernova → hologram), an ambient light so spheres
have no dark side, and OWNS wiring dimmed so TRACE gold stays unique.

**Process lesson:** the difference between the broken and working versions wasn't cleverness, it
was closing the loop — deploy, observe in a real browser, read the error, fix, redeploy.
Same lesson the workshop teaches about retrieval.

---

## 8. Possible upgrades

- Floating text labels next to major nodes (three.js sprites)
- Show relationship type on hover / a label toggle
- Write operations from the console (`CREATE`) → watch nodes appear live during the session
- Participant mode: a URL parameter that pre-selects a seed node, so each person starts from
  "their" engineer
