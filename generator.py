"""
NordWind Energy — Synthetic World Generator
============================================
Generates a coherent fictional energy company used across all 4 workshop sessions:
  - Entities: teams, engineers, services, incidents
  - Relationships: MEMBER_OF, OWNS, DEPENDS_ON, RESPONDED_TO, AFFECTED, AUTHORED
  - Documents (~70): postmortems, ADRs, runbooks, onboarding docs, slack threads
  - Ground truth: canonical answers to the workshop's key questions
Fully deterministic (seeded) so the dataset can be regenerated identically.
"""

import json
import random
import hashlib
from pathlib import Path
from datetime import date, timedelta

random.seed(42)

OUT = Path(__file__).parent / "dataset"
DOCS = OUT / "documents"
ENTS = OUT / "entities"
for p in (OUT, DOCS, ENTS):
    p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. THE WORLD — teams, engineers, services
# ---------------------------------------------------------------------------

TEAMS = [
    {"id": "T1", "name": "Grid Operations",      "focus": "real-time grid telemetry and control"},
    {"id": "T2", "name": "Customer Platform",    "focus": "customer-facing web and mobile experiences"},
    {"id": "T3", "name": "Payments & Billing",   "focus": "payment processing, invoicing, tariffs"},
    {"id": "T4", "name": "Data Platform",        "focus": "data lake, pipelines, analytics"},
    {"id": "T5", "name": "Core Infrastructure",  "focus": "Kubernetes, networking, observability"},
    {"id": "T6", "name": "Forecasting & AI",     "focus": "demand forecasting and ML services"},
    {"id": "T7", "name": "Field Systems",        "focus": "smart meters and field-device integration"},
    {"id": "T8", "name": "Security & Identity",  "focus": "authentication, authorization, compliance"},
]

ENGINEERS = [
    # (name, team, role)
    ("Motoko Kusanagi",      "T1", "Staff Engineer"),
    ("Spike Spiegel",         "T1", "Senior Engineer"),
    ("Edward Elric",        "T1", "Engineer"),
    ("Levi Ackerman",        "T1", "SRE"),
    ("Nami",      "T2", "Tech Lead"),
    ("Usopp",        "T2", "Senior Engineer"),
    ("Asuka Langley",      "T2", "Frontend Engineer"),
    ("Tanjiro Kamado",       "T2", "Engineer"),
    ("Nico Robin",       "T3", "Tech Lead"),
    ("Light Yagami",     "T3", "Senior Engineer"),
    ("Mikasa Ackerman",      "T3", "Engineer"),
    ("Roronoa Zoro",        "T3", "Payments Specialist"),
    ("Olivier Armstrong",      "T4", "Staff Engineer"),
    ("L Lawliet",       "T4", "Data Engineer"),
    ("Bulma",     "T4", "Senior Engineer"),
    ("Shikamaru Nara",     "T4", "Engineer"),
    ("Misato Katsuragi",       "T5", "Principal SRE"),
    ("Kakashi Hatake",      "T5", "SRE"),
    ("Franky",        "T5", "Platform Engineer"),
    ("Yor Forger",       "T5", "Network Engineer"),
    ("Senku Ishigami",   "T6", "ML Engineer"),
    ("Frieren",           "T6", "Senior ML Engineer"),
    ("Kurisu Makise",        "T6", "Data Scientist"),
    ("Winry Rockbell",        "T7", "Tech Lead"),
    ("Shinji Ikari",    "T7", "Embedded Engineer"),
    ("Loid Forger",     "T7", "Engineer"),
    ("Erza Scarlet",       "T8", "Security Lead"),
    ("Killua Zoldyck",        "T8", "Security Engineer"),
    ("Hinata Hyuga",        "T8", "IAM Engineer"),
    ("Lelouch Lamperouge",     "T8", "Compliance Engineer"),
]

SERVICES = [
    # (id/name, owner team, description, language)
    ("telemetry-ingest",   "T1", "ingests real-time sensor data from grid substations", "Go"),
    ("grid-monitor",       "T1", "real-time monitoring and alerting for grid health", "Go"),
    ("dispatch-optimizer", "T1", "optimizes power dispatch across generation assets", "Python"),
    ("customer-portal",    "T2", "customer-facing web application for accounts and usage", "TypeScript"),
    ("mobile-api",         "T2", "backend-for-frontend serving the mobile apps", "TypeScript"),
    ("outage-notifier",    "T2", "sends outage notifications via email, SMS and push", "Python"),
    ("payment-gateway",    "T3", "processes card and bank payments with external PSPs", "Java"),
    ("billing-engine",     "T3", "computes invoices from usage data and tariff plans", "Java"),
    ("tariff-service",     "T3", "manages tariff plans and pricing rules", "Java"),
    ("data-lake-sync",     "T4", "syncs operational data into the analytics lake", "Python"),
    ("reporting-service",  "T4", "generates regulatory and internal reports", "Python"),
    ("forecast-service",   "T6", "predicts energy demand using ML models", "Python"),
    ("meter-reader",       "T7", "collects readings from smart meters in the field", "Go"),
    ("auth-service",       "T8", "authentication and token issuance for all platforms", "Go"),
    ("api-gateway",        "T5", "edge routing, rate limiting and TLS termination", "Go"),
]

