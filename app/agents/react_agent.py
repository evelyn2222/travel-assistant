import json
import re
import os
import requests
from typing import Any, Dict, List, Callable
from app.tools.travel_tools import get_weather_hint, get_poi_suggestions, estimate_costs


class ReActAgent:
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            "get_weather": self._get_weather,
            "get_poi": self._get_poi,
            "estimate_budget": self._estimate_budget,
        }
        self.tool_descriptions = {
            "get_weather": "获取目的地在指定日期的天气情况和穿衣建议。参数: destination(目的地), start_date(开始日期), end_date(结束日期)",
            "get_poi": "获取目的地的景点和美食推荐。参数: destination(目的地), interests(兴趣列表)",
            "estimate_budget": "估算旅行预算。参数: days(天数), travelers(人数), budget_cny(总预算)",
        }
        self.system_prompt = self._build_system_prompt()
        self.minimax_api_key = os.getenv('MINIMAX_API_KEY', '')

    def _build_system_prompt(self) -> str:
        tools_desc = "\n".join([
            f"- {name}: {desc}" 
            for name, desc in self.tool_descriptions.items()
        ])
        
        return f"""你是旅行规划助手，使用ReAct范式（推理-行动-观察）来帮助用户规划旅行。

可用工具：
{tools_desc}

请按以下格式回答：
思考: [你的推理过程，分析用户需求，决定下一步行动]
工具: [工具名称，如果需要调用工具]
参数: [工具参数，JSON格式，如果需要调用工具]
答案: [最终答案，如果推理完成]

示例：
思考: 用户想去东京旅行，我需要先获取天气信息
工具: get_weather
参数: {{"destination": "东京", "start_date": "2026-05-01", "end_date": "2026-05-05"}}
观察: [工具返回的结果]
思考: 获取到天气信息后，我需要推荐景点
工具: get_poi
参数: {{"destination": "东京", "interests": ["美食", "城市漫步"]}}
观察: [工具返回的结果]
思考: 现在我有足够的信息来生成完整的旅行计划
答案: [最终的旅行计划]

注意：
1. 每次只调用一个工具
2. 工具参数必须是有效的JSON格式
3. 在调用工具前，先进行推理分析
4. 收集足够信息后，给出最终答案
5. 最终答案应该是完整的旅行计划，包括每日行程、预算明细、本地建议等
"""

    def _get_weather(self, destination: str, start_date: str, end_date: str) -> str:
        return get_weather_hint(destination, start_date, end_date)

    def _get_poi(self, destination: str, interests: List[str]) -> str:
        poi_list = get_poi_suggestions(destination, interests)
        return json.dumps(poi_list, ensure_ascii=False)

    def _estimate_budget(self, days: int, travelers: int, budget_cny: int) -> str:
        budget = estimate_costs(days, travelers, budget_cny)
        return json.dumps(budget, ensure_ascii=False)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        result = {
            "thought": "",
            "tool": None,
            "args": None,
            "answer": None
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith("思考:"):
                result["thought"] = line[3:].strip()
            elif line.startswith("工具:"):
                result["tool"] = line[3:].strip()
            elif line.startswith("参数:"):
                args_str = line[3:].strip()
                try:
                    result["args"] = json.loads(args_str)
                except json.JSONDecodeError:
                    result["args"] = {}
            elif line.startswith("答案:"):
                result["answer"] = line[3:].strip()
        
        return result

    def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"错误: 工具 '{tool_name}' 不存在"
        
        try:
            result = self.tools[tool_name](**args)
            return str(result)
        except Exception as e:
            return f"工具调用失败: {str(e)}"

    def _call_minimax_api(self, prompt: str) -> str:
        if not self.minimax_api_key:
            raise RuntimeError("MINIMAX_API_KEY is not set")
        
        url = "https://api.minimaxi.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.minimax_api_key}"
        }
        data = {
            "model": "MiniMax-M2.5",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60, verify=False)
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and result['choices']:
                content = result['choices'][0]['message']['content'].strip()
                if '</think>' in content:
                    content = content.split('</think>')[-1].strip()
                return content
            else:
                return ""
        except Exception as e:
            print(f"MINIMAX API调用失败: {e}")
            return ""

    def run(self, query: str, max_iterations: int = 10) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]
        
        for iteration in range(max_iterations):
            try:
                response = self._call_minimax_api(query)
                response_text = response
                
                if not response_text:
                    return "无法获取API响应"
                
                parsed = self._parse_response(response_text)
                
                if parsed["answer"]:
                    return parsed["answer"]
                
                if parsed["tool"] and parsed["args"]:
                    tool_result = self._call_tool(parsed["tool"], parsed["args"])
                    
                    observation = f"观察: {tool_result}"
                    messages.append({"role": "assistant", "content": f"{response_text}\n{observation}"})
                    query = f"基于以上观察，继续完成旅行规划"
                else:
                    return "无法解析LLM响应，请重试"
                    
            except Exception as e:
                return f"ReAct循环出错: {str(e)}"
        
        return "达到最大迭代次数，未能完成旅行规划"

    def run_with_fallback(self, query: str, max_iterations: int = 10) -> str:
        try:
            return self.run(query, max_iterations)
        except Exception as e:
            print(f"ReAct Agent失败: {e}")
            return "ReAct Agent暂时不可用，请稍后重试"