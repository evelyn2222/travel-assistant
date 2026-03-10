from datetime import datetime
from typing import Any, List

from app.agents.llm import LLMClient
from app.models.schemas import AgentNote, TripPlan, TripRequest, TripResponse
from app.tools.travel_tools import estimate_costs, get_poi_suggestions, get_weather_hint


class TravelOrchestrator:
    def __init__(self) -> None:
        self.llm = LLMClient()

    def build_trip_plan(self, req: TripRequest) -> TripResponse:
        notes: List[AgentNote] = []

        days = self._trip_days(req.start_date, req.end_date)
        weather_hint = get_weather_hint(req.destination, req.start_date, req.end_date)
        poi = get_poi_suggestions(req.destination, req.interests)
        budget = estimate_costs(days, req.travelers, req.budget_cny)

        planner_output = self._planner_agent(req, days, weather_hint, poi)
        notes.append(AgentNote(agent="planner", summary="已生成基础行程框架与每日主题。"))

        budget_output = self._budget_agent(req, planner_output, budget)
        notes.append(AgentNote(agent="budget", summary="已按预算对行程和消费结构做约束。"))

        guide_output = self._local_guide_agent(req, planner_output, weather_hint, poi)
        notes.append(AgentNote(agent="local-guide", summary="已补充本地交通、错峰和体验建议。"))

        plan = TripPlan(
            overview=planner_output.get("overview", f"{req.destination} {days} 日旅行计划"),
            itinerary=planner_output.get("itinerary", []),
            budget_breakdown=budget_output,
            local_tips=guide_output.get("local_tips", []),
            caveats=guide_output.get("caveats", [weather_hint]),
        )

        return TripResponse(request=req, plan=plan, notes=notes)

    def _planner_agent(
        self,
        req: TripRequest,
        days: int,
        weather_hint: str,
        poi: List[str],
    ) -> dict[str, Any]:
        prompt = (
            "你是旅行规划 Agent。输出 JSON，字段包含 overview 和 itinerary。"
            "itinerary 是数组，每天一个对象，包含 day/date/theme/morning/afternoon/evening。"
            f"用户需求: 出发地={req.origin}, 目的地={req.destination}, 天数={days}, 节奏={req.pace}, 兴趣={req.interests}。"
            f"候选地点={poi}。天气提示={weather_hint}。"
        )
        try:
            return self.llm.json_completion("只输出严格 JSON。", prompt)
        except Exception:
            return self._planner_fallback(req, days, poi)

    def _budget_agent(
        self,
        req: TripRequest,
        planner_output: dict[str, Any],
        budget_estimate: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = (
            "你是预算优化 Agent。基于总预算给出合理分配，并输出 JSON。"
            "字段: total/travelers/per_day/accommodation/transport/food/tickets/misc/optimization_tips。"
            f"总预算={req.budget_cny}，人数={req.travelers}，行程={planner_output.get('overview','')}。"
            f"初始估算={budget_estimate}。"
        )
        try:
            return self.llm.json_completion("只输出严格 JSON。", prompt)
        except Exception:
            budget_estimate["optimization_tips"] = [
                "优先预订可退改酒店，波动期可降低风险。",
                "城市内优先公共交通，减少打车成本。",
                "门票提前 3-7 天预订通常更稳妥。",
            ]
            return budget_estimate

    def _local_guide_agent(
        self,
        req: TripRequest,
        planner_output: dict[str, Any],
        weather_hint: str,
        poi: List[str],
    ) -> dict[str, Any]:
        prompt = (
            "你是本地向导 Agent。输出 JSON，字段 local_tips 和 caveats，均为字符串数组。"
            f"目的地={req.destination}，兴趣={req.interests}，行程概览={planner_output.get('overview', '')}，"
            f"POI={poi}，天气={weather_hint}。"
        )
        try:
            return self.llm.json_completion("只输出严格 JSON。", prompt)
        except Exception:
            return {
                "local_tips": [
                    f"抵达 {req.destination} 后先办交通卡，通勤效率更高。",
                    "热门景点尽量在开门后 1 小时内进入。",
                    "用步行+地铁组合，通常能平衡效率和体验。",
                ],
                "caveats": [
                    weather_hint,
                    "证件与保险文件建议电子版+纸质版双备份。",
                ],
            }

    def _planner_fallback(self, req: TripRequest, days: int, poi: list[str]) -> dict[str, Any]:
        itinerary = []
        for i in range(days):
            itinerary.append(
                {
                    "day": i + 1,
                    "date": f"Day-{i + 1}",
                    "theme": "城市探索",
                    "morning": poi[i % len(poi)] if poi else f"{req.destination} 经典线路",
                    "afternoon": f"{req.destination} 在地美食",
                    "evening": f"{req.destination} 夜游与休闲",
                }
            )
        return {
            "overview": f"{req.destination} {days} 日智能行程",
            "itinerary": itinerary,
        }

    @staticmethod
    def _trip_days(start_date: str, end_date: str) -> int:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        if days <= 0:
            raise ValueError("end_date 必须晚于或等于 start_date")
        return days