# DEPENDS_ON: (A, B) means "A depends on / calls B"
DEPENDENCIES = [
    ("grid-monitor",       "telemetry-ingest"),
    ("dispatch-optimizer", "grid-monitor"),
    ("dispatch-optimizer", "forecast-service"),
    ("customer-portal",    "mobile-api"),
    ("customer-portal",    "billing-engine"),
    ("customer-portal",    "auth-service"),
    ("mobile-api",         "auth-service"),
    ("mobile-api",         "billing-engine"),
    ("outage-notifier",    "grid-monitor"),
    ("outage-notifier",    "customer-portal"),
    ("billing-engine",     "payment-gateway"),      # <- key edge
    ("billing-engine",     "tariff-service"),
    ("billing-engine",     "meter-reader"),
    ("reporting-service",  "data-lake-sync"),
    ("reporting-service",  "billing-engine"),
    ("data-lake-sync",     "telemetry-ingest"),
    ("data-lake-sync",     "meter-reader"),
    ("forecast-service",   "data-lake-sync"),
    ("api-gateway",        "auth-service"),
    ("customer-portal",    "api-gateway"),
    ("payment-gateway",    "auth-service"),
]

# ---------------------------------------------------------------------------
# 2. INCIDENTS — hand-authored skeletons for narrative coherence
#    (affected services + responders chosen so ground-truth questions
#     have interesting, non-obvious answers)
# ---------------------------------------------------------------------------

INCIDENTS = [
    # id, title, severity, affected services, responders, root cause key, days_ago
    ("INC-2101", "Billing run produced duplicate invoices", "SEV2",
     ["billing-engine"], ["Nico Robin", "Light Yagami", "Olivier Armstrong"],
     "idempotency", 320),
    ("INC-2102", "Payment gateway timeout spike during evening peak", "SEV1",
     ["payment-gateway", "billing-engine"], ["Roronoa Zoro", "Nico Robin", "Misato Katsuragi"],
     "connection_pool", 300),
    ("INC-2103", "Customer portal login failures after auth deploy", "SEV1",
     ["customer-portal", "auth-service"], ["Nami", "Hinata Hyuga", "Kakashi Hatake"],
     "jwt_rotation", 285),
    ("INC-2104", "Telemetry ingest lag exceeding 15 minutes", "SEV2",
     ["telemetry-ingest", "grid-monitor"], ["Motoko Kusanagi", "Spike Spiegel"],
     "kafka_partitions", 270),
    ("INC-2105", "Smart meter readings missing for region North", "SEV2",
     ["meter-reader", "billing-engine"], ["Winry Rockbell", "Shinji Ikari", "Mikasa Ackerman"],
     "firmware", 255),
    ("INC-2106", "Forecast service producing negative demand values", "SEV3",
     ["forecast-service"], ["Senku Ishigami", "Frieren"],
     "training_data", 240),
    ("INC-2107", "API gateway 502 errors under load test", "SEV3",
     ["api-gateway"], ["Franky", "Yor Forger"],
     "keepalive", 230),
    ("INC-2108", "Outage notifications sent to wrong customers", "SEV1",
     ["outage-notifier", "customer-portal"], ["Usopp", "Tanjiro Kamado", "Nami"],
     "cache_key", 215),
    ("INC-2109", "Data lake sync silently dropping meter events", "SEV2",
     ["data-lake-sync", "meter-reader"], ["L Lawliet", "Bulma", "Loid Forger"],
     "schema_drift", 200),
    ("INC-2110", "Tariff update applied retroactively to closed invoices", "SEV2",
     ["tariff-service", "billing-engine"], ["Mikasa Ackerman", "Light Yagami"],
     "effective_date", 185),
    ("INC-2111", "Auth token validation latency degrading all platforms", "SEV1",
     ["auth-service", "api-gateway", "mobile-api"], ["Erza Scarlet", "Hinata Hyuga", "Misato Katsuragi", "Franky"],
     "cert_chain", 170),
    ("INC-2112", "Grid monitor false alarms flooding on-call", "SEV3",
     ["grid-monitor"], ["Spike Spiegel", "Edward Elric"],
     "threshold", 160),
    ("INC-2113", "Payment settlement file rejected by bank", "SEV2",
     ["payment-gateway"], ["Roronoa Zoro", "Lelouch Lamperouge"],
     "file_format", 150),
    ("INC-2114", "Mobile app showing stale usage data", "SEV3",
     ["mobile-api", "data-lake-sync"], ["Asuka Langley", "Shikamaru Nara"],
     "cache_ttl", 140),
    ("INC-2115", "Dispatch optimizer using outdated forecasts", "SEV2",
     ["dispatch-optimizer", "forecast-service"], ["Levi Ackerman", "Kurisu Makise", "Frieren"],
     "pipeline_ordering", 125),
    ("INC-2116", "Reporting service regulatory export failed month-end", "SEV2",
     ["reporting-service", "billing-engine"], ["Bulma", "Olivier Armstrong", "Nico Robin"],
     "timeout", 110),
    ("INC-2117", "Customer portal checkout errors for corporate accounts", "SEV2",
     ["customer-portal", "payment-gateway"], ["Tanjiro Kamado", "Roronoa Zoro"],
     "amount_limit", 95),
    ("INC-2118", "Meter reader fleet disconnects after network change", "SEV1",
     ["meter-reader", "telemetry-ingest"], ["Winry Rockbell", "Yor Forger", "Loid Forger"],
     "mtu", 80),
    ("INC-2119", "Duplicate outage push notifications", "SEV3",
     ["outage-notifier"], ["Usopp", "Asuka Langley"],
     "retry_dedup", 65),
    ("INC-2120", "Billing engine OOM during quarterly reconciliation", "SEV1",
     ["billing-engine", "reporting-service"], ["Light Yagami", "Olivier Armstrong", "Kakashi Hatake"],
     "memory", 50),
]

