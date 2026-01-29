# Admin Accounts UI – Product Requirements Document

## 1. Summary

**Objective:** Deliver an internal **Admin Accounts UI** that lets support and operations staff quickly search, inspect, and troubleshoot **accounts/subscribers** for the AI Trip Planner system, with a focus on **investigating user connections via shared IP addresses**.

**Approach:** Build on the existing **FastAPI backend** and **single-page Tailwind frontend** in this repo, adding a simple admin API surface and a protected admin SPA section.

**Implementation Status:** ✅ **MVP Complete** — Core UI with search, user profiles, and IP connection visualization is functional with 112 mock users.

---

## 2. Problem & Goals

### Problem

Today there is no consolidated view of accounts/subscribers. Support staff must dig through logs, ad‑hoc scripts, or database views to answer basic questions:

- "Is this account active?"
- "What trips has this subscriber generated?"
- "Are these accounts linked?"

### Primary Goal

Enable admins to quickly **find an account**, **view a clear, read‑only summary** of its status, usage, and key attributes, and **investigate connections between users based on shared IP addresses**.

### Secondary Goals

- Reduce time to resolve common support tickets
- Standardize how account information is surfaced, so engineers don't need to manually query the system
- Identify potentially linked accounts (e.g., fraud detection, multi-account abuse)

### Out of Scope (v1)

- Editing account data (no create/update/delete)
- Full role-based access control (we can start with a simple admin flag or basic auth)
- Complex analytics dashboards or reporting

---

## 3. Users & Use Cases

### Primary Users

| Role | Description |
|------|-------------|
| **Customer Support** | Resolve "why isn't this working for me?" tickets |
| **Operations / PMs** | Spot high‑value subscribers and troubleshoot unusual usage |
| **Trust & Safety** | Investigate potentially linked accounts for fraud or abuse |

### Key Use Cases

| ID | Use Case | Status |
|----|----------|--------|
| UC1 | **Search by identifier** — Look up an account by email, account ID, or name | ✅ Implemented |
| UC2 | **Quick overview** — See status, plan tier, created date, and last activity | ✅ Implemented |
| UC3 | **Usage insights** — See recent trip planning activity | ⏳ Future |
| UC4 | **Debug context** — See recent backend errors associated with that account | ⏳ Future |
| UC5 | **Lightweight filtering** — Filter list by status or tier | ⏳ Future |
| UC6 | **IP Connection Investigation** — View a visual node chart showing all other users connected via shared IP addresses | ✅ Implemented |

---

## 4. Functional Requirements

### 4.1 Admin UI

#### FR1 – Admin Entry Point ✅

- Route: `/admin` accessible via direct URL
- Frontend served by **FastAPI** (`/` returns `frontend/index.html`)
- Admin UI is part of the same SPA with client-side routing

#### FR2 – Search & Results List ✅

- **Search input** accepts email, account ID (partial or full), or name
- **Auto-selection**: Searching for an exact user ID (e.g., "001") automatically selects that user
- **Debounced search**: 400ms delay to prevent excessive filtering
- **Results table** displays:
  - Profile picture + Name
  - User ID
  - Email
  - Location
  - Status (active/inactive badge)
  - Plan (paid/free badge)
  - Last activity (relative time)

#### FR3 – User Profile Widget ✅

Display a **profile card** for the selected user showing:

| Field | Format |
|-------|--------|
| Profile picture | Rounded avatar (DiceBear API) |
| Name | Large, prominent text |
| User ID | Monospace font (e.g., `USR-001`) |
| Email | Standard text |
| Sign-up location | With map pin icon |
| Sign-up date | Formatted date |
| Last activity | Relative time |
| Status badge | Green (active) / Red (inactive) |
| Plan badge | 💎 Paid / 🆓 Free |
| IP addresses | List of amber-colored tags |

#### FR4 – IP Connection Node Chart ✅

A **canvas-based visual node graph** showing:

- **Center node**: Selected user with purple glow effect
- **Connected nodes**: Users sharing at least one IP address (max 12 displayed)
- **Overflow indicator**: "+X more" message when connections exceed display limit

**Node details:**
- Profile initials in colored circle
- Full user name below node
- User ID below name
- Color coding: Green (active), Red (inactive)

**Edge details:**
- Line thickness indicates connection strength (1 IP = thin, 2+ IPs = thick)
- **IP address labels displayed on each edge**
- White background behind labels for readability

**Interactions:**
- Click any connected node to navigate and load that user's profile
- High DPI support for crisp rendering on retina displays

#### FR5 – Account Detail View ⏳

*Future enhancement — not in current MVP*

#### FR6 – Basic Filters ⏳

*Future enhancement — not in current MVP*

#### FR7 – Read‑only ✅

No actions that modify data in this MVP.

---

### 4.2 Backend / API

#### FR8 – Static File Serving ✅

- FastAPI serves frontend files from `/static` endpoint
- Allows loading of JavaScript modules and assets

#### FR9–FR12 – Admin API Endpoints ⏳

*Future enhancement — Currently using client-side mock data*

---

### 4.3 Mock Data Requirements

#### FR13 – Mock User Data ✅

**Implementation:** 112 mock users with the following schema:

