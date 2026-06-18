# -*- coding: utf-8 -*-
"""
课程顾问谈单模拟训练系统 V3.0
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
app.secret_key = 'talk_v3'
CORS(app)

from flask import send_from_directory
import random, string

# Admin pages
@app.route("/admin")
def admin_page():
    return send_from_directory("templates", "admin.html")

@app.route("/admin/login")
def admin_login_page():
    return send_from_directory("templates", "admin.html")

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# 加载家长角色增强设定
CONFIG_JSON = ''
config_path = os.path.join(os.path.dirname(__file__), '..', 'skills', 'parent-ai-skill', 'config.json')
if os.path.exists(config_path):
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        rp = config_data.get('role_prompt', {})
        # 格式化
        lines = []
        if rp.get('base'):
            lines.append(f"【基础设定】{rp['base']}")
        if rp.get('emotion'):
            for k, v in rp['emotion'].items():
                lines.append(f"【{k}】{v}")
        if rp.get('personality'):
            for k, v in rp['personality'].items():
                lines.append(f"【{k}】{v}")
        if rp.get('human_traits'):
            lines.append("【人性特点】" + "; ".join(rp['human_traits']))
        if rp.get('reply_style'):
            lines.append("【回复风格】" + "; ".join(rp['reply_style']))
        if rp.get('triggers'):
            lines.append("【触发器】" + str(rp['triggers']))
        CONFIG_JSON = "\n".join(lines)
    except: pass

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CASES = {
    "1": {
        "id": "1", "name": "小升初冲刺", "parent": "陈强", "parent_title": "陈强", "avatar": "avatar_chen.jpg",
        "child": "小雨", "child_grade": "六年级", "child_problem": "成绩中等，语文85/数学78/英语82",
        "child_info": {"personality": "有主见，对补习有点抵触，觉得'我不用补，我自己能行'", "problem": "潜力未释放"},
        "parent_info": {"occupation": "个体经营者", "personality": "务实，带审视感", "concerns": ["师资力量", "往年提分案例", "签约保过"], "age": 42},
        "emotion": "带点审视感",
        "case_bg": "课程顾问在校区接待了陈强（小雨爸爸），他之前通过电话咨询过。小雨成绩中等，陈强已经对比了3家机构，带着审视感。小雨跟爸爸一起来，但不太情愿。陈强说'钱不是问题，问题是能不能考上'",
        "products": ["小升初一对一", "小升初精品小组课（5-8人）"],
        "objections": ["孩子不愿意学怎么办", "能保证考上吗", "一对一还是小组课好"],
        "tags": ["小升初", "冲刺"],
        "intro": "【推了推眼镜，在前台扫了一圈】你好，我之前打过电话的，姓陈。（语气带着审视感）先来看看你们这边的课程，能保证考上吗？"
    },
    "2": {
        "id": "2", "name": "初二成绩下滑", "parent": "刘莹", "parent_title": "刘莹", "avatar": "avatar_liu.jpg",
        "child": "小杰", "child_grade": "初二", "child_problem": "数学85→62，物理55，英语80→70",
        "child_info": {"personality": "青春期，有点叛逆，不太愿意跟家长沟通，回家就关房门", "problem": "断崖式下滑"},
        "parent_info": {"occupation": "小学老师", "personality": "职业习惯，会挑刺", "concerns": ["初二'分水岭'到底有多关键", "青春期孩子怎么引导", "物理怎么补"], "age": 38},
        "emotion": "带着老师职业习惯，会问得比较细",
        "case_bg": "刘莹经同班同学家长推荐，瞒着孩子来校区咨询。小杰初二断崖式下滑，数学85→62，物理55，英语80→70。青春期叛逆，回家就关房门。刘莹是小学老师，对教学方法会挑刺，之前上过辅导班但效果不好。",
        "products": ["初中一对一", "初中精品小组课（5-8人）"],
        "objections": ["之前补过没用", "孩子不愿意补", "一对一能管住青春期孩子吗"],
        "tags": ["初二", "成绩下滑"],
        "intro": "【微微皱眉，把包里的一沓试卷放在桌上】你好，我是朋友推荐来的。（语气带着焦虑）我家孩子初二了，成绩下滑得厉害，特别是数学和物理，您给看看怎么回事？"
    },
    "3": {
        "id": "3", "name": "初三距离目标甚远", "parent": "赵明", "parent_title": "赵明", "avatar": "avatar_zhao.jpg",
        "child": "小豪", "child_grade": "初三", "child_problem": "距目标高中差80分，数学90/英语75",
        "child_info": {"personality": "比较贪玩，但最近开始慌了，知道要中考了", "problem": "目标差距大"},
        "parent_info": {"occupation": "工程师", "personality": "喜欢算投入产出比", "concerns": ["剩下时间还够不够", "要不要全日制冲刺", "全日制到底是什么模式"], "age": 45},
        "emotion": "既焦虑又纠结",
        "case_bg": "赵明在期末考后带孩子来咨询，小豪主动说要补课。小豪距目标高中差80分左右，数学90/150，英语75/150。初中三年没补过课，对全日制模式完全不了解。时间只剩不到半年。赵明是工程师，喜欢算投入产出比。",
        "products": ["中考全日制冲刺", "中考一对一", "中考精品小组课（5-8人）"],
        "objections": ["时间够不够", "全日制跟学校怎么协调", "价格贵不贵"],
        "tags": ["初三", "全日制"],
        "intro": "【轻轻叹了口气，在沙发上缓缓坐下】你好，孩子初三了，想考一中。（表情既焦虑又纠结）还有半年时间，您说有希望吗？"
    },
    "4": {
        "id": "4", "name": "中考失利复读", "parent": "周强", "parent_title": "周强", "avatar": "avatar_zhou.jpg",
        "child": "小峰", "child_grade": "初三刚毕业", "child_problem": "离普高线差25分",
        "child_info": {"personality": "这次失利后受了打击，比之前沉默了，偶尔会说'早知道就认真点'", "problem": "中考失利"},
        "parent_info": {"occupation": "公务员", "personality": "沉重但带希望", "concerns": ["复读班师资怎么样", "管理严不严", "提分效果如何"], "age": 44},
        "emotion": "沉重但带着一丝希望",
        "case_bg": "周强打听到复读项目，带孩子一起来咨询。小峰中考离普高线差25分，数学英语各差10分左右。孩子受打击后偶尔会说'��知道就认真点'。之前补过两个月一对一，效果一般。最怕'万一又考不上'。",
        "products": ["中考复读10人精品小组课"],
        "objections": ["复读真的能提分吗", "复读班和学校有什么区别", "孩子心理能承受吗"],
        "tags": ["中考", "复读"],
        "intro": "【牵着孩子的手，眼神里透着疲惫和希望】你好，孩子中考没考好。（声音有些沉重）这是孩子的成绩，您给看看有没有办法？"
    },
    "5": {
        "id": "5", "name": "高二数学方法不对", "parent": "林芳", "parent_title": "林芳", "avatar": "avatar_lin.jpg",
        "child": "小琳", "child_grade": "高二", "child_problem": "数学85-95/150徘徊",
        "child_info": {"personality": "自觉努力，不偷懒，但方法不太对，孩子自己也很挫败", "problem": "方法不对"},
        "parent_info": {"occupation": "家庭主妇", "personality": "心疼孩子又着急", "concerns": ["需要真正能帮孩子找到方法的老师", "而不是再刷题"], "age": 40},
        "emotion": "心疼孩子又着急",
        "case_bg": "林芳在学校老师建议下，自己来校区咨询数学辅导。小琳数学长期85-95/150徘徊，刷题不少但上不去100。文科选科，英语120/语文110不差。孩子很努力刷题到半夜，方法不对。对'方法不对'这个说法很敏感。",
        "products": ["高中一对一", "高中精品小组课（5-8人）"],
        "objections": ["刷题都不行，一对一真的能解决吗", "找不到方法怎么办", "怕耽误孩子时间"],
        "tags": ["高二", "数学"],
        "intro": "【眼眶微微发红，声音里带着心疼】你好，孩子高二了，数学一直上不去。（轻轻叹气）每天刷题到半夜，可就是不见效果，您给想想办法？"
    },
    "6": {
        "id": "6", "name": "高三数物化不理想", "parent": "王东", "parent_title": "王东", "avatar": "avatar_wang.jpg",
        "child": "小宇", "child_grade": "高三", "child_problem": "数学105/物理65/化学70",
        "child_info": {"personality": "比较成熟，知道自己要什么，但压力大容易焦虑，睡眠不太好", "problem": "数理化不理想"},
        "parent_info": {"occupation": "医生", "personality": "专业要求高", "concerns": ["物理化学能不能短期提分", "怎么平衡各科时间", "模考后怎么调整策略"], "age": 46},
        "emotion": "紧迫感很强",
        "case_bg": "王东一模成绩出来后直接来校区咨询。小宇总分520-540/750徘徊，目标冲特控线稳一本。数学105/150，物理65/100，化学70/100。高二下开始补数学有进步（85→105），物理化学没补过。紧迫感极强，说不到点子上直接走人。",
        "products": ["高考一对一", "高考精品小组课（5-8人）"],
        "objections": ["还有半年来得及吗", "数理化三科都补孩子撑得住吗", "能保证提多少"],
        "tags": ["高三", "特控线"],
        "intro": "【站姿有些僵硬，紧抿着嘴唇】你好，孩子高三了。（语气很急促）一模刚出来，各科都不理想，您给分析分析？"
    },
    "7": {
        "id": "7", "name": "高考失利复读", "parent": "李丹", "parent_title": "李丹", "avatar": "avatar_lidan.jpg",
        "child": "小松", "child_grade": "高三刚毕业", "child_problem": "高考435，离本科线差12分",
        "child_info": {"personality": "比较成熟，知道自己要什么，受打击后说'我想再来一年'", "problem": "高考失利"},
        "parent_info": {"occupation": "公务员", "personality": "理性带数据", "concerns": ["复读班的师资", "管理强度", "往年提分数据", "是否签约"], "age": 45},
        "emotion": "比较理性，带着数据和问题来",
        "case_bg": "李丹出分后带孩子来咨询，孩子态度很坚决要复读。小松高考435，离本科线差12分，平时模考450-470。孩子自己说要复读，态度坚决。理综崩了，数学英语是平时水平。要看到硬核证据才信，带着数据和问题来的。",
        "products": ["高考复读10人精品小组课"],
        "objections": ["复读一年压力更大扛不扛得住", "明年政策有没有变化", "能提多少分"],
        "tags": ["高考", "复读"],
        "intro": "你好，我想了解一下高考复读班。"
    },
    "8": {
        "id": "8", "name": "五年级小升初", "parent": "战勇", "parent_title": "战勇", "avatar": "avatar_zhan.jpg",
        "child": "小浩", "child_grade": "五年级下学期", "child_problem": "距目标初中差15分左右，数学85/英语88/语文92",
        "child_info": {"personality": "贪玩好动，但最近开始慌了，知道要小升初了", "problem": "目标差距中等"},
        "parent_info": {"occupation": "工程师", "personality": "理性但着急", "concerns": ["剩下时间还够不够", "要不要补课冲刺", "冲刺到底是什么模式"], "age": 35},
        "emotion": "有些着急但理性",
        "case_bg": "战勇在期末考后带孩子来咨询，小浩主动说要补课。小浩距目标初中差15分左右，数学85/英语88/语文92。五年级前没补过课，对模式完全不了解。时间只剩不到一年。",
        "products": ["小升初同步冲刺", "小升初一对一", "小升初精品小组课（5-8人）"],
        "objections": ["时间够不够", "全日制跟学校怎么协调", "价格贵不贵"],
        "tags": ["五年级", "小升初", "冲刺"],
        "intro": "【微微皱眉，把孩子成绩单放在桌上】你好，孩子五年级了，想考目标初中。（表情有些着急）还有一年时间，您说有希望吗？"
    }
}

CARDS_FILE = os.path.join(DATA_DIR, 'cards.json')
USAGES_FILE = os.path.join(DATA_DIR, 'usages.json')

def init_cards():
    cards = load_json(CARDS_FILE, {})
    if not cards:
        cards = {"VIP-UNLIMITED": {"type": "畅练卡", "usages": -1, "status": "active"}, "TIYAN-50EF89": {"type": "体验卡", "usages": 10, "status": "active"}, "CHANGLIAN-50EF89": {"type": "畅练卡", "usages": 80, "status": "active"}}
        save_json(CARDS_FILE, cards)
    return cards

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cases')
def get_cases():
    return jsonify({"cases": list(CASES.values())})

@app.route('/api/case/<case_id>')
def get_case(case_id):
    case = CASES.get(case_id)
    return jsonify(case) if case else jsonify({"error": "不存在"}), 404

@app.route('/api/activate', methods=['POST'])
def activate():
    data = request.json
    card = data.get('card', '').strip().upper()
    cards = init_cards()
    card_data = cards.get(card)
    if not card_data or card_data.get('status') != 'active':
        return jsonify({"success": False, "error": "卡密无效"}), 400
    usages = card_data.get('usages', 0)
    usages_data = load_json(USAGES_FILE, {})
    remaining = usages_data.get(card, usages) if usages != -1 else -1
    if usages == -1:
        remaining = -1
    elif remaining <= 0:
        return jsonify({"success": False, "error": "训练次数已用完"}), 400
    return jsonify({"success": True, "remaining": remaining, "card_type": card_data.get('type')})
def build_prompt(case, conversation):
    parent, parent_title = case["parent"], case["parent_title"]
    child, child_grade = case["child"], case["child_grade"]
    parent_info = case.get("parent_info", {})
    child_info = case.get("child_info", {})
    
    # 获取对话历史（不带角色标签）
    dialog = ""
    for m in conversation:
        if m.get("role") == "parent":
            # 家长的话直接显示，不加标签
            dialog += m.get("content", "") + "\n"
        else:
            # 课程顾问的话不加标签
            dialog += m.get("content", "") + "\n"
    
    # 家长历史（避免重复）
    parent_history = [m.get("content", "") for m in conversation if m.get("role") == "parent"]
    last_3_parent = parent_history[-3:] if len(parent_history) >= 3 else parent_history
    
    prompt = f"""【角色扮演】