ROOT_CAUSES = {
    "idempotency":      "the invoice job lacked an idempotency key, so a retried batch re-emitted invoices that had already been written",
    "connection_pool":  "the HTTP connection pool to the external PSP was capped at 20 connections, which saturated during the 19:00 payment peak and queued requests until they timed out",
    "jwt_rotation":     "the new signing key was rotated in auth-service before customer-portal had picked up the updated JWKS, so token validation failed for freshly issued tokens",
    "kafka_partitions": "a consumer group rebalance left two Kafka partitions unassigned for 40 minutes, so substation events accumulated unprocessed",
    "firmware":         "a firmware update changed the meter payload encoding from CBOR to a proprietary framing that meter-reader could not parse, and unparseable readings were dropped silently",
    "training_data":    "a data pipeline change introduced negative consumption rows into the training set, and the model learned to extrapolate them",
    "keepalive":        "upstream keepalive timeout (60s) exceeded the load balancer idle timeout (30s), so the LB reused connections the upstream had already closed",
    "cache_key":        "the notification recipient cache was keyed by postal code instead of account id, so customers in the same postal code received each other's outage notifications",
    "schema_drift":     "meter-reader added a new field to its event schema; data-lake-sync's strict Avro reader rejected the events and the dead-letter queue had no alerting",
    "effective_date":   "the tariff update API defaulted effective_date to 1970-01-01 when the field was omitted, causing recalculation of historical invoices",
    "cert_chain":       "an intermediate certificate expired; token validation fell back to full chain resolution on every request, adding 800ms of latency platform-wide",
    "threshold":        "a sensitivity threshold was accidentally deployed with the staging value (0.1 instead of 0.7), turning normal fluctuation into alerts",
    "file_format":      "the bank switched settlement format from fixed-width to ISO 20022 XML on a contractual date that was tracked in a spreadsheet nobody checked",
    "cache_ttl":        "usage-summary cache TTL was raised from 5 minutes to 24 hours during a cost-cutting change, without invalidation on new data arrival",
    "pipeline_ordering":"the forecast publication step ran before model inference completed, so the optimizer consumed the previous day's forecast file",
    "timeout":          "the month-end export query joined twelve months of invoice lines without an index on billing_period, exceeding the 300s statement timeout",
    "amount_limit":     "corporate invoices above €50,000 exceeded the PSP's per-transaction limit; the gateway surfaced this as a generic 402 the portal did not handle",
    "mtu":              "a network change reduced the VPN MTU to 1400, and the meter fleet's TLS handshake packets were silently fragmented and dropped",
    "retry_dedup":      "the push provider returned 5xx after successfully delivering, and our retry logic had no deduplication window",
    "memory":           "the reconciliation job loaded the full quarter of invoice lines into memory instead of streaming, exceeding the 8GB pod limit",
}

ACTION_ITEMS = {
    "idempotency":      ["Add idempotency keys to all batch write jobs", "Alert on duplicate invoice numbers"],
    "connection_pool":  ["Raise PSP connection pool to 200 with queue rejection", "Add pool saturation dashboards"],
    "jwt_rotation":     ["Automate JWKS propagation checks before key rotation", "Add canary token validation to deploys"],
    "kafka_partitions": ["Alert on unassigned partitions within 5 minutes", "Document consumer rebalance runbook"],
    "firmware":         ["Add parse-failure metrics with paging alert", "Require decoding contract tests for firmware rollouts"],
    "training_data":    ["Add range validation to training pipeline", "Reject models whose predictions violate physical bounds"],
    "keepalive":        ["Align LB and upstream keepalive timeouts", "Add 502 rate to golden signals"],
    "cache_key":        ["Key all per-customer caches by account id", "Add PII-safety review to notification changes"],
    "schema_drift":     ["Move to schema registry with compatibility checks", "Alert on dead-letter queue depth"],
    "effective_date":   ["Make effective_date mandatory in tariff API", "Guard recalculation of settled invoices"],
    "cert_chain":       ["Monitor certificate expiry at 30/14/7 days", "Cache full chain validation results"],
    "threshold":        ["Separate staging and production config repositories", "Add config diff to deploy approval"],
    "file_format":      ["Track partner contract dates in the service catalog", "Add settlement file schema validation in CI"],
    "cache_ttl":        ["Invalidate usage cache on ingestion events", "Require review for TTL changes above 1 hour"],
    "pipeline_ordering":["Add explicit dependency between inference and publication steps", "Fail closed when forecast file is stale"],
    "timeout":          ["Add billing_period index", "Stream month-end export in batches"],
    "amount_limit":     ["Split corporate payments above PSP limit", "Map PSP error codes to actionable portal messages"],
    "mtu":              ["Clamp MSS on the VPN concentrator", "Add fleet connectivity canary"],
    "retry_dedup":      ["Add 10-minute deduplication window keyed by notification id", "Treat provider 5xx-after-delivery as success"],
    "memory":           ["Stream reconciliation instead of loading in memory", "Alert at 80% of pod memory limit"],
}

BASE_DATE = date(2026, 6, 1)

def inc_date(days_ago):
    return (BASE_DATE - timedelta(days=days_ago)).isoformat()

TEAM_BY_ID = {t["id"]: t for t in TEAMS}
ENG_TEAM = {e[0]: e[1] for e in ENGINEERS}
SVC_OWNER = {s[0]: s[1] for s in SERVICES}
SVC_DESC = {s[0]: s[2] for s in SERVICES}

def team_name(tid): return TEAM_BY_ID[tid]["name"]

