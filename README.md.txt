# Page Pulse

> Instant webpage health audits — status, speed, structure, and accessibility, in one scan.

Built for the **Digital Heroes Software Development Internship**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Folder Structure](#folder-structure)
- [API Documentation](#api-documentation)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [Design Decisions](#design-decisions)
- [Future Improvements](#future-improvements)
- [Testing](#testing)
- [License](#license)

---

## Project Overview

Page Pulse is a full-stack web application that audits any public webpage URL.
Given a URL, it fetches the page, measures how it responds, and reports a
compact set of health and accessibility signals: HTTP status, response time,
page title, meta description, heading structure, missing image alt text, and
approximate word count.

The project is split into two independently deployable parts:

- **Backend** — a FastAPI service that performs the actual fetch + analysis
  and exposes a single JSON API endpoint.
- **Frontend** — a React (Vite) single-page app that gives that endpoint a
  visual, diagnostic-monitor-themed interface.

---

## Features

- Accepts any URL and validates its format before use
- Fetches the target page and measures real response time
- Reports the target's HTTP status code
- Extracts the page `<title>`
- Extracts the meta description (falls back to Open Graph description)
- Counts `<h1>` headings
- Counts `<img>` tags missing usable `alt` text
- Calculates an approximate visible word count
- Structured JSON API with a predictable error contract
- Explicit handling for invalid URLs, timeouts, non-HTML responses, and
  server-side failures
- Responsive, card-based results UI with loading and error states

---

## Tech Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Frontend   | React 18 + Vite                                |
| Backend    | FastAPI (Python)                               |
| Parsing    | BeautifulSoup4                                 |
| HTTP client (server-side) | `requests`                       |
| Testing    | pytest, FastAPI `TestClient`, `unittest.mock`   |
| Frontend deploy | Vercel                                    |
| Backend deploy  | Render                                    |

---

## Installation

Clone the repository, then set up each side independently.

### Backend

```
cd backend
pip install -r requirements.txt
```

### Frontend

```
cd frontend
npm install
```

---

## Folder Structure

```
page-pulse/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app, CORS, global error handlers
│   │   ├── routes/
│   │   │   └── audit.py           # POST /audit route
│   │   ├── services/
│   │   │   ├── fetcher.py         # HTTP fetch + timing + content-type checks
│   │   │   └── audit_service.py   # Orchestrates validate → fetch → parse
│   │   ├── parser/
│   │   │   └── html_parser.py     # BeautifulSoup metric extraction
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   └── utils/
│   │       ├── validators.py      # URL format validation
│   │       └── exceptions.py      # Error hierarchy → HTTP status mapping
│   ├── tests/                     # pytest suite (see Testing)
│   ├── requirements.txt
│   ├── requirements-dev.txt       # pytest + httpx, test-only
│   └── pytest.ini
│
└── frontend/
    ├── src/
    │   ├── main.jsx / App.jsx / index.css
    │   ├── api/
    │   │   └── auditApi.js        # POST /audit client
    │   ├── utils/
    │   │   └── validateUrl.js     # Client-side URL format check
    │   └── components/
    │       ├── Header.jsx / Footer.jsx
    │       ├── ScanForm.jsx       # URL input
    │       ├── PulseMonitor.jsx   # Animated status/EKG indicator
    │       ├── ResultsPanel.jsx / VitalCard.jsx
    │       ├── ErrorBanner.jsx
    │       └── EmptyState.jsx
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── .env.example
```

---

## API Documentation

### `POST /audit`

Audits a single URL and returns its vitals.

**Request body**

```json
{
  "url": "https://example.com"
}
```

**Successful response** — `200 OK`

```json
{
  "status": 200,
  "response_time": 0.198,
  "page_title": "Example Domain",
  "meta_description": "An example page used for illustrative purposes.",
  "h1_count": 1,
  "images_missing_alt": 0,
  "word_count": 42
}
```

| Field                | Type    | Description                                              |
|----------------------|---------|------------------------------------------------------------|
| `status`             | integer | HTTP status code returned **by the target URL** (not Page Pulse itself) |
| `response_time`      | float   | Time to fetch the page, in seconds                        |
| `page_title`         | string \| null | Contents of the `<title>` tag, if present           |
| `meta_description`   | string \| null | Meta description (or Open Graph description) if present |
| `h1_count`           | integer | Number of `<h1>` elements on the page                      |
| `images_missing_alt` | integer | Number of `<img>` tags with no usable `alt` attribute      |
| `word_count`         | integer | Approximate word count of visible page text                |

> **Note:** if the target page itself returns a 404 or 500, that is
> reported as data in the `status` field — it is not treated as a Page
> Pulse API error. Page Pulse's own errors (below) only cover cases where
> the audit itself could not be completed.

**Error responses**

| Status | Meaning              | When it happens                                      |
|--------|----------------------|-------------------------------------------------------|
| `400`  | Invalid URL           | Missing, malformed, or non-http(s) URL                |
| `408`  | Timeout               | The target did not respond within the request timeout |
| `415`  | Unsupported content   | The target responded with a non-HTML content type     |
| `500`  | Internal server error | Connection failure, DNS error, or unexpected exception |

Error body shape:

```json
{
  "detail": "Human-readable explanation of what went wrong."
}
```

---

## Running Locally

### 1. Start the backend

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is now available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

```
cd frontend
cp .env.example .env
npm run dev
```

By default `.env` points `VITE_API_BASE_URL` at `http://127.0.0.1:8000`. The
app runs at `http://127.0.0.1:5173`.

With both running, enter any URL in the frontend and click **Run scan**.

---

## Deployment

### Backend → Render

1. Push the `backend/` folder to a Git repository.
2. Create a new **Web Service** on Render, pointing at that repository/folder.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Note the deployed URL (e.g. `https://page-pulse-api.onrender.com`).

### Frontend → Vercel

1. Push the `frontend/` folder to a Git repository.
2. Import the project into Vercel (framework preset: **Vite**).
3. Set the environment variable `VITE_API_BASE_URL` to the Render backend
   URL from above.
4. Deploy. Vercel runs `npm run build` and serves the `dist/` output.

Because the frontend and backend are deployed to separate origins, the
backend's CORS policy is configured to accept requests from any origin.

---

## Design Decisions

- **Backend errors vs. target errors are kept separate.** A target page
  returning `404` or `500` is meaningful audit data, so it's returned as
  the `status` field with a normal `200` from Page Pulse's own API. Page
  Pulse's own error codes (`400`/`408`/`415`/`500`) are reserved for cases
  where the audit itself couldn't be completed — bad input, a timeout, an
  unreadable content type, or an unexpected failure.
- **Layered backend structure.** Routes, services, parsing, and validation
  are kept in separate modules so each piece (HTTP fetching, HTML analysis,
  input validation) can be tested and modified independently.
- **Custom exception hierarchy.** A single `PagePulseError` base class with
  a `status_code` on each subclass lets one global exception handler in
  `main.py` translate every failure into the documented error shape,
  instead of scattering `try/except` blocks across the codebase.
- **Diagnostic-monitor visual identity.** The frontend leans into the
  product's name: a live animated pulse/EKG line reflects the scan's state
  (idle → scanning → healthy/warning/failed), and results are presented as
  "vital sign" cards with color-coded indicators, echoing a medical
  monitor rather than a generic dashboard template.
- **Environment-based API URL.** The frontend never hardcodes the backend
  origin; it reads `VITE_API_BASE_URL` so the same build can point at a
  local backend during development and the deployed Render service in
  production.

---

## Future Improvements

- Add support for auditing multiple URLs in a single batch request
- Cache recent audit results to avoid re-fetching unchanged pages
- Expand accessibility checks (e.g. heading order, color contrast basics,
  form label coverage)
- Add a scan history view (persisted client-side or via a lightweight store)
- Add rate limiting on the backend to prevent abuse of the public endpoint
- Add end-to-end tests covering the frontend against a running backend
- Support authenticated/private pages via optional request headers

---

## Testing

The backend includes a pytest suite covering the full request lifecycle
without making real network calls (HTTP calls are mocked).

```
cd backend
pip install -r requirements-dev.txt
pytest -v
```

Coverage includes:

- **Happy path** — a mocked HTML response is fetched, parsed, and returned
  with correct status, timing, and all extracted metrics
- **Invalid URL** — malformed input is rejected with `400` before any
  network call is attempted
- **Timeout** — a simulated timeout returns `408`
- **Non-HTML content** — a non-HTML content type returns `415`
- Additional coverage for upstream connection failures, unhandled
  exceptions, and each HTML-parsing edge case (missing title/description,
  Open Graph fallback, script/style text exclusion, alt-text detection)

---

## License

This project was built for the **Digital Heroes Software Development
Internship** as a training task. See [digitalheroesco.com](https://digitalheroesco.com)
for more on the program. Unless otherwise specified by Digital Heroes, this
code is intended for educational and portfolio use.
