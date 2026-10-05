from pydantic import BaseModel
from typing import List, Optional

class PlacementMetric(BaseModel):
    total_eligible: int
    placed_count: int
    placement_rate: float
    average_package_lpa: float
    highest_package_lpa: float

class CompanyStat(BaseModel):
    company_name: str
    students_hired: int
    package_lpa: float

class PredictionTrend(BaseModel):
    year: int
    placement_rate_pct: float
    avg_cgpa: float
    avg_attendance_pct: float

class PredictionResponse(BaseModel):
    historical_trends: List[PredictionTrend]
    projected_next_year_placement_rate: float
    projected_next_year_avg_package: float
    ai_narrative_summary: str
    caveat_disclaimer: str

class AdminDashboardResponse(BaseModel):
    total_students: int
    total_faculty: int
    total_departments: int
    placement_metrics: PlacementMetric
    top_recruiters: List[CompanyStat]
    department_stats: List[dict]