你是{parent_title}，一位真实的家长来咨询课程。

【家长背景】
- 孩子：{child}（{child_grade}）
- 问题：{child_info.get("problem", "")}
- 目标：{child_info.get("goal", "")}
- 性格：{parent_info.get("personality", "")}
- 职业：{parent_info.get("occupation", "")}
- 顾虑：{parent_info.get("concerns", "")}

【对话历史】
{dialog}

【说话风格】
你是一位真实的家长，会：
1. 用表情和动作描述：如（皱眉头）、（叹气）、（点头）等
2. 追问细节：如"真的吗？"、"那怎么收费？"、"老师怎么样？"
3. 表达疑虑：如"我还是担心..."、"能保证效果吗？"
4. 根据课程顾问的回答自然回应
5. 每次回复都要有变化，不要重复同样的话

【禁止】
- 不要说同样的话
- 不要一次发多条消息
- 不要替课程顾问回答问题

请用自然的家长语气回复，加上表情动作："""

    return prompt
def call_ai(prompt):
    import requests
    api_key = "sk-cp-DY6GzYTlfR7hmmSmTJeqfAGa7SIrzxBy1H6sSXYwKpgfxPzH5BLuhm98R2aQdlbH-Xk8qq6LXMVFm8mhMIkxJBegenQB9wI8yjU65XRoABTh5a8zwsPh6xQ"
    url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"model": "abab6.5s-chat", "max_tokens": 400, "temperature": 0.8, "messages": [{"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except:
        pass
    return "（思考了一下）你说得对，让我再想想。"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    case_id, user_message = data.get('case_id'), data.get('message')
    conversation = data.get('conversation', [])
    case = CASES.get(case_id)
    if not case:
        return jsonify({"error": "案例不存在"}), 404
    conversation.append({"role": "consultant", "content": user_message})
    ai_response = call_ai(build_prompt(case, conversation))
    conversation.append({"role": "parent", "content": ai_response})
    return jsonify({"response": ai_response, "case_id": case_id, "conversation": conversation})



@app.route('/api/coach_hint', methods=['POST'])
def coach_hint():
    data = request.json
    case_id, conversation = data.get('case_id'), data.get('conversation', [])
    case = CASES.get(case_id)
    if not case:
        return jsonify({"error": "案例不存在"}), 404
    
    # 获取家长最后一条消息
    parent_msgs = [m.get('content', '') for m in conversation if m.get('role') == 'parent']
    latest_parent_msg = parent_msgs[-1] if parent_msgs else ""
    
    if not latest_parent_msg:
        return jsonify({"hint": "暂无家长消息可分析"})
    
    ai_prompt = f"""作为一位专业的销售培训教练，请对家长的这句话进行快速分析，给出销售建议。

