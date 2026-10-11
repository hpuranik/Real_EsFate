# Urban Intelligence Platform - Setup & Deployment

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 18+
- Mapbox Account (free tier available)

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend runs on: **http://localhost:8000**

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- View methodology: http://localhost:8000/methodology

### Frontend

```bash
cd frontend

# 1. Setup environment
cp .env.local.template .env.local

# 2. Get Mapbox token
# - Visit https://mapbox.com (free account)
# - Copy your access token (starts with pk_)
# - Edit .env.local and paste token

# 3. Install dependencies
npm install

# 4. Start dev server
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 🗺️ First Use: Click the Map

1. Visit http://localhost:3000
2. Map loads with Pittsburgh census tracts
3. Click any colored tract
4. Evidence panel opens showing displacement risk score
5. Switch between Researcher/Resident/Investor/City views
6. See all four views of same data

---

## 📊 Architecture

```
┌─────────────────────────────────────┐
│   Next.js Frontend (TypeScript)     │
│  - Mapbox GL JS for visualization   │
│  - Four stakeholder views           │
│  - Real-time evidence panel         │
└──────────────┬──────────────────────┘
               │ REST API (JSON)
               ↓
┌─────────────────────────────────────┐
│   FastAPI Backend (Python)          │
│  - Deterministic scoring engine     │
│  - Research signal aggregation      │
│  - Caching layer (in-memory)        │
│  - Data validation                  │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│   Signal Services                   │
│  - Tier 1: Research (Zuk et al.)    │
│  - Tier 2: Government (Permits, etc)│
│  - Tier 3: Local (Nextdoor, etc)    │
└─────────────────────────────────────┘
```

---

## 🔌 Environment Variables

### Frontend (.env.local)

```
# API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000

# Mapbox access token (required)
NEXT_PUBLIC_MAPBOX_TOKEN=pk_YOUR_TOKEN_HERE
```

### Backend (.env - optional for Phase 7+)

Currently uses mock data. When real APIs integrated:

```
# Yelp API
YELP_API_KEY=...

# Zillow API
ZILLOW_API_KEY=...

# Database (Phase 7)
DATABASE_URL=postgresql://...
```

---

## 📋 Phases Completed

- ✅ **Phase 1**: Deterministic scoring engine
- ✅ **Phase 2**: Map UI + API integration
- ✅ **Phase 3**: Research signals + prediction layers
- ✅ **Phase 4**: Signal ingestion (Yelp, Jobs services)
- ✅ **Phase 5**: Visualization + stakeholder views
- ✅ **Phase 6**: Caching + validation + explainability
- 🔄 **Phase 7**: Real data integration (next)
- 📅 **Phase 8**: Recalibration + feedback loops
- 📅 **Phase 9**: Production deployment

---

## 🔍 Key Endpoints

### Tracts
- `GET /tracts` - List all Pittsburgh census tracts
- `GET /tract-score/{tract_id}` - Get displacement score for one tract
- `GET /all-tracts` - Get scores for all tracts (for heatmap)

### Signals
- `GET /signals/{tract_id}` - Raw Tier 1/2/3 signals
- `GET /prediction-history/{tract_id}` - Prediction history (for recalibration)

### System
- `GET /health` - System health
- `GET /status` - Detailed system status
- `GET /methodology` - Full research methodology + citations
- `GET /schema` - Data schemas and validation rules

---

## 🎯 Stakeholder Views

Each view uses identical underlying data but changes presentation:

### Researcher View
- Full transparency
- All signal breakdowns
- Confidence intervals
- Research citations
- Methodology details

### Resident View
- Plain language risk level
- Tenant resources & rights
- Actionable recommendations
- Historical context

### Investor View  
- Opportunity score (inverse of risk)
- Market signals
- **Required** disclosure: displacement risk
- Ethical considerations

### City Planner View
- Policy intervention windows
- Early warning signals
- Recommended tools (CLTs, zoning, ordinances)
- Timeline for action

---

## 🧪 Testing

### Manual Testing

1. **Map loads**: Visit http://localhost:3000 - should see Pittsburgh map
2. **Map interaction**: Click a colored tract - evidence panel should appear
3. **View switching**: Click Researcher/Resident/Investor/City tabs
4. **API health**: Visit http://localhost:8000/health - should return `{"status": "healthy"}`

### API Testing (with curl)

```bash
# Get all tracts
curl http://localhost:8000/tracts