# ---------------------------------------------------------------------------
# 3. DOCUMENT GENERATION
# ---------------------------------------------------------------------------

documents = []  # (doc_id, doc_type, title, date, text, metadata)

def add_doc(doc_id, doc_type, title, d, text, meta=None):
    documents.append({
        "doc_id": doc_id, "doc_type": doc_type, "title": title,
        "date": d, "text": text.strip() + "\n", "metadata": meta or {},
    })

# ---- 3a. Incident postmortems (20) --------------------------------------

PM_OPENERS = [
    "This postmortem covers {title_lower}. It is written blamelessly; our goal is to improve the system, not to assign fault.",
    "On {date}, NordWind experienced {title_lower}. This document records the timeline, root cause, and follow-up actions.",
    "The following is the incident review for {inc_id}, {title_lower}. It was compiled from the incident channel and on-call notes.",
]

def make_postmortem(inc):
    inc_id, title, sev, affected, responders, cause_key, days_ago = inc
    d = inc_date(days_ago)
    lead = responders[0]
    lead_team = team_name(ENG_TEAM[lead])
    cause = ROOT_CAUSES[cause_key]
    actions = ACTION_ITEMS[cause_key]
    opener = random.choice(PM_OPENERS).format(
        title_lower=title[0].lower() + title[1:], date=d, inc_id=inc_id)

    affected_lines = []
    for s in affected:
        affected_lines.append(f"- **{s}** (owned by {team_name(SVC_OWNER[s])}): {SVC_DESC[s]}")

    resp_lines = []
    for r in responders:
        role = "incident lead" if r == lead else "responder"
        resp_lines.append(f"- {r} ({team_name(ENG_TEAM[r])}) — {role}")

    detect_min = random.randint(3, 25)
    mitigate_min = detect_min + random.randint(20, 90)
    resolve_min = mitigate_min + random.randint(30, 240)

    impact_pool = {
        "SEV1": ["Customer-facing functionality was degraded for a significant share of users.",
                 "The incident was visible to customers and triggered inbound support contacts."],
        "SEV2": ["Impact was significant internally but customer visibility was limited.",
                 "A subset of customers and internal workflows were affected."],
        "SEV3": ["Impact was contained to internal teams; no customer-facing degradation was observed."],
    }

    text = f"""# Postmortem {inc_id}: {title}

**Date:** {d} · **Severity:** {sev} · **Status:** Resolved
**Incident lead:** {lead} ({lead_team})

{opener}

## Impact

{random.choice(impact_pool[sev])} Time to detect was {detect_min} minutes; time to mitigate was {mitigate_min} minutes; full resolution took {resolve_min} minutes.

## Affected services

{chr(10).join(affected_lines)}

## Responders

{chr(10).join(resp_lines)}

## Timeline

- **T+0** — Monitoring detected anomalous behaviour related to {affected[0]}.
- **T+{detect_min}m** — {lead} was paged and declared {sev}. An incident channel was opened.
- **T+{mitigate_min}m** — Mitigation applied; impact reduced while investigation continued.
- **T+{resolve_min}m** — Root cause confirmed and fix deployed. Incident closed.

## Root cause

The root cause was that {cause}.

## What went well

- Paging worked and the right people were in the channel within minutes.
- {random.choice(["Rollback procedures were up to date.", "Dashboards made the blast radius clear quickly.", "Cross-team communication was fast and focused."])}

## Action items

{chr(10).join(f"- [ ] {a} (owner: {random.choice(responders)})" for a in actions)}
"""
    add_doc(f"PM-{inc_id}", "postmortem", f"Postmortem {inc_id}: {title}", d, text,
            {"incident_id": inc_id, "severity": sev, "affected_services": affected,
             "responders": responders})

for inc in INCIDENTS:
    make_postmortem(inc)

# ---- 3b. Architecture Decision Records (10) ------------------------------