【家长最后一句话】
{latest_parent_msg}

【请按以下格式回复，注意用**加粗标题**，保持结构清晰】

🎯 销售教练建议

1. **当前状态判断**：天龙八步第几步？五步共识第几步？
2. **家长情绪判断**：家长的情绪和意图是什么？
3. **话术建议**：接下来课程顾问应该怎么回复？请给出具体话术。
4. **下一步提醒**：接下来应该收集什么信息？

请用简洁专业的语言回复。"""

    import requests
    try:
        api_key = "sk-cp-DY6GzYTlfR7hmmSmTJeqfAGa7SIrzxBy1H6sSXYwKpgfxPzH5BLuhm98R2aQdlbH-Xk8qq6LXMVFm8mhMIkxJBegenQB9wI8yjU65XRoABTh5a8zwsPh6xQ"
        url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload = {"model": "abab6.5s-chat", "max_tokens": 400, "temperature": 0.85, "messages": [{"role": "user", "content": ai_prompt}]}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            hint = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            hint = "AI分析暂时不可用"
    except Exception as e:
        hint = f"AI分析服务暂时不可用"
    
    return jsonify({"hint": hint})


@app.route('/api/coach', methods=['POST'])
def coach():
    data = request.json
    case_id, conversation = data.get('case_id'), data.get('conversation', [])
    case = CASES.get(case_id)
    if not case:
        return jsonify({"error": "案例不存在"}), 404
    
    # 提取对话历史
    consultant_msgs = [m.get('content', '') for m in conversation if m.get('role') == 'consultant']
    parent_msgs = [m.get('content', '') for m in conversation if m.get('role') == 'parent']
    
    # 构建AI分析Prompt - 按对话顺序展示（不带角色标签）
    dialog_history = ""
    for m in conversation:
        dialog_history += m.get('content', '') + "\n"
    
    ai_prompt = f"""作为一位专业的销售培训教练，请对这段模拟谈单对话进行详细、客观的点评。

