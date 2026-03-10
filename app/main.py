import os
import json
from datetime import datetime
import requests

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

load_dotenv()

app = Flask(__name__, template_folder='web')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def call_minimax_api(prompt):
    """调用MINIMAX API获取智能信息"""
    # 先检查是否有网络连接
    try:
        import socket
        socket.create_connection(('www.baidu.com', 80), timeout=5)
    except:
        print("网络连接失败")
        return ""
    
    # 从环境变量中读取API密钥
    minimax_api_key = os.getenv('MINIMAX_API_KEY', '')
    if not minimax_api_key:
        print("未设置MINIMAX_API_KEY环境变量")
        return ""
    
    # 使用正确的MINIMAX API端点
    url = "https://api.minimaxi.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {minimax_api_key}"
    }
    data = {
        "model": "MiniMax-M2.5",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 2000
    }
    try:
        print(f"调用MINIMAX Coding Plan API，提示词: {prompt[:50]}...")
        print(f"API端点: {url}")
        print(f"API密钥: {headers['Authorization'][:20]}...")
        response = requests.post(url, headers=headers, json=data, timeout=60, verify=False)
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:200]}...")
        response.raise_for_status()
        result = response.json()
        # 检查响应结构
        if 'reply' in result:
            print(f"API返回结果: {result.get('reply', '')[:100]}...")
            return result.get("reply", "").strip()
        elif 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content'].strip()
            # 去除思考过程
            if '<think>' in content:
                content = content.split('</think>')[-1].strip()
            print(f"API返回结果: {content[:100]}...")
            return content
        else:
            print("API响应格式不正确")
            return ""
    except requests.exceptions.Timeout:
        print("MINIMAX API调用超时")
        # 尝试使用备用端点
        return call_minimax_api_backup(prompt)
    except requests.exceptions.RequestException as e:
        print(f"MINIMAX API调用失败: {e}")
        # 尝试使用备用端点
        return call_minimax_api_backup(prompt)
    except Exception as e:
        print(f"其他错误: {e}")
        # 尝试使用备用端点
        return call_minimax_api_backup(prompt)

def call_minimax_api_backup(prompt):
    """使用备用端点调用MINIMAX API"""
    # 从环境变量中读取API密钥
    minimax_api_key = os.getenv('MINIMAX_API_KEY', '')
    if not minimax_api_key:
        print("未设置MINIMAX_API_KEY环境变量")
        return ""
    
    url = "https://api.minimaxi.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {minimax_api_key}"
    }
    data = {
        "model": "MiniMax-M2.5",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 2000
    }
    try:
        print(f"调用MINIMAX备用API，提示词: {prompt[:50]}...")
        print(f"API端点: {url}")
        print(f"API密钥: {headers['Authorization'][:20]}...")
        response = requests.post(url, headers=headers, json=data, timeout=60, verify=False)
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:200]}...")
        response.raise_for_status()
        result = response.json()
        # 检查响应结构
        if 'reply' in result:
            print(f"API返回结果: {result.get('reply', '')[:100]}...")
            return result.get("reply", "").strip()
        elif 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content'].strip()
            # 去除思考过程
            if '<think>' in content:
                content = content.split('</think>')[-1].strip()
            print(f"API返回结果: {content[:100]}...")
            return content
        else:
            print("API响应格式不正确")
            return ""
    except Exception as e:
        print(f"备用API调用失败: {e}")
        return ""