ADRS = [
    ("ADR-001", "Adopt Kafka as the event backbone for grid telemetry", "telemetry-ingest",
     "Motoko Kusanagi", 700,
     "Substation sensor volume is growing 40% year over year and the previous RabbitMQ setup could not provide replayability. We evaluated Kafka, Pulsar and Kinesis. Kafka was selected for its mature ecosystem, exactly-once semantics within a partition, and the team's operational familiarity. telemetry-ingest publishes raw readings to the `grid.telemetry.raw` topic; grid-monitor and data-lake-sync consume independently. Consequence: consumer group rebalances become an operational concern and must be monitored."),
    ("ADR-002", "Split billing-engine from payment-gateway", "billing-engine",
     "Nico Robin", 640,
     "Historically invoice computation and payment execution lived in a single 'billing' monolith. Deploys of tariff logic risked payment processing, and PCI scope covered the entire codebase. We decided to split into billing-engine (invoice computation, tariff application) and payment-gateway (PSP integration, settlement). billing-engine calls payment-gateway over a versioned internal API. Consequence: PCI scope shrinks to payment-gateway alone, but we accept a synchronous dependency from billing-engine to payment-gateway for payment initiation."),
    ("ADR-003", "Standardize authentication on auth-service with short-lived JWTs", "auth-service",
     "Erza Scarlet", 600,
     "Each platform previously handled sessions differently. We standardize on auth-service issuing 15-minute JWTs with rotating signing keys published via JWKS. customer-portal, mobile-api, api-gateway and payment-gateway validate tokens locally. Consequence: key rotation becomes a coordinated event across all consumers; a stale JWKS cache anywhere causes validation failures."),
    ("ADR-004", "Adopt Avro with a schema registry for meter events", "meter-reader",
     "Winry Rockbell", 520,
     "Meter firmware evolves independently of backend services and past encoding changes have broken downstream consumers. We adopt Avro with a central schema registry and backward-compatibility enforcement. meter-reader registers schemas on deploy; data-lake-sync and billing-engine resolve schemas at read time. Consequence: schema changes that break compatibility are rejected in CI rather than discovered in production."),
    ("ADR-005", "Move demand forecasting to a feature-store architecture", "forecast-service",
     "Frieren", 480,
     "Forecast features were computed ad hoc inside training scripts, causing training/serving skew. We introduce a feature store fed by data-lake-sync; forecast-service reads identical features at training and inference time. Consequence: data-lake-sync becomes a hard dependency of the forecasting stack and its freshness SLO must be tightened to 30 minutes."),
    ("ADR-006", "Introduce api-gateway as the single edge for external traffic", "api-gateway",
     "Misato Katsuragi", 560,
     "External clients previously reached services through three separate load balancers with inconsistent TLS and rate-limiting configuration. We introduce api-gateway as the single edge: TLS termination, rate limiting, and routing to customer-portal and mobile-api. Consequence: api-gateway becomes a critical single point of failure and must run across three availability zones."),
    ("ADR-007", "Use outbox pattern for outage notifications", "outage-notifier",
     "Usopp", 430,
     "Notifications were previously fired directly from grid-monitor event handlers, and a notifier outage meant lost notifications. We adopt the transactional outbox: grid-monitor writes notification intents to its database; outage-notifier polls the outbox and handles delivery, retries and deduplication. Consequence: at-least-once delivery becomes the contract, and deduplication must be handled downstream."),
    ("ADR-008", "Stream month-end reporting instead of batch loading", "reporting-service",
     "Olivier Armstrong", 100,
     "Month-end regulatory exports have repeatedly hit statement timeouts and memory limits as invoice volume grows (see INC-2116 and INC-2120). We move reporting-service to cursor-based streaming over billing data with checkpointing. Consequence: exports become resumable and memory-bounded, at the cost of a more complex failure model."),
    ("ADR-009", "Adopt OpenTelemetry across all services", "api-gateway",
     "Kakashi Hatake", 380,
     "Incident investigations regularly stall while correlating logs across services with inconsistent formats. We adopt OpenTelemetry tracing with W3C trace context propagated from api-gateway through every internal call. Consequence: every service owner must instrument their service; Core Infrastructure provides a shared SDK wrapper."),
    ("ADR-010", "Isolate corporate payments onto a dedicated PSP route", "payment-gateway",
     "Roronoa Zoro", 60,
     "Corporate invoices routinely exceed the consumer PSP's per-transaction limit (see INC-2117). We route payments above €50,000 to a dedicated corporate PSP with bank-transfer rails. payment-gateway selects the route based on amount and account type. Consequence: two PSP integrations must be maintained, with separate settlement reconciliation."),
]

for adr_id, title, svc, author, days_ago, body in ADRS:
    d = inc_date(days_ago)
    text = f"""# {adr_id}: {title}

**Status:** Accepted · **Date:** {d} · **Author:** {author} ({team_name(ENG_TEAM[author])})
**Primary service:** {svc}

## Context and decision

{body}
"""
    add_doc(adr_id, "adr", f"{adr_id}: {title}", d, text,
            {"service": svc, "author": author})

# ---- 3c. Runbooks (15) ----------------------------------------------------