【案例】{case['name']} - {case['parent_title']}咨询{case['child']}({case['child_grade']})
【孩子问题】{case['child_info']['problem']}
【家长职业】{case['parent_info'].get('occupation', '')}
【家长性格】{case['parent_info'].get('personality', '')}

【对话历史】
{dialog_history}

=== 点评模板 ===

【总评】X/100分

【一句话总结】对这段对话的整体评价

---

1. 流程完整性 (30分)
- ①破冰 (X/5): [评分+简评]
- ②信息收集 (X/5): [评分+简评]
- ③需求分析 (X/5): [评分+简评]
- ④下危机 (X/5): [评分+简评]
- ⑤产品介绍 (X/5): [评分+简评]
- ⑥方案设计 (X/5): [评分+简评]
- ⑦异议处理 (X/5): [评分+简评]
- ⑧逼单关单 (X/5): [评分+简评]
跳步检查: [有/无]


2. 共识达成度 (25分)
- 现状共识 (X/10): [评分+简评]
- 目标共识 (X/5): [评分+简评]
- 必要共识 (X/5): [评分+简评]
- 方案共识 (X/5): [评分+简评]


3. 三性检验 (25分)
- 必要性塑造 (X/10): [评分+简评]
- 紧迫性塑造 (X/8): [评分+简评]
- 唯一性塑造 (X/7): [评分+简评]