# Get score for tract
curl http://localhost:8000/tract-score/42003030100

# Get methodology
curl http://localhost:8000/methodology
```

---

## 📊 Data & Signals

### Current: Mock Data (Phase 6)

All signals currently use realistic mock data:
- **Tier 1**: Rent appreciation, permit surge, eviction uptick, home prices (research-backed)
- **Tier 2**: Yelp business churn, job posting shifts (service-ready)
- **Tier 3**: Nextdoor sentiment, liquor licenses (schema ready)

### Next: Real Data (Phase 7)

Priority integration:
1. Pittsburgh Permits (free, daily updates)
2. Princeton Eviction Lab (free, monthly)
3. FHFA Home Prices (FRED API, free)
4. Zillow Rent Data (paid)
5. Yelp Business Data (paid)

---

## 🔬 Scoring Verification

**Formula** (deterministic, reproducible):
```
Score = (Tier1_avg × 0.60) + (Tier2_avg × 0.30)
Range: 0-100
```

**Color Scale**:
- 🟢 0-40: Low risk (green)
- 🟡 40-60: Medium risk (yellow)
- 🟠 60-80: High risk (orange)
- 🔴 80-100: Critical risk (red)

**Confidence Intervals** (based on Zuk et al. 2018):
- 1-year: 0.82 (permit surge is reliable early signal)
- 3-year: 0.65 (rent trends established)
- 5-year: 0.45 (many confounding factors)

**Key Principle**: No black-box LLM scoring. All values traceable to research and data sources.

---

## 🛠️ Troubleshooting

### "Mapbox token not configured"
- Check that `.env.local` exists in `frontend/` directory
- Verify `NEXT_PUBLIC_MAPBOX_TOKEN` has a valid token (starts with `pk_`)
- Restart frontend dev server: `npm run dev`

### "Map shows blank gray box"
- Ensure Mapbox token is valid
- Check browser console for errors
- Verify network tab shows successful API calls

### "Can't click tracts"
- Confirm backend is running: `curl http://localhost:8000/health`
- Check browser console for API errors
- Verify `NEXT_PUBLIC_API_URL` points to correct backend URL

### "Evidence panel is empty"
- Check that backend returned data: `curl http://localhost:8000/tract-score/42003030100`
- Verify frontend received response in network tab
- Check React component state in DevTools

---

## 📚 Documentation

### Research Citations (Backend)
All signals backed by peer-reviewed research:
- Zuk et al. (2018): Gentrification indicators
- Hwang & Lin (2016): Permit surge signals
- Princeton Eviction Lab: Eviction data
- FHFA: Home price data

See `/methodology` endpoint for full bibliography.

### Architecture Decisions
- **Deterministic Scoring**: All calculations reproducible from inputs
- **Tier-Based Signals**: Separation of ground truth (T1), observed (T2), behavioral (T3)
- **Multi-Stakeholder Views**: Same data, different presentation per user role
- **Research Integrity**: No LLM-generated scores, all sources cited

---

## 🚀 Deployment (Phase 8+)

### Local Docker (Coming)
```bash
docker-compose up
```

### Cloud Deployment (Coming)
- Frontend: Vercel / Netlify
- Backend: Railway / Fly.io / AWS
- Database: PostgreSQL on managed platform

---

## 📞 Support

For issues or questions:
1. Check `/methodology` endpoint for system documentation
2. Review Swagger UI at `http://localhost:8000/docs`
3. Check console for error messages
4. File issue on GitHub with reproduction steps

---

## 📄 License

Academic research use. See LICENSE file for details.

---

**Last Updated**: Phase 6 Complete
**Status**: Ready for Phase 7 (Real Data Integration)
**Estimated Time to Production**: 2-3 weeks