RUNBOOK_SECTIONS = {
    "telemetry-ingest": ("Consumer lag on grid.telemetry.raw",
        "Check the consumer group status first. If partitions are unassigned, restart one consumer pod at a time and watch reassignment. Never restart all pods simultaneously — a full rebalance under load extends the lag. If lag exceeds 15 minutes, notify Grid Operations on-call because grid-monitor alerting fidelity degrades."),
    "grid-monitor": ("Alert storm triage",
        "If alert volume exceeds 50/minute, first verify thresholds against the production config repository — staging values have leaked before. Silence by alert class, never globally. Escalate to the Grid Operations tech lead if substation-level alerts persist after threshold verification."),
    "dispatch-optimizer": ("Stale forecast input",
        "The optimizer refuses to run if the forecast file is older than 6 hours, and falls back to the last valid dispatch plan. Verify forecast-service published today's file to the shared bucket; if not, page Forecasting & AI. Do not hand-edit dispatch plans without sign-off from Grid Operations."),
    "customer-portal": ("Login failure spike",
        "Login failures above 5% are almost always upstream: check auth-service JWKS freshness first, then api-gateway 5xx rates. The portal caches JWKS for 10 minutes; a forced refresh endpoint exists at /internal/jwks/refresh. If failures correlate with an auth-service deploy, roll back auth-service, not the portal."),
    "mobile-api": ("Stale usage data reports",
        "Usage summaries are cached; check the cache TTL configuration before investigating pipelines. If data-lake-sync freshness lags, the mobile app shows yesterday's usage — this is expected degraded mode, communicate it in the status page rather than restarting services."),
    "outage-notifier": ("Duplicate or misdirected notifications",
        "Stop the world first: pause outbox polling via the /internal/pause endpoint. Verify recipient resolution keys (must be account id) and the deduplication window. Misdirected notifications are a privacy incident — page Security & Identity immediately in addition to the service owner."),
    "payment-gateway": ("PSP timeout spike",
        "Check connection pool saturation dashboards before anything else — pool exhaustion looks identical to PSP-side degradation. If the PSP status page confirms an incident on their side, enable the payment retry queue and inform Payments & Billing lead. Never disable idempotency checks to 'push payments through'."),
    "billing-engine": ("Invoice batch failure",
        "Identify whether the failure is pre- or post-write. Pre-write failures can simply be re-run. Post-write failures must never be blindly retried — verify idempotency keys are present for the batch, otherwise duplicate invoices are created (see INC-2101). Quarterly reconciliation jobs must be run with streaming mode enabled."),
    "tariff-service": ("Tariff change validation",
        "Every tariff change requires an explicit effective_date — the API rejects omissions since INC-2110. Preview the recalculation scope with the dry-run endpoint before applying. Changes touching closed invoices require Payments & Billing lead approval."),
    "data-lake-sync": ("Dead-letter queue growth",
        "DLQ depth above 1,000 events indicates schema rejection. Compare the producing service's registered schema version against what data-lake-sync resolves. Replay from the DLQ only after the schema mismatch is fixed; replaying rejected events without a fix loops them straight back."),
    "reporting-service": ("Month-end export failure",
        "Exports are checkpointed; always resume, never restart from scratch. Check the checkpoint table for the last completed cursor. If the export is close to the regulatory deadline, notify Data Platform lead — a manual extract procedure exists but requires four-eyes approval."),
    "forecast-service": ("Implausible forecast values",
        "The service enforces physical bounds on predictions since INC-2106; if bounds violations spike, the model is likely consuming corrupted features. Freeze model promotion, pin the previous model version, and open a data-quality investigation with Data Platform."),
    "meter-reader": ("Fleet disconnect wave",
        "Distinguish network from firmware: a synchronized disconnect across regions after a network change points to MTU/MSS issues (see INC-2118); region-by-region degradation after a rollout points to firmware. The fleet canary dashboard shows handshake success rates per region."),
    "auth-service": ("Token validation latency",
        "Check certificate chain validity first — an expired intermediate certificate causes platform-wide latency (see INC-2111). Certificate expiry alerts fire at 30/14/7 days; if you are reading this during an incident, someone ignored three alerts. Key rotations must follow the JWKS propagation checklist."),
    "api-gateway": ("Elevated 502 responses",
        "Compare upstream keepalive and LB idle timeouts before scaling anything — mismatched timeouts produce 502s that look like capacity problems (see INC-2107). The gateway runs in three availability zones; verify zone health before failing over."),
}

for i, (svc, (scenario, body)) in enumerate(RUNBOOK_SECTIONS.items(), 1):
    owner = team_name(SVC_OWNER[svc])
    d = inc_date(random.randint(30, 400))
    text = f"""# Runbook: {svc} — {scenario}

**Service:** {svc} · **Owning team:** {owner} · **Last reviewed:** {d}

## Service summary

{svc} {SVC_DESC[svc]}.

## Scenario: {scenario}

{body}

## Escalation

Primary escalation is the {owner} on-call rotation. For customer-data exposure of any kind, additionally page Security & Identity without waiting for confirmation.
"""
    add_doc(f"RB-{i:03d}", "runbook", f"Runbook: {svc} — {scenario}", d, text,
            {"service": svc, "team": owner})

# ---- 3d. Slack-style threads (12) ----------------------------------------