4. 异议处理能力 (20分)
[针对实际对话中出现的异议，使用"接化发"原则逐个点评]


做得好的:
1. [具体亮点1]
2. [具体亮点2]


需要改进的:
1. [具体建议1]
2. [具体建议2]


建议:
1. [改进建议1]
2. [改进建议2]


总结: [对本次谈单的整体总结和后续提升建议]

=== 输出要求 ===
请严格按照上述模板格式输出，基于对话实际内容进行客观评分。每个环节都要给出具体分数和评分理由。

评分标准（严格评分）：
严格按照实际完成情况评分，没有做到就没有分。每个环节根据实际表现给分，不要因为"希望"给高分。

注意：只描述实际完成情况，不添加主观评价词。

请开始输出点评报告："""
    
    # 调用AI分析
    import requests
    try:
        api_key = "sk-cp-DY6GzYTlfR7hmmSmTJeqfAGa7SIrzxBy1H6sSXYwKpgfxPzH5BLuhm98R2aQdlbH-Xk8qq6LXMVFm8mhMIkxJBegenQB9wI8yjU65XRoABTh5a8zwsPh6xQ"
        url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload = {"model": "abab6.5s-chat", "max_tokens": 1500, "messages": [{"role": "user", "content": ai_prompt}]}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            advice = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            advice = "AI分析暂时不可用，请检查API配置"
    except Exception as e:
        advice = f"AI分析服务暂时不可用: {str(e)}"
    
    return jsonify({"advice": advice})
    


# ========== 管理后台API ==========
@app.route('/api/admin/create_card', methods=['POST'])
def admin_create_card():
    data = request.json
    card_type = data.get('type', '体验卡')
    count = data.get('count', 1)
    
    cards = load_json(CARDS_FILE, {})
    usages_data = load_json(USAGES_FILE, {})
    
    if card_type == '体验卡':
        prefix = 'TIYAN-'
        usages = 10
    else:
        prefix = 'CHANGLIAN-'
        usages = 80
    
    created = []
    for i in range(count):
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        card = prefix + suffix
        cards[card] = {'type': card_type, 'usages': usages, 'status': 'active'}
        usages_data[card] = usages
        created.append(card)
    
    save_json(CARDS_FILE, cards)
    save_json(USAGES_FILE, usages_data)
    
    return jsonify({'success': True, 'cards': created})

@app.route('/api/admin/cards', methods=['GET'])
def admin_get_cards():
    cards = load_json(CARDS_FILE, {})
    usages_data = load_json(USAGES_FILE, {})
    
    card_list = []
    for card, info in cards.items():
        remaining = usages_data.get(card, info.get('usages', 0))
        card_list.append({
            'card': card,
            'type': info.get('type', ''),
            'usages': info.get('usages', 0),
            'remaining': remaining,
            'status': info.get('status', 'active')
        })
    
    return jsonify({'cards': card_list})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    cards = load_json(CARDS_FILE, {})
    usages_data = load_json(USAGES_FILE, {})
    
    total_cards = len(cards)
    active_cards = sum(1 for c in cards.values() if c.get('status') == 'active')
    
    total_used = 0
    for card, usage in usages_data.items():
        if usage >= 0 and card in cards:
            initial = cards[card].get('usages', 0)
            if initial > 0:
                total_used += (initial - usage)
    
    tiyan_count = sum(1 for c in cards.values() if c.get('type') == '体验卡')
    changlian_count = sum(1 for c in cards.values() if c.get('type') == '畅练卡')
    
    return jsonify({
        'total_cards': total_cards,
        'active_cards': active_cards,
        'total_used': total_used,
        'tiyan_count': tiyan_count,
        'changlian_count': changlian_count
    })

@app.route('/api/admin/usage_records', methods=['GET'])
def admin_usage_records():
    cards = load_json(CARDS_FILE, {})
    usages_data = load_json(USAGES_FILE, {})
    
    records = []
    for card, info in cards.items():
        initial = info.get('usages', 0)
        remaining = usages_data.get(card, initial)
        used = initial - remaining if (initial > 0 and remaining >= 0) else 0
        
        records.append({
            'card': card,
            'type': info.get('type', ''),
            'initial': initial,
            'remaining': remaining,
            'used': used,
            'status': info.get('status', 'active')
        })
    
    return jsonify({'records': records})
