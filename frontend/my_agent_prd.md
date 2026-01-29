# Admin Accounts UI – Product Requirements Document

## 1. Summary

**Objective:** Deliver an internal **Admin Accounts UI** that lets support and operations staff quickly search, inspect, and troubleshoot **accounts/subscribers** for the AI Trip Planner system.

**Approach:** Build on the existing **FastAPI backend** and **single-page Tailwind frontend** in this repo, adding a simple admin API surface and a protected admin SPA section.

---

## 2. Problem & Goals

**Problem:** Today there is no consolidated view of accounts/subscribers. Support staff must dig through logs, ad‑hoc scripts, or database views to answer basic questions (e.g., “Is this account active?”, “What trips has this subscriber generated?”).

**Primary Goal:** Enable admins to quickly **find an account** and **view a clear, read‑only summary** of its status, usage, and key attributes.

**Secondary Goals:**
- Reduce time to resolve common support tickets.
- Standardize how account information is surfaced, so engineers don’t need to manually query the system.

**Out of Scope (for this first version):**
- Editing account data (no create/update/delete).
- Full role-based access control (we can start with a simple admin flag or basic auth).
- Complex analytics dashboards or reporting.

---

## 3. Users & Use Cases

**Primary users:**
- **Customer Support:** Resolve “why isn’t this working for me?” tickets.
- **Operations / PMs:** Spot high‑value subscribers and troubleshoot unusual usage.

**Key use cases:**
- **UC1 – Search by identifier:** Look up an account by email, account ID, or subscriber ID.
- **UC2 – Quick overview:** See status (active/inactive), plan tier, created date, and last activity.
- **UC3 – Usage insights:** See recent trip planning activity: number of trips, last trip timestamp, basic metadata (destination, duration).
- **UC4 – Debug context:** See any recent **backend errors** associated with that account (e.g., rate limits, invalid keys).
- **UC5 – Lightweight filtering (MVP-level):** Filter list by status (active/inactive) or tier (e.g., free/paid) to support triage.

---

## 4. Functional Requirements

### 4.1 Admin UI

- **FR1 – Admin entry point**
  - A new route in the frontend (e.g., `/admin`) accessible via direct URL (we can hide from main nav initially).
  - Frontend continues to be served by **FastAPI** (`/` returns `frontend/index.html`); admin UI is part of the same SPA.

- **FR2 – Search & results list**
  - Search input that accepts **email, account ID, or subscriber ID**.
  - On search:
    - Calls a new **FastAPI admin endpoint** (e.g., `GET /admin/accounts?query=...`).
    - Displays a list of matching accounts with key columns:
      - Account ID
      - Email (if available)
      - Plan/tier
      - Status (active/inactive)
      - Created date
      - Last activity date

- **FR3 – Account detail view**
  - Clicking a row opens a detail view (drawer or dedicated panel on the right).
  - Detail view shows:
    - **Core profile:** ID, email, created date, plan, status.
    - **Recent usage:** last N trip planning requests and their outcomes.
      - For each trip: destination, duration, timestamp, success/failure flag.
    - **Recent error summary** (e.g., last 5 backend errors tied to this account/session, such as OpenAI quota issues).

- **FR4 – Basic filters**
  - Filter controls above the table:
    - Status: All / Active / Inactive.
    - Plan: All / Free / Paid (or similar labels as defined by backend data).

- **FR5 – Read‑only**
  - No actions that modify data (no buttons like “Deactivate account”, “Change plan”, etc.) in this MVP.

### 4.2 Backend / API

Using this repo’s architecture:

- **FR6 – Accounts data model access**
  - Introduce a simple internal representation of an account/subscriber, sourced from wherever the app stores user/session data (for the course project this may be stubbed or simulated).
  - Provide a **FastAPI router** under a new namespace, e.g., `/admin/accounts`.

- **FR7 – List/search endpoint**
  - `GET /admin/accounts`:
    - Query params: `query`, `status`, `plan`, `limit`, `offset`.
    - Returns a paginated list of account summaries.

- **FR8 – Detail endpoint**
  - `GET /admin/accounts/{account_id}`:
    - Returns detailed account info plus:
      - Recent trip-planning requests.
      - Recent associated errors (e.g., stored from logs or synthetic data for this project).

- **FR9 – Auth (MVP)**
  - For now, simple protection (e.g., config‑gated admin key header or basic auth) so `/admin/accounts` is **not publicly usable**.
  - No full JWT/SSO integration in this phase; this can be layered later.

---

## 5. Non‑Functional Requirements

- **NFR1 – Performance:** Search and detail fetch should complete within **<500 ms** under normal load for typical admin queries.

- **NFR2 – Security:**
  - Admin endpoints must not be exposed without some form of admin check (even if minimal in this project context).
  - No secrets (API keys, `.env` contents) surfaced in any admin UI fields.

- **NFR3 – Reliability:** If data for some fields is missing, the UI should degrade gracefully (show “—” or “Not available”) rather than erroring.

- **NFR4 – Reuse existing stack:**
  - **Frontend:** Continue using **Tailwind + vanilla JS** in `frontend/index.html` to keep consistency with current UI.
  - **Backend:** Add endpoints to the existing **FastAPI** app in `backend/main.py` or a small module imported there; do not modify `/plan-trip` behavior.

---

## 6. UX & Interaction Overview

**Layout:**
- Admin view uses the same visual language as the existing trip planner: header bar, cards, and neutral backgrounds.
- Main content layout:
  - **Left/top:** Search + filters.
  - **Center:** Accounts table.
  - **Right/overlay:** Detail panel for the selected account.

**Error states:**
- If a search fails (backend 4xx/5xx), show a non‑intrusive error card: “We couldn’t load accounts. Please try again or contact engineering.”
- If no results: show an empty state with guidance (“Try another email, ID, or remove filters.”).

---

## 7. Success Metrics (qualitative for this project)

- Support staff can **resolve basic account inquiries** (status, last use, obvious errors) **without engineering help**.
- Internal feedback that the admin UI is:
  - Easy to access,
  - Fast enough,
  - And presents the “right at‑a‑glance” information for accounts/subscribers.

---

*If you’d like, I can next outline a very concrete “implementation steps” checklist (for engineers) that maps from this PRD into specific files/endpoints in this repo.*