THREADS = [
    ("#incident-2102", 299, [
        ("Roronoa Zoro", "seeing PSP timeouts climb again, same shape as yesterday evening"),
        ("Misato Katsuragi", "pool saturation graph is pegged at 20/20 connections. that's our side, not theirs"),
        ("Nico Robin", "raising the pool now. also queuing a proper fix — we should reject instead of queue when saturated"),
        ("Roronoa Zoro", "confirmed recovery at 19:42. writing the postmortem tomorrow, action items already obvious"),
    ]),
    ("#payments-billing", 180, [
        ("Light Yagami", "reminder: the effective_date guard is live. tariff calls without it now 400"),
        ("Mikasa Ackerman", "already caught one integration that was omitting it 🎉"),
        ("Nico Robin", "good. INC-2110 must never happen again — recalculating closed invoices was our worst week this year"),
    ]),
    ("#platform-eng", 168, [
        ("Franky", "post-INC-2111 we now monitor cert expiry at 30/14/7 days across everything the gateway touches"),
        ("Kakashi Hatake", "the irony of an *identity* provider going down because of an expired intermediate cert"),
        ("Misato Katsuragi", "800ms extra on every request platform-wide. cheapest possible lesson would have been reading the alert email"),
        ("Erza Scarlet", "to be fair the alert went to a mailbox that was decommissioned in the org migration. fixed now — alerts page on-call directly"),
    ]),
    ("#forecasting", 124, [
        ("Kurisu Makise", "dispatch got yesterday's forecast again — pipeline ordering, publication ran before inference finished"),
        ("Frieren", "adding an explicit dependency between the steps. also making the optimizer fail closed on stale files"),
        ("Levi Ackerman", "grid ops appreciates it. we dispatched against stale numbers for 6 hours before anyone noticed"),
    ]),
    ("#data-platform", 199, [
        ("L Lawliet", "DLQ hit 40k events silently. meter-reader added a field and our strict avro reader said no"),
        ("Bulma", "the registry migration (ADR-004) fixes exactly this — compatibility check happens in their CI, not our runtime"),
        ("Shikamaru Nara", "also adding DLQ depth alerting. 40k silent rejections is embarrassing"),
    ]),
    ("#field-systems", 79, [
        ("Winry Rockbell", "fleet disconnect root cause confirmed: VPN MTU dropped to 1400, TLS handshakes fragmented and dropped"),
        ("Yor Forger", "clamping MSS on the concentrator. networking change reviews now include the meter fleet checklist"),
        ("Loid Forger", "adding a per-region handshake canary so next time we see it in minutes, not hours"),
    ]),
    ("#customer-platform", 214, [
        ("Nami", "postal-code cache keys. we sent outage notifications to *neighbours* of affected customers"),
        ("Usopp", "every per-customer cache is now keyed by account id, checked in CI with a lint rule"),
        ("Erza Scarlet", "security review sign-off done. classifying as privacy near-miss, regulator notification not required this time"),
    ]),
    ("#billing-oncall", 49, [
        ("Light Yagami", "reconciliation OOM'd again, 8GB pod limit, full quarter in memory"),
        ("Olivier Armstrong", "ADR-008 streaming work covers this. reporting-service is moving to cursor-based export, billing reconciliation should adopt the same pattern"),
        ("Kakashi Hatake", "bumping the pod to 16GB as a stopgap tonight so the quarter closes, but the fix is streaming, not RAM"),
    ]),
    ("#grid-ops", 159, [
        ("Edward Elric", "alert storm was a config leak — staging threshold 0.1 went to prod, should be 0.7"),
        ("Spike Spiegel", "separating the config repos per ADR discussion. also adding config diff to deploy approvals"),
        ("Motoko Kusanagi", "good catch. 300 pages in one night is how you burn out an on-call rotation"),
    ]),
    ("#security", 149, [
        ("Lelouch Lamperouge", "bank rejected the settlement file — they moved to ISO 20022 on a date that lived in a spreadsheet"),
        ("Roronoa Zoro", "partner contract dates are going into the service catalog with automated reminders. spreadsheets are where deadlines go to die"),
    ]),
    ("#mobile", 139, [
        ("Asuka Langley", "stale usage data reports — cache TTL was raised to 24h in a cost change, nobody added invalidation"),
        ("Shikamaru Nara", "wiring invalidation to ingestion events now. TTL changes above 1h now need review"),
    ]),
    ("#eng-all", 20, [
        ("Misato Katsuragi", "OpenTelemetry rollout is at 12 of 15 services. holdouts: dispatch-optimizer, tariff-service, meter-reader"),
        ("Winry Rockbell", "meter-reader lands next sprint, embedded constraints made the SDK wrapper tricky"),
        ("Kakashi Hatake", "once we're at 15/15, incident correlation stops being archaeology. looking forward to it"),
    ]),
]

for i, (channel, days_ago, msgs) in enumerate(THREADS, 1):
    d = inc_date(days_ago)
    lines = "\n".join(f"**{who}:** {msg}" for who, msg in msgs)
    text = f"""# Slack thread — {channel} ({d})

{lines}
"""
    add_doc(f"SL-{i:03d}", "slack_thread", f"Slack thread {channel} ({d})", d, text,
            {"channel": channel, "participants": sorted({who for who, _ in msgs})})

# ---- 3e. Onboarding / overview docs (8) ----------------------------------

OVERVIEWS = [
    ("OV-001", "NordWind Energy — Engineering Overview",
     f"""NordWind Energy is a fictional Northern European power utility serving 2.4 million customers. Engineering is organised into eight teams: {", ".join(t["name"] for t in TEAMS)}. Each service has exactly one owning team, and cross-team changes go through the architecture review process documented in our ADRs. The platform runs on Kubernetes across three availability zones, with Kafka as the event backbone and PostgreSQL as the default operational store."""),
    ("OV-002", "Service Catalog — Customer Domain",
     """The customer domain consists of customer-portal (the web application), mobile-api (backend-for-frontend for the iOS and Android apps), and outage-notifier (multi-channel notifications). All customer-facing traffic enters through api-gateway. Authentication is delegated to auth-service; the portal and mobile-api never handle credentials directly. Usage data displayed to customers originates from meter-reader and flows through data-lake-sync."""),
    ("OV-003", "Service Catalog — Payments Domain",
     """The payments domain is owned by Payments & Billing and consists of three services. tariff-service manages pricing plans and their effective dates. billing-engine computes invoices by combining meter readings with tariff rules. payment-gateway executes payments against external PSPs and handles settlement files. The split between billing-engine and payment-gateway is documented in ADR-002 and keeps PCI scope minimal. Corporate payments above €50,000 use a dedicated PSP route per ADR-010."""),
    ("OV-004", "Service Catalog — Grid Domain",
     """The grid domain covers real-time operations: telemetry-ingest consumes substation sensor streams into Kafka, grid-monitor evaluates grid health and raises alerts, and dispatch-optimizer plans generation dispatch using demand forecasts. The forecasts come from forecast-service, owned by Forecasting & AI. Grid operations are safety-relevant: dispatch plan overrides always require human sign-off."""),
    ("OV-005", "On-call and Incident Process",
     """Every team runs a weekly on-call rotation. Incidents are classified SEV1 (customer-facing, all hands), SEV2 (significant, limited visibility) and SEV3 (internal). The incident lead is the first responder from the owning team of the most affected service. Every SEV1 and SEV2 requires a blameless postmortem within five working days. Privacy-relevant incidents additionally page Security & Identity regardless of severity."""),
    ("OV-006", "New Engineer Onboarding — Week One",
     """Welcome to NordWind. In week one you will: get access to the service catalog and this documentation set; shadow your team's on-call; read the three most recent postmortems in your domain; and deploy a small change behind a feature flag. Our engineering culture values blameless reviews, written decisions (ADRs), and boring technology chosen deliberately."""),
    ("OV-007", "Data Flow — From Meter to Invoice",
     """A meter reading travels the following path: meter-reader collects it from the field device and publishes an Avro event; data-lake-sync lands it in the analytics lake; billing-engine consumes readings for the billing period, applies tariffs from tariff-service, and produces an invoice; payment-gateway then executes payment collection. Any break in this chain shows up, eventually, as a billing anomaly — which is why meter events use schema-registry enforcement per ADR-004."""),
    ("OV-008", "Observability Standards",
     """All services emit OpenTelemetry traces with W3C context propagation, structured JSON logs, and RED metrics (rate, errors, duration). Golden-signal dashboards are generated from the service catalog. Alerting policy: every page must be actionable and linked to a runbook. Alert fatigue is treated as an incident in its own right — see the grid-monitor alert storm postmortem for why."""),
]