def get_weather_hint(destination, start_date, end_date):
    """示例天气工具。"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
    except ValueError:
        return f"{destination} 天气数据暂不可用，请检查日期格式。"

    # 使用MINIMAX API获取天气信息
    weather_prompt = f"请提供{destination}在{start_date}至{end_date}期间的天气情况，包括平均温度、降水概率和穿衣建议，用简洁的中文回答。"
    weather_info = call_minimax_api(weather_prompt)
    
    if weather_info:
        return f"预计旅行 {days} 天，{destination} {weather_info}"
    else:
        #  fallback到基于月份的判断
        season = "温暖" if start.month in {4, 5, 9, 10} else "偏冷/偏热"
        return f"预计旅行 {days} 天，{destination} 当地体感可能{season}，建议出发前 72 小时复查天气。"


def get_poi_suggestions(destination, interests):
    """智能POI推荐工具，使用MINIMAX API获取城市景点信息，失败时使用内置数据"""
    # 内置的城市景点数据
    specific_pois = {
        "东京": {
            "城市地标": ["东京晴空塔", "东京塔", "明治神宫"],
            "历史街区": ["浅草寺", "银座", "涩谷十字路口"],
            "夜间漫步路线": ["六本木 Hills", "新宿御苑", "台场"],
            "美食": ["筑地市场", "新宿美食街", "浅草小吃街"],
            "城市漫步": ["上野公园", "隅田川沿岸", "代官山"],
            "艺术馆": ["东京国立博物馆", "森美术馆", "东京都美术馆"]
        },
        "上海": {
            "城市地标": ["东方明珠", "外滩", "上海中心大厦"],
            "历史街区": ["豫园", "田子坊", "新天地"],
            "夜间漫步路线": ["外滩夜景", "南京路步行街", "陆家嘴"],
            "美食": ["外滩美食区", "豫园小吃", "新天地餐厅"],
            "城市漫步": ["外滩滨江", "衡山路", "武康路"],
            "艺术馆": ["上海博物馆", "龙美术馆", "上海当代艺术博物馆"]
        },
        "北京": {
            "城市地标": ["故宫", "天安门", "长城"],
            "历史街区": ["南锣鼓巷", "什刹海", "前门大街"],
            "夜间漫步路线": ["王府井", "三里屯", "簋街"],
            "美食": ["王府井小吃街", "簋街", "前门美食"],
            "城市漫步": ["颐和园", "圆明园", "奥林匹克公园"],
            "艺术馆": ["中国国家博物馆", "故宫博物院", "798艺术区"]
        },
        "南京": {
            "城市地标": ["中山陵", "夫子庙", "玄武湖"],
            "历史街区": ["老门东", "总统府", "明孝陵"],
            "夜间漫步路线": ["秦淮河夜景", "新街口", "玄武湖公园"],
            "美食": ["夫子庙小吃", "老门东美食街", "南京大排档"],
            "城市漫步": ["玄武湖公园", "紫金山", "雨花台"],
            "艺术馆": ["南京博物院", "六朝博物馆", "江苏省美术馆"]
        },
        "杭州": {
            "城市地标": ["西湖", "灵隐寺", "雷峰塔"],
            "历史街区": ["河坊街", "南宋御街", "西溪湿地"],
            "夜间漫步路线": ["西湖夜景", "钱江新城", "南山路"],
            "美食": ["楼外楼", "知味观", "河坊街小吃"],
            "城市漫步": ["西湖环线", "九溪烟树", "杨公堤"],
            "艺术馆": ["中国美术学院", "浙江美术馆", "杭州博物馆"]
        },
        "成都": {
            "城市地标": ["锦里", "宽窄巷子", "大熊猫繁育研究基地"],
            "历史街区": ["武侯祠", "青羊宫", "杜甫草堂"],
            "夜间漫步路线": ["春熙路", "九眼桥", "太古里"],
            "美食": ["锦里小吃", "宽窄巷子美食", "火锅一条街"],
            "城市漫步": ["浣花溪公园", "成都人民公园", "东郊记忆"],
            "艺术馆": ["四川博物院", "成都博物馆", "U37创意空间"]
        },
        "广州": {
            "城市地标": ["广州塔", "陈家祠", "白云山"],
            "历史街区": ["北京路", "上下九", "沙面"],
            "夜间漫步路线": ["珠江夜游", "北京路步行街", "太古汇"],
            "美食": ["北京路美食", "上下九小吃", "广州早茶"],
            "城市漫步": ["越秀公园", "二沙岛", "滨江路"],
            "艺术馆": ["广东省博物馆", "广州艺术博物院", "红砖厂创意园"]
        },
        "深圳": {
            "城市地标": ["世界之窗", "东部华侨城", "深圳湾公园"],
            "历史街区": ["东门老街", "南头古城", "大鹏所城"],
            "夜间漫步路线": ["深圳湾夜景", "福田中心区", "海岸城"],
            "美食": ["东门小吃", "华强北美食", "潮汕牛肉火锅"],
            "城市漫步": ["深圳湾公园", "莲花山公园", "笔架山公园"],
            "艺术馆": ["关山月美术馆", "何香凝美术馆", "深圳当代艺术与城市规划馆"]
        },
        "西安": {
            "城市地标": ["兵马俑", "大雁塔", "城墙"],
            "历史街区": ["回民街", "永兴坊", "小雁塔"],
            "夜间漫步路线": ["大唐不夜城", "南门夜景", "回民街"],
            "美食": ["回民街小吃", "永兴坊美食", "西安泡馍"],
            "城市漫步": ["曲江池", "大明宫遗址", "汉城湖"],
            "艺术馆": ["陕西历史博物馆", "西安博物院", "秦始皇帝陵博物院"]
        },
        "厦门": {
            "城市地标": ["鼓浪屿", "厦门大学", "南普陀寺"],
            "历史街区": ["中山路步行街", "曾厝垵", "沙坡尾"],
            "夜间漫步路线": ["环岛路夜景", "白鹭洲公园", "海湾公园"],
            "美食": ["中山路美食街", "曾厝垵小吃", "沙坡尾美食"],
            "城市漫步": ["环岛路", "植物园", "白鹭洲公园"],
            "艺术馆": ["厦门博物馆", "鼓浪屿钢琴博物馆", "沙坡尾艺术区"]
        },
        "青岛": {
            "城市地标": ["五四广场", "栈桥", "崂山"],
            "历史街区": ["八大关", "劈柴院", "小鱼山"],
            "夜间漫步路线": ["五四广场夜景", "栈桥夜景", "台东步行街"],
            "美食": ["云霄路美食街", "劈柴院小吃", "啤酒街"],
            "城市漫步": ["滨海步道", "栈桥公园", "中山公园"],
            "艺术馆": ["青岛博物馆", "青岛美术馆", "奥帆博物馆"]
        },
        "大连": {
            "城市地标": ["星海广场", "大连圣亚海洋世界", "金石滩"],
            "历史街区": ["俄罗斯风情街", "中山广场", "老虎滩"],
            "夜间漫步路线": ["星海广场夜景", "东港商务区", "天津街"],
            "美食": ["天津街美食街", "歹街", "海鲜市场"],
            "城市漫步": ["滨海路", "星海公园", "劳动公园"],
            "艺术馆": ["大连博物馆", "大连现代博物馆", "金石滩文化博览广场"]
        }
    }
    
    base = []
    
    # 首先检查是否有内置数据
    if destination in specific_pois:
        # 添加城市地标
        if "城市地标" in specific_pois[destination]:
            base.extend(specific_pois[destination]["城市地标"])
        # 添加历史街区
        if "历史街区" in specific_pois[destination]:
            base.extend(specific_pois[destination]["历史街区"])
        # 添加夜间漫步路线
        if "夜间漫步路线" in specific_pois[destination]:
            base.extend(specific_pois[destination]["夜间漫步路线"])
        # 添加兴趣相关的具体地点
        for interest in interests:
            if interest in specific_pois[destination]:
                base.extend(specific_pois[destination][interest])
    else:
        # 尝试使用MINIMAX API获取景点信息
        poi_prompt = f"请提供{destination}的热门景点，包括城市地标、历史街区、夜间漫步路线等，每个类别至少3个景点，用中文列出。"
        poi_info = call_minimax_api(poi_prompt)
        
        if poi_info:
            # 解析MINIMAX返回的景点信息
            lines = poi_info.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('##') and not line.startswith('#') and not line.startswith('<') and not line.startswith('>') and not line.startswith('**'):
                    # 提取景点名称，去除序号和多余字符
                    if '.' in line:
                        line = line.split('.', 1)[1].strip()
                    if '：' in line:
                        line = line.split('：', 1)[1].strip()
                    if ' ' in line and not ' ' in line.split(' ')[0]:
                        line = line.split(' ', 1)[1].strip()
                    if line and len(line) > 2:
                        base.append(line)
        
        # 即使API返回不完整，也尝试添加一些默认景点
        if not base:
            # 尝试使用更简单的提示词
            simple_poi_prompt = f"请提供{destination}的3个最著名景点，用中文列出。"
            simple_poi_info = call_minimax_api(simple_poi_prompt)
            if simple_poi_info:
                lines = simple_poi_info.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('##') and not line.startswith('#') and not line.startswith('<') and not line.startswith('>') and not line.startswith('**'):
                        if '.' in line:
                            line = line.split('.', 1)[1].strip()
                        if '：' in line:
                            line = line.split('：', 1)[1].strip()
                        if ' ' in line and not ' ' in line.split(' ')[0]:
                            line = line.split(' ', 1)[1].strip()
                        if line and len(line) > 2:
                            base.append(line)
        
        # 如果API调用失败或返回为空，使用通用模板
        if not base:
            base = [
                f"{destination} 城市地标",
                f"{destination} 历史街区",
                f"{destination} 夜间漫步路线",
            ]
            if interests:
                extra = [f"{destination} {tag} 高评分地点" for tag in interests[:3]]
                base.extend(extra)
    
    return base


def estimate_costs(days, travelers, budget_cny):
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
        "optimization_tips": [
            "优先预订可退改酒店，波动期可降低风险。",
            "城市内优先公共交通，减少打车成本。",
            "门票提前 3-7 天预订通常更稳妥。",
        ],
    }


def trip_days(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1
    if days <= 0:
        raise ValueError("end_date 必须晚于或等于 start_date")
    return days


def build_trip_plan(req):
    """简化版旅行计划生成器。"""
    days = trip_days(req['start_date'], req['end_date'])
    weather_hint = get_weather_hint(req['destination'], req['start_date'], req['end_date'])
    poi = get_poi_suggestions(req['destination'], req['interests'])
    budget = estimate_costs(days, req['travelers'], req['budget_cny'])

    # 生成详细的行程
    itinerary = []
    
    # 内置的美食推荐数据
    food_recommendations_data = {
        "东京": ["章鱼小丸子", "拉面", "寿司", "天妇罗", "烤肉", "刺身", "串烧"],
        "上海": ["小笼包", "生煎包", "红烧肉", "葱油拌面", "蟹粉豆腐", "汤包", "白斩鸡"],
        "北京": ["北京烤鸭", "炸酱面", "豆汁", "卤煮火烧", "炒肝", "铜锅涮肉", "门钉肉饼"],
        "南京": ["盐水鸭", "鸭血粉丝汤", "小笼包", "赤豆元宵", "锅贴", "牛肉锅贴", "南京烤鸭"],
        "杭州": ["西湖醋鱼", "东坡肉", "龙井虾仁", "叫花鸡", "杭州小笼包", "油焖春笋", "宋嫂鱼羹"],
        "成都": ["火锅", "串串香", "麻婆豆腐", "担担面", "龙抄手", "三大炮", "钵钵鸡"],
        "广州": ["广式早茶", "烧鹅", "白切鸡", "肠粉", "煲仔饭", "云吞面", "双皮奶"],
        "深圳": ["潮汕牛肉火锅", "烧腊", "肠粉", "虾饺", "烧鹅", "煲仔饭", "椰子鸡"],
        "西安": ["肉夹馍", "凉皮", "羊肉泡馍", "biangbiang面", "油泼面", "臊子面", "葫芦头" ],
        "厦门": ["沙茶面", "烧肉粽", "土笋冻", "海蛎煎", "面线糊", "姜母鸭", "花生汤"],
        "青岛": ["啤酒", "海鲜", "烤肉", "锅贴", "鲅鱼水饺", "蛤蜊", "凉粉"],
        "大连": ["海鲜", "焖子", "烤鱿鱼", "咸鱼饼子", "炒焖子", "大连老菜", "海鲜饺子"]
    }
    
    destination = req['destination']
    food_recommendations = []
    
    # 首先检查是否有内置美食数据
    if destination in food_recommendations_data:
        food_recommendations = food_recommendations_data[destination]
    else:
        # 尝试使用MINIMAX API获取美食信息
        food_prompt = f"请提供{destination}的特色美食，至少7种，用中文列出。"
        food_info = call_minimax_api(food_prompt)
        
        if food_info:
            # 解析MINIMAX返回的美食信息
            lines = food_info.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('##') and not line.startswith('#') and not line.startswith('<') and not line.startswith('>') and not line.startswith('**'):
                    # 提取美食名称，去除序号和多余字符
                    if '.' in line:
                        line = line.split('.', 1)[1].strip()
                    if '：' in line:
                        line = line.split('：', 1)[1].strip()
                    if ' ' in line and not ' ' in line.split(' ')[0]:
                        line = line.split(' ', 1)[1].strip()
                    if line and len(line) > 2:
                        # 只提取美食名称，不包含描述
                        if ' - ' in line:
                            line = line.split(' - ', 1)[0].strip()
                        if '（' in line:
                            line = line.split('（', 1)[0].strip()
                        if '(' in line:
                            line = line.split('(', 1)[0].strip()
                        food_recommendations.append(line)
        
        # 如果API调用失败或返回为空，使用通用模板
        if not food_recommendations:
            food_recommendations = [f"{destination} 当地美食"] * 7
    
    # 创建景点和美食的副本，用于生成行程
    available_pois = poi.copy()
    available_foods = food_recommendations.copy()
    
    # 打乱顺序，增加随机性
    import random
    random.shuffle(available_pois)
    random.shuffle(available_foods)
    
    for i in range(days):
        # 确保有足够的景点可用
        if not available_pois:
            # 如果所有景点都已使用，重新复制并打乱
            available_pois = poi.copy()
            random.shuffle(available_pois)
        
        # 确保有足够的美食可用
        if not available_foods:
            # 如果所有美食都已使用，重新复制并打乱
            available_foods = food_recommendations.copy()
            random.shuffle(available_foods)
        
        # 选择上午的景点
        morning_activity = available_pois.pop(0) if available_pois else f"{req['destination']} 经典线路"
        
        # 选择中午的美食
        noon_food = available_foods.pop(0) if available_foods else f"{destination} 当地美食"
        noon_activity = f"品尝{noon_food}"
        
        # 确保有足够的景点可用
        if not available_pois:
            # 如果所有景点都已使用，重新复制并打乱
            available_pois = poi.copy()
            random.shuffle(available_pois)
        
        # 选择下午的景点
        afternoon_activity = available_pois.pop(0) if available_pois else f"{req['destination']} 经典线路"
        
        # 确保有足够的美食可用
        if not available_foods:
            # 如果所有美食都已使用，重新复制并打乱
            available_foods = food_recommendations.copy()
            random.shuffle(available_foods)
        
        # 选择晚上的美食
        evening_food = available_foods.pop(0) if available_foods else f"{destination} 当地美食"
        evening_activity = f"品尝{evening_food}"
        
        itinerary.append({
            "day": i + 1,
            "date": f"Day-{i + 1}",
            "theme": "城市探索",
            "morning": morning_activity,
            "noon": noon_activity,
            "afternoon": afternoon_activity,
            "evening": evening_activity,
        })

    # 生成自然语言格式的旅行计划
    natural_language_plan = f"# {req['destination']} {days} 日旅行计划\n\n"
    
    # 行程概览
    natural_language_plan += f"## 行程概览\n"
    natural_language_plan += f"从 {req['origin']} 出发，前往 {req['destination']}，旅行时间为 {req['start_date']} 至 {req['end_date']}，共 {days} 天。\n\n"
    
    # 每日行程
    natural_language_plan += f"## 每日行程\n"
    for item in itinerary:
        natural_language_plan += f"### 第 {item['day']} 天\n"
        natural_language_plan += f"上午：{item['morning']}\n"
        natural_language_plan += f"中午：午餐 {item['noon']}\n"
        natural_language_plan += f"下午：{item['afternoon']}\n"
        natural_language_plan += f"晚上：晚餐 {item['evening']}\n\n"
    
    # 预算明细
    natural_language_plan += f"## 预算明细\n"
    natural_language_plan += f"总预算：{budget['total']} 元\n"
    natural_language_plan += f"人均每日：{budget['per_day'] // req['travelers']} 元\n"
    natural_language_plan += f"住宿：{budget['accommodation']} 元\n"
    natural_language_plan += f"交通：{budget['transport']} 元\n"
    natural_language_plan += f"餐饮：{budget['food']} 元\n"
    natural_language_plan += f"门票：{budget['tickets']} 元\n"
    natural_language_plan += f"其他：{budget['misc']} 元\n\n"
    
    # 预算优化建议
    natural_language_plan += f"## 预算优化建议\n"
    for tip in budget['optimization_tips']:
        natural_language_plan += f"- {tip}\n"
    natural_language_plan += "\n"
    
    # 当地提示
    natural_language_plan += f"## 当地提示\n"
    local_tips = [
        f"抵达 {req['destination']} 后先办交通卡，通勤效率更高。",
        "热门景点尽量在开门后 1 小时内进入。",
        "用步行+地铁组合，通常能平衡效率和体验。",
    ]
    for tip in local_tips:
        natural_language_plan += f"- {tip}\n"
    natural_language_plan += "\n"
    
    # 注意事项
    natural_language_plan += f"## 注意事项\n"
    caveats = [
        weather_hint,
        "证件与保险文件建议电子版+纸质版双备份。",
    ]
    for caveat in caveats:
        natural_language_plan += f"- {caveat}\n"
    
    return natural_language_plan


@app.route("/plan-trip", methods=["POST"])
def plan_trip():
    try:
        req = request.json
        if not req:
            return jsonify({"error": "请求体不能为空"}), 400

        # 验证必要字段
        required_fields = ["origin", "destination", "start_date", "end_date", "budget_cny"]
        for field in required_fields:
            if field not in req:
                return jsonify({"error": f"缺少必要字段: {field}"}), 400

        # 设置默认值
        req.setdefault("travelers", 1)
        req.setdefault("interests", [])
        req.setdefault("pace", "balanced")

        result = build_trip_plan(req)
        return result, 200, {"Content-Type": "text/plain; charset=utf-8"}
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"生成失败: {str(e)}"}), 500


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    app.run(host=host, port=port, debug=True)
