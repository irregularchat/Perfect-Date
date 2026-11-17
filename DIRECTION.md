# Direction: Perfect Date Generator

A web app that plans dates and outings from real venues (Google Places): a timeline of
activities, a map, budget and vibe filters, two-location midpoint planning, and
long-distance destination suggestions. It started at an IrregularChat virtual hackathon.

Status: dormant (last change 2025-08-16). 93 commits in two bursts: 2025-04-11 to 04-14
(Gradio and OpenAI version) and 2025-08-16 (FastAPI rewrite, done in one day).

## Where it is heading
- The last session rewrote it as a FastAPI backend (`backend.py`) with a vanilla JS/Leaflet
  frontend and SQLite. It removed the Gradio app, the React frontend and the Docker setup.
  (3d31490)
- Two-location dating shipped: a Haversine midpoint, fairness scoring, and destination
  cities for long distances. (9f8156f, e2f0a8d, b07b307, ROADMAP-TWO-LOCATION-DATING.md)
- Shareable links with rich previews were implemented. (5472dcc)

## Priorities
If work resumes, the next item in ROADMAP.md is the "Advanced Personalization Engine"
(Priority 2). Sharing (Priority 1) is implemented per 5472dcc, though ROADMAP.md still
calls it "Ready for Implementation". Before that, the minimum to resume:
1. Bring ROADMAP.md (v1.x numbering) and README.md (v0.2) into line with the code.
   (inferred)
2. Security and data hygiene review (tracked privately).

## Non-goals and constraints
- FastAPI, vanilla JavaScript, Tailwind via CDN, Leaflet, SQLite. "No framework
  dependencies" on the frontend. (README.md "Technology Stack", 3d31490)
- Venue data must be real (Google Places), not mock data. (ROADMAP.md "Venue Quality",
  e02b74e, 41bb93d)
- The Google Maps key comes from `.env` (`GOOGLE_MAPS_API_KEY`). (README.md)

## Decisions
- 2025-08-16: Restructure around FastAPI, and drop Gradio, React and Docker. (3d31490)
- 2025-08-16: Use global destination cities for long-distance pairs. (be6a027)
- 2025-08-16: Use AI-generated Places queries with an IP geolocation fallback. (93dfd71,
  c200027)
- 2025-04-12: Broaden from a date generator to an event idea generator. (fded62e)

## Open questions for the owner
1. Is this project still wanted, or was it a hackathon piece to archive? If it's wanted,
   where should it be deployed?

## Related documents
- ROADMAP.md, ROADMAP-TWO-LOCATION-DATING.md, README.md