for ov_id, title, body in OVERVIEWS:
    d = inc_date(random.randint(50, 500))
    text = f"# {title}\n\n{body}\n"
    add_doc(ov_id, "overview", title, d, text, {})

# ---------------------------------------------------------------------------
# 4. GROUND TRUTH — canonical answers for workshop questions
# ---------------------------------------------------------------------------

# Q-KEY: "Which engineers responded to incidents affecting services that
#         depend on payment-gateway?"
dependents_of_pg = sorted({a for a, b in DEPENDENCIES if b == "payment-gateway"})
key_engineers = sorted({
    r for (inc_id, title, sev, affected, responders, ck, da) in INCIDENTS
    if any(s in dependents_of_pg for s in affected)
    for r in responders
})

ground_truth = {
    "key_multihop_question": {
        "question": "Which engineers have responded to incidents affecting services that depend on payment-gateway?",
        "services_depending_on_payment_gateway": dependents_of_pg,
        "qualifying_incidents": [
            inc[0] for inc in INCIDENTS if any(s in dependents_of_pg for s in inc[3])
        ],
        "answer_engineers": key_engineers,
        "why_vector_rag_fails": "The dependency edge (billing-engine -> payment-gateway) lives in ADR-002/OV-003, while responder lists live in separate postmortems. Answering requires joining across documents and aggregating — semantic similarity retrieves fragments, not the join.",
    },
    "supporting_questions": {
        "most_incident_prone_service": max(
            {s: sum(1 for i in INCIDENTS if s in i[3]) for s in SVC_DESC}.items(),
            key=lambda kv: kv[1]),
        "engineer_incident_counts": {
            e[0]: sum(1 for i in INCIDENTS if e[0] in i[4]) for e in ENGINEERS},
        "cross_team_responder_incidents": [
            i[0] for i in INCIDENTS
            if len({ENG_TEAM[r] for r in i[4]}) > 1],
    },
}

# ---------------------------------------------------------------------------
# 5. WRITE EVERYTHING
# ---------------------------------------------------------------------------

(ENTS / "teams.json").write_text(json.dumps(TEAMS, indent=2))
(ENTS / "engineers.json").write_text(json.dumps(
    [{"name": n, "team_id": t, "role": r, "team_name": team_name(t)}
     for n, t, r in ENGINEERS], indent=2))
(ENTS / "services.json").write_text(json.dumps(
    [{"name": s, "owner_team_id": t, "owner_team": team_name(t),
      "description": d, "language": lang}
     for s, t, d, lang in SERVICES], indent=2))
(ENTS / "incidents.json").write_text(json.dumps(
    [{"id": i, "title": t, "severity": sv, "affected_services": af,
      "responders": rs, "root_cause_key": ck, "date": inc_date(da)}
     for i, t, sv, af, rs, ck, da in INCIDENTS], indent=2))

relationships = (
    [{"type": "MEMBER_OF", "from": n, "to": team_name(t)} for n, t, _ in ENGINEERS] +
    [{"type": "OWNS", "from": team_name(t), "to": s} for s, t, _, _ in SERVICES] +
    [{"type": "DEPENDS_ON", "from": a, "to": b} for a, b in DEPENDENCIES] +
    [{"type": "AFFECTED", "from": i[0], "to": s} for i in INCIDENTS for s in i[3]] +
    [{"type": "RESPONDED_TO", "from": r, "to": i[0]} for i in INCIDENTS for r in i[4]]
)
(OUT / "relationships.json").write_text(json.dumps(relationships, indent=2))
(OUT / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2))

# Documents: individual markdown + one JSONL for easy loading in Colab
with open(OUT / "documents.jsonl", "w") as f:
    for doc in documents:
        f.write(json.dumps(doc) + "\n")
        safe = doc["doc_id"].replace("/", "_")
        (DOCS / f"{safe}.md").write_text(doc["text"])

manifest = {
    "world": "NordWind Energy (fictional)",
    "seed": 42,
    "counts": {
        "teams": len(TEAMS), "engineers": len(ENGINEERS),
        "services": len(SERVICES), "incidents": len(INCIDENTS),
        "documents": len(documents), "relationships": len(relationships),
        "docs_by_type": {t: sum(1 for d in documents if d["doc_type"] == t)
                         for t in ["postmortem", "adr", "runbook", "slack_thread", "overview"]},
    },
    "checksum": hashlib.md5(
        "".join(d["text"] for d in documents).encode()).hexdigest(),
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
print("\nKey question ground truth:")
print("  Dependents of payment-gateway:", dependents_of_pg)
print("  Qualifying incidents:", ground_truth["key_multihop_question"]["qualifying_incidents"])
print("  Answer engineers:", key_engineers)
