from datetime import datetime
from typing import List


def get_weather_hint(destination: str, start_date: str, end_date: str) -> str:
    """示例天气工具。生产环境可接 OpenWeather/和风天气 API。"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
    except ValueError:
        return f"{destination} 天气数据暂不可用，请检查日期格式。"

    season = "温暖" if start.month in {4, 5, 9, 10} else "偏冷/偏热"
    return f"预计旅行 {days} 天，{destination} 当地体感可能{season}，建议出发前 72 小时复查天气。"


def get_poi_suggestions(destination: str, interests: List[str]) -> List[str]:
    """示例 POI 工具。生产环境可接地图/本地生活平台。"""
    base = [
        f"{destination} 城市地标",
        f"{destination} 历史街区",
        f"{destination} 夜间漫步路线",
    ]
    if not interests:
        return base
    extra = [f"{destination} {tag} 高评分地点" for tag in interests[:3]]
    return base + extra


def estimate_costs(days: int, travelers: int, budget_cny: int) -> dict:
    """预算估算器。"""
    accommodation = int(budget_cny * 0.35)
    transport = int(budget_cny * 0.25)
    food = int(budget_cny * 0.25)
    tickets = int(budget_cny * 0.1)
    misc = max(0, budget_cny - accommodation - transport - food - tickets)
    per_day = int(budget_cny / max(days, 1))

    return {
        "total": budget_cny,
        "travelers": travelers,
        "per_day": per_day,
        "accommodation": accommodation,
        "transport": transport,
        "food": food,
        "tickets": tickets,
        "misc": misc,
    }
