"""Job posting shifts service.

Ingests job posting data from Indeed, LinkedIn, AngelList.
Extracts location information.
Categorizes industries.
Maps to census tracts.

Phase 4: Mock data based on realistic Pittsburgh trends
Phase 5+: Real Indeed/LinkedIn API integration
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JobPosting:
    job_id: str
    title: str
    company: str
    industry: str  # "tech", "finance", "healthcare", "service", "manufacturing"
    location_tract: str
    posted_date: str
    salary_estimate: float = None


# Mock Pittsburgh job postings (realistic distribution)
MOCK_JOB_POSTINGS = {
    "42003030100": [  # Downtown (finance, tech HQ)
        JobPosting("j1", "Senior Software Engineer", "TechCorp", "tech", "42003030100", "2024-04-01", 145000),
        JobPosting("j2", "Data Analyst", "FinanceCo", "finance", "42003030100", "2024-04-05", 95000),
        JobPosting("j3", "Product Manager", "TechCorp", "tech", "42003030100", "2024-04-08", 155000),
        JobPosting("j4", "Software Engineer", "TechCorp", "tech", "42003030100", "2024-04-10", 140000),
        JobPosting("j5", "Financial Analyst", "FinanceCo", "finance", "42003030100", "2024-04-12", 100000),
    ],
    "42003030200": [  # Strip District (service, retail)
        JobPosting("j6", "Restaurant Manager", "LocalBusiness", "service", "42003030200", "2024-04-01", 45000),
        JobPosting("j7", "Retail Sales", "RetailStore", "service", "42003030200", "2024-04-05", 35000),
    ],
    "42003030300": [  # Lawrenceville (mixed, tech moving in)
        JobPosting("j8", "Software Engineer", "StartupX", "tech", "42003030300", "2024-04-01", 125000),
        JobPosting("j9", "UX Designer", "StartupX", "tech", "42003030300", "2024-04-03", 110000),
        JobPosting("j10", "Restaurant Manager", "LocalBar", "service", "42003030300", "2024-04-02", 48000),
        JobPosting("j11", "Frontend Engineer", "StartupY", "tech", "42003030300", "2024-04-06", 128000),
        JobPosting("j12", "Data Science", "StartupX", "tech", "42003030300", "2024-04-09", 135000),
    ],
    "42003030400": [  # North Shore (mixed, stable)
        JobPosting("j13", "Hotel Manager", "HotelChain", "service", "42003030400", "2024-04-01", 65000),
        JobPosting("j14", "Hospitality Staff", "HotelChain", "service", "42003030400", "2024-04-05", 32000),
    ],
    "42003030500": [  # Hill District (healthcare, service)
        JobPosting("j15", "Healthcare Worker", "Hospital", "healthcare", "42003030500", "2024-04-01", 52000),
        JobPosting("j16", "Community Liaison", "NonProfit", "service", "42003030500", "2024-04-03", 42000),
    ],
    "42003030600": [  # Hazelwood (manufacturing, declining)
        JobPosting("j17", "Factory Worker", "ManufacturingCo", "manufacturing", "42003030600", "2024-01-01", 48000),
    ],
    "42003030700": [  # Southside (emerging, mixed)
        JobPosting("j18", "Software Engineer", "StartupZ", "tech", "42003030700", "2024-04-01", 130000),
        JobPosting("j19", "Service Worker", "LocalBiz", "service", "42003030700", "2024-04-02", 38000),
        JobPosting("j20", "Tech Support", "StartupZ", "tech", "42003030700", "2024-04-05", 65000),
    ],
    "42003030800": [  # Oakland (tech, healthcare, university)
        JobPosting("j21", "University Professor", "University", "healthcare", "42003030800", "2024-04-01", 95000),
        JobPosting("j22", "Research Scientist", "TechLab", "tech", "42003030800", "2024-04-03", 120000),
    ],
    "42003030900": [  # Shadyside (finance, professional)
        JobPosting("j23", "Financial Advisor", "InvestmentFirm", "finance", "42003030900", "2024-04-01", 150000),
        JobPosting("j24", "Attorney", "LawFirm", "finance", "42003030900", "2024-04-05", 140000),
    ],
}


def compute_job_shift(tract_id: str) -> Dict[str, Any]:
    """Compute job posting shift for a tract.
    
    Analyzes:
    - Total job postings
    - Average salary
    - Industry mix (tech growing = gentrification signal)
    
    Returns canonical signal.
    """
    
    if tract_id not in MOCK_JOB_POSTINGS:
        return None
    
    postings = MOCK_JOB_POSTINGS[tract_id]
    now = datetime.now()
    
    # Industry distribution
    industry_counts = {}
    total_salary = 0
    for posting in postings:
        industry_counts[posting.industry] = industry_counts.get(posting.industry, 0) + 1
        if posting.salary_estimate:
            total_salary += posting.salary_estimate
    
    avg_salary = total_salary / len(postings) if postings else 0
    
    # Detect industry shift
    tech_pct = (industry_counts.get("tech", 0) / len(postings) * 100) if postings else 0
    finance_pct = (industry_counts.get("finance", 0) / len(postings) * 100) if postings else 0
    service_pct = (industry_counts.get("service", 0) / len(postings) * 100) if postings else 0
    manufacturing_pct = (industry_counts.get("manufacturing", 0) / len(postings) * 100) if postings else 0
    
    industry_shift = "stable"
    if tech_pct > 40:
        industry_shift = "tech_influx"
    elif finance_pct > 30:
        industry_shift = "finance_concentration"
    elif manufacturing_pct > 30:
        industry_shift = "manufacturing_decline"
    elif service_pct > 50:
        industry_shift = "service_economy"
    
    return {
        "tract_id": tract_id,
        "signal_type": "job_posting_shift",
        "value": tech_pct,  # Tech percentage as primary signal
        "total_postings_12m": len(postings),
        "avg_salary": round(avg_salary, 2),
        "median_salary": sorted([p.salary_estimate for p in postings if p.salary_estimate])[len([p for p in postings if p.salary_estimate])//2] if postings else 0,
        "industry_distribution": industry_counts,
        "industry_shift": industry_shift,
        "tech_percentage": round(tech_pct, 1),
        "finance_percentage": round(finance_pct, 1),
        "service_percentage": round(service_pct, 1),
        "manufacturing_percentage": round(manufacturing_pct, 1),
        "timestamp": now.isoformat(),
        "source": "Job Postings (mock)",
        "confidence": 0.68,
    }


def get_job_signal(tract_id: str) -> Dict[str, Any]:
    """Get job posting shift signal for a tract."""
    return compute_job_shift(tract_id)
