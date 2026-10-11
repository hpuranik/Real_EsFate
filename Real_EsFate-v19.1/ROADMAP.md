# Real_EsFate Roadmap

Last updated: v19. Status key: DONE / CODE DONE (needs live verification) / TODO / DEFERRED.

## Product goal
Predict neighborhood appreciation and gentrification for **land and property
investors** (Pittsburgh first, worldwide later). Four lenses: Investor,
Researcher, Resident, City Planner.

## Architecture rules (never break)
1. Every prediction traceable to a named source. No black boxes.
2. No randomness; no wall-clock dependence in mock data. Same tract, same score.
3. Missing real data falls back to a clearly labeled mock (`data_source: mock_fallback`).
4. No ML until 20+ tracts have real validated history.
5. No chatbot / autonomous agents.
6. `main.py` is the only entry point. `main_phase3.py` and `main_complete.py` are
   legacy files; do not run them (left in place by decision, not deleted).

## Phase status
| Phase | Item | Status |
|---|---|---|
| 1 | 30 neighborhoods, 214 block groups, real FIPS | DONE |
| 2 | Census ACS | CODE DONE - key set, live call unverified (403 seen in sandbox/Codespaces test pending) |
| 2 | HMDA | CODE DONE - live call unverified |
| 2 | WPRDC building permits | CODE DONE - field names inferred, MUST verify against a real response |
| 2 | Yelp | CODE DONE - needs `YELP_API_KEY` |
| 2 | Tier 1 rent / home price / eviction | TODO - no tract-level live API; options: ZIP/county-level (Zillow, FHFA) or bulk Eviction Lab download |
| 2 | Jobs API | TODO - mock only |
| 3 | Grade, 1y/5y appreciation, confidence | DONE (heuristic on opportunity score) |
| 3 | Real median prices | TODO - currently labeled `placeholder_not_live` |
| 4 | Dark card redesign, BLUF views | DONE |
| 3.5 | Researcher signal breakdown + comparables | DONE |
| 3.5 | City planner infrastructure recommendations | DONE |
| 3.5 | Tier 3 (10%) applied in score formula | DONE (v16); legacy mock IDs remapped (v19) |
| 5 | Catalyst detection (Claude API + web search) | TODO |
| 6 | Monte Carlo / scenario modeling | DEFERRED until all Phase 2 data is real |
| 7 | Backtest to 20+ tracts, then consider ML | TODO |
| 8 | Worldwide expansion (city_config pattern) | TODO |

## Deferred: Land-specific scoring (decided: later phase)
Today one score per tract serves land and property; only the Investment
Simulator treats land differently (financing math). A land-specific signal set
would add: zoning changes, vacant-lot share, permit-to-build activity,
buildable square footage. Needs parcel-level sources (assessor / WPRDC zoning
layers), which are harder to source than tract-level APIs. Revisit after Phase 2
data is verified live.

## Known data caveats
- Mock Yelp/Jobs data covers only 9 of 30 neighborhoods; the rest redistribute
  Tier 3's 10% onto Tiers 1 and 2 (shown in `methodology.signal_weights`).
- Mock Yelp/Jobs are calibrated to a fixed reference date (2024-06-01) so
  scores don't drift with the calendar.
- Use `GET /data-sources/{tract_id}` to see which sources are live vs mock.
