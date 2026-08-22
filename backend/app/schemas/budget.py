from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BudgetBase(BaseModel):
    """Base schema for trip budget allocations."""
    transport_cost: float = Field(default=0.0, ge=0.0)
    stay_cost: float = Field(default=0.0, ge=0.0)
    meals_cost: float = Field(default=0.0, ge=0.0)
    misc_cost: float = Field(default=0.0, ge=0.0)
    total_budget_limit: Optional[float] = Field(None, ge=0.0)


class BudgetUpdate(BaseModel):
    """Payload for updating manually configured budget fields."""
    transport_cost: Optional[float] = Field(None, ge=0.0)
    misc_cost: Optional[float] = Field(None, ge=0.0)
    total_budget_limit: Optional[float] = Field(None, ge=0.0)


class BudgetOut(BudgetBase):
    """Budget database record response."""
    id: str
    trip_id: str

    model_config = ConfigDict(from_attributes=True)


class CostBreakdownOut(BaseModel):
    """Detailed category-level cost breakdown."""
    stay_cost: float
    activities_cost: float
    meals_cost: float
    transport_cost: float
    misc_cost: float
    total_cost: float


class PerDayOut(BaseModel):
    """Daily cost and target savings metrics."""
    cost_per_day: float
    savings_needed_per_day: Optional[float] = None


class BudgetStatusOut(BaseModel):
    """Budget limit adherence and balance calculations."""
    total_budget_limit: Optional[float] = None
    is_over_budget: Optional[bool] = None
    budget_overage: Optional[float] = None
    budget_remaining: Optional[float] = None


class StopBreakdownOut(BaseModel):
    """Cost breakdown for a specific destination stop."""
    stop_id: str
    city_name: str
    days: int
    stay_cost: float
    activities_cost: float
    meals_cost: float
    stop_total: float


class CostDistributionPercentOut(BaseModel):
    """Percentage contribution of each category to the total trip cost."""
    stay: float
    activities: float
    meals: float
    transport: float
    misc: float


class BudgetCalculationOut(BaseModel):
    """Comprehensive budget analysis and cost forecast for a trip."""
    trip_id: str
    trip_title: str
    trip_status: Optional[str] = "upcoming"
    total_trip_days: int
    days_until_trip: Optional[int] = None
    cost_breakdown: CostBreakdownOut
    per_day: PerDayOut
    budget_status: BudgetStatusOut
    stop_breakdown: List[StopBreakdownOut] = []
    cost_distribution_percent: CostDistributionPercentOut


class PredictedBudgetOut(BaseModel):
    """Machine learning predicted trip cost."""
    trip_id: str
    predicted_total_cost: float
    features_used: dict