```javascript
{
  user_id: "USR-001",           // Unique identifier
  name: "John Doe",             // Full name
  email: "john.doe@email.com",  // Email address
  profile_pic: "https://...",   // DiceBear avatar URL
  signup_location: "New York",  // City and country
  signup_date: "2024-01-15...", // ISO date string
  last_activity: "2026-01-29..",// ISO date string
  status: "active",             // "active" or "inactive"
  plan: "paid",                 // "free" or "paid"
  ip_addresses: ["192.168..."]  // Array of IP addresses
}
```

#### FR14 – IP Connection Relationships ✅

**Implementation details:**

- **8 IP clusters** with shared addresses to create realistic connection patterns
- **USR-001** is connected to **8+ other users** via shared IP addresses
- Probability-based IP assignment for generated users:
  - 20% chance to share cluster1 IP with USR-001
  - 15% chance to share cluster6 IP
  - 15% chance to share cluster7 IP
- Results in a rich network suitable for fraud investigation demonstrations

---

## 5. Non‑Functional Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| NFR1 | **Performance** — Search completes within <500ms | ✅ Met |
| NFR2 | **Security** — Admin endpoints protected; no secrets exposed | ⏳ Partial |
| NFR3 | **Reliability** — Graceful degradation for missing data | ✅ Met |
| NFR4 | **Stack reuse** — Tailwind + vanilla JS frontend, FastAPI backend | ✅ Met |
| NFR5 | **Visualization** — Responsive node chart with canvas rendering | ✅ Met |

---

## 6. UX & Interaction Overview

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Trip Planner – Admin                                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  🔍 Search by User ID, Email, or Name...    [Search]    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │  USER PROFILE        │  │  IP CONNECTION NETWORK           │ │
│  │  ┌────┐              │  │                                  │ │
│  │  │ 👤 │  John Doe    │  │       [User A]                   │ │
│  │  └────┘              │  │          │                       │ │
│  │  USR-001             │  │    ┌─────┼─────┐                 │ │
│  │  📍 New York, USA    │  │    │  IP:xxx   │                 │ │
│  │  ✅ Active  💎 Paid  │  │ [User B]─[YOU]─[User C]          │ │
│  │                      │  │          │                       │ │
│  │  IPs: 192.168.1.100  │  │       [User D]                   │ │
│  │       10.0.0.50      │  │                                  │ │
│  └──────────────────────┘  └──────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  SEARCH RESULTS                                             ││
│  │  ┌─────┬────────────┬──────────┬────────┬─────────────────┐││
│  │  │ ID  │ Name       │ Email    │ Status │ Last Activity   │││
│  │  ├─────┼────────────┼──────────┼────────┼─────────────────┤││
│  │  │ 001 │ John Doe   │ j@e.com  │ Active │ 2 hours ago     │││
│  │  │ 002 │ Jane Smith │ js@e.com │ Active │ 1 day ago       │││
│  │  └─────┴────────────┴──────────┴────────┴─────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### User Profile Widget

- Card-style layout with shadow and rounded corners
- Large profile picture (rounded, left-aligned)
- Name prominently displayed
- User ID in monospace/code style
- Sign-up location with map pin icon
- Status and plan badges with color coding
- IP addresses in amber tag format

### IP Connection Chart

- **Interactive canvas-based node graph**
- Center node with glow effect for selected user
- Connected nodes arranged in circular pattern
- **IP addresses displayed as labels on connecting edges**
- Click to navigate between connected users

### Error States

| State | Display |
|-------|---------|
| Search fails | Error card: "We couldn't load accounts. Please try again." |
| No results | Empty state: "No users found. Try another search term." |
| No IP connections | Message: "No linked accounts found for this user." |

---

## 7. Success Metrics

### Qualitative Goals

- ✅ Support staff can **resolve basic account inquiries** without engineering help
- ✅ Trust & Safety team can **quickly identify linked accounts** via the IP connection chart
- ✅ Admin UI is easy to access, fast, and presents "right at-a-glance" information

### Technical Validation

- ✅ Search returns results in <500ms
- ✅ USR-001 shows 8+ IP-connected users
- ✅ Node chart renders with IP labels on edges
- ✅ Click-through navigation works between connected users

---

## 8. Implementation Notes

### Files Modified

| File | Purpose |
|------|---------|
| `frontend/index.html` | Main SPA with admin UI components and inline mock data |
| `backend/main.py` | FastAPI server with static file serving |

### Mock Data Location

Mock user data (112 users) is **inlined in `index.html`** for reliability. This includes:

- `MOCK_USERS` array with full user objects
- `SHARED_IPS` clustering configuration
- Helper functions: `findConnectedUsers()`, `searchUsers()`, `formatRelativeTime()`

### Running the Application

```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows
python main.py
```

Then navigate to: `http://localhost:8000/admin`

---

## 9. Future Enhancements

| Priority | Feature | Description |
|----------|---------|-------------|
| High | Backend API | Replace mock data with real database queries |
| High | Authentication | Add admin login and role-based access |
| Medium | Filters | Add status and plan tier filtering |
| Medium | Export | CSV/JSON export of search results |
| Medium | IP History | Detailed view of IP usage timeline |
| Low | Analytics | Usage statistics and trend charts |
| Low | Bulk Actions | Multi-select for batch operations |

---

*Last updated: January 29, 2026*
