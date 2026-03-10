from typing import Any, List

from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    origin: str = Field(..., description="出发城市")
    destination: str = Field(..., description="目的地")
    start_date: str = Field(..., description="出发日期，格式 YYYY-MM-DD")
    end_date: str = Field(..., description="返回日期，格式 YYYY-MM-DD")
    travelers: int = Field(default=1, ge=1, le=10)
    budget_cny: int = Field(..., ge=100)
    interests: List[str] = Field(default_factory=list)
    pace: str = Field(default="balanced", description="slow|balanced|fast")


class AgentNote(BaseModel):
    agent: str
    summary: str


class TripPlan(BaseModel):
    overview: str
    itinerary: List[dict[str, Any]]
    budget_breakdown: dict[str, Any]
    local_tips: List[str]
    caveats: List[str]


class TripResponse(BaseModel):
    request: TripRequest
    plan: TripPlan
    notes: List[AgentNote]
