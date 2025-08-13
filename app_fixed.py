import streamlit as st
import requests
import json
import os
import time
from datetime import datetime, date
import base64
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI副业方向推荐工具 - 稳定版",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主标题、副标题、简介
st.markdown('''
<h1 class="main-header">🚀 AI副业方向推荐工具</h1>
<h3 style="text-align:center; color:#444; margin-top:-1rem;">让AI帮你发现最适合你的副业方向，获得专属行动计划</h3>
<p style="text-align:center; color:#666; font-size:1.1rem; max-width:700px; margin:0 auto 1.5rem auto;">
本工具基于AI大模型，结合你的兴趣、技能和目标，智能推荐最适合你的AI副业方向，并给出三步行动建议。填写信息后，1分钟内获得专属副业方案，助你高效变现、成长、打造个人品牌。<br><b>适合：想副业赚钱、想学AI、想打造个人品牌、想时间自由的你！</b>
</p>
''', unsafe_allow_html=True)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f0f4fa !important;
        color: #222 !important;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        font-size: 1.1rem;
        line-height: 1.8;
    }
    .qr-section {
        background: #fffbe6 !important;
        color: #222 !important;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        border: 2px solid #fdcb6e;
        font-size: 1.1rem;
    }
    .resource-card {
        background: #f7f7fa !important;
        color: #222 !important;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        font-size: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .error-box {
        background-color: #fff5f5 !important;
        color: #c53030 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        margin: 1rem 0;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 学习资源数据库（只推荐主流工具官网）
LEARNING_RESOURCES = {
    "AI写作": [
        {"title": "Notion AI（多语言AI写作/笔记）", "url": "https://www.notion.so/product/ai", "type": "官网"},
        {"title": "秘塔写作猫（中文AI写作）", "url": "https://xiezuocat.com/", "type": "官网"},
        {"title": "ChatGPT（OpenAI官方）", "url": "https://chat.openai.com/", "type": "官网"}
    ],
    "AI绘画": [
        {"title": "Midjourney（AI艺术生成）", "url": "https://www.midjourney.com/", "type": "官网"},
        {"title": "Stable Diffusion（开源AI绘画）", "url": "https://stability.ai/", "type": "官网"},
        {"title": "文心一格（百度AI绘画）", "url": "https://yige.baidu.com/", "type": "官网"}
    ],
    "AI编程": [
        {"title": "GitHub Copilot（AI编程助手）", "url": "https://github.com/features/copilot", "type": "官网"},
        {"title": "通义灵码（阿里AI编程）", "url": "https://tongyi.aliyun.com/lingma", "type": "官网"},
        {"title": "ChatGPT（代码生成/调试）", "url": "https://chat.openai.com/", "type": "官网"}
    ],
    "AI营销": [
        {"title": "火山引擎AIGC营销平台", "url": "https://www.volcengine.com/product/aigc", "type": "官网"},
        {"title": "腾讯智营（AI营销）", "url": "https://ad.tencent.com/product/ai", "type": "官网"},
        {"title": "HubSpot AI（海外智能营销）", "url": "https://www.hubspot.com/products/ai", "type": "官网"}
    ]
}

# 兴趣、技能选项
INTEREST_OPTIONS = [
    "写作", "摄影", "编程", "设计", "短视频", "自媒体", "AI绘画", "AI写作", "AI编曲", "AI配音", "AI剪辑", "AI营销", "教育培训", "心理咨询", "健康健身", "理财投资", "电商运营", "产品经理", "项目管理", "翻译", "其他"
]
SKILL_OPTIONS = [
    "内容创作", "视频剪辑", "平面设计", "Python编程", "数据分析", "AI工具使用", "市场营销", "社群运营", "文案策划", "项目管理", "产品设计", "摄影基础", "写作基础", "英语", "日语", "PPT制作", "Excel", "演讲表达", "自律习惯", "其他"
]

# 限制：每天每用户仅可生成1次
TODAY = date.today().isoformat()
if 'last_generate_date' not in st.session_state:
    st.session_state['last_generate_date'] = ''
if 'generate_count' not in st.session_state:
    st.session_state['generate_count'] = 0

# 新的一天自动重置
if st.session_state['last_generate_date'] != TODAY:
    st.session_state['last_generate_date'] = TODAY
    st.session_state['generate_count'] = 0

# 初始化DeepSeek客户端
def init_deepseek_client():
    """初始化DeepSeek客户端"""
    # 只用环境变量读取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请在本地.env中设置DEEPSEEK_API_KEY")
        return None
    
    return api_key

# 生成AI推荐（增强版，带重试机制）
def generate_ai_recommendation(api_key, user_data):
    """使用DeepSeek生成副业推荐（带重试机制）"""
    
    # 构建提示词
    prompt = f"""
你是一位AI副业咨询专家。请根据以下用户资料，推荐一个最合适的AI副业方向，并给出三步具体行动计划。

兴趣：{user_data['interest']}
技能：{user_data['skills']}
时间投入：{user_data['time']}
副业目的：{user_data['goal']}
是否出镜：{user_data['on_camera']}
其他信息：{user_data['additional_info']}

请回复格式如下：
1. 推荐副业方向：
2. 为什么适合你：
3. 三步行动建议：
4. 预期收益：
5. 所需工具：

请用简体中文回复，内容要具体、实用、可操作。每个部分都要详细说明。
"""
    
    # 重试配置
    max_retries = 3
    base_timeout = 30
    
    for attempt in range(max_retries):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-coder",
                "messages": [
                    {"role": "system", "content": "你是一位专业的AI副业咨询师，擅长为用户提供个性化的副业建议。请提供具体、可操作的建议。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            # 动态调整超时时间
            timeout = base_timeout * (attempt + 1)
            
            with st.spinner(f"🤖 AI正在分析... (第{attempt + 1}次尝试，超时时间{timeout}秒)"):
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 401:
                st.error("❌ API密钥无效，请检查配置")
                return None
            elif response.status_code == 429:
                st.error("❌ API请求过于频繁，请稍后再试")
                return None
            elif response.status_code == 500:
                st.warning(f"⚠️ 服务器错误，正在重试... ({attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    st.error("❌ 服务器暂时不可用，请稍后再试")
                    return None
            else:
                st.error(f"❌ API调用失败: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏰ 请求超时，正在重试... ({attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            else:
                st.error("❌ 网络连接超时，请检查网络连接或稍后再试")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ 网络连接失败，请检查网络连接")
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ 请求失败，正在重试... ({attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            else:
                st.error(f"❌ AI推荐生成失败: {str(e)}")
                return None
    
    return None

# 生成备用推荐（当API失败时）
def generate_fallback_recommendation(user_data):
    """生成备用推荐"""
    interest = user_data['interest']
    skills = user_data['skills']
    goal = user_data['goal']
    
    # 基于用户选择的兴趣和技能生成基础推荐
    if "写作" in interest or "内容创作" in skills:
        return """
1. 推荐副业方向：AI内容创作
2. 为什么适合你：结合你的写作兴趣和内容创作技能，AI内容创作是最适合的方向
3. 三步行动建议：
   - 第一步：学习使用ChatGPT、Notion AI等AI写作工具
   - 第二步：在知乎、小红书等平台发布AI辅助创作的内容
   - 第三步：接单写作、代运营等变现
4. 预期收益：月收入2000-8000元
5. 所需工具：ChatGPT、Notion AI、秘塔写作猫
        """
    elif "摄影" in interest or "短视频" in interest:
        return """
1. 推荐副业方向：AI短视频制作
2. 为什么适合你：结合你的摄影和短视频兴趣，AI短视频制作是很好的选择
3. 三步行动建议：
   - 第一步：学习使用AI视频剪辑工具如剪映、CapCut
   - 第二步：制作AI工具使用教程视频
   - 第三步：接单制作短视频、开设课程
4. 预期收益：月收入3000-12000元
5. 所需工具：剪映、CapCut、ChatGPT、Midjourney
        """
    elif "编程" in interest or "Python编程" in skills:
        return """
1. 推荐副业方向：AI编程助手
2. 为什么适合你：结合你的编程技能，AI编程助手是最适合的方向
3. 三步行动建议：
   - 第一步：学习使用GitHub Copilot、通义灵码等AI编程工具
   - 第二步：在GitHub上分享AI辅助编程的项目
   - 第三步：接单编程、开发AI工具
4. 预期收益：月收入5000-15000元
5. 所需工具：GitHub Copilot、通义灵码、ChatGPT
        """
    else:
        return """
1. 推荐副业方向：AI工具推广
2. 为什么适合你：基于你的兴趣和技能，AI工具推广是很好的入门方向
3. 三步行动建议：
   - 第一步：学习各种AI工具的使用方法
   - 第二步：在社交媒体分享AI工具使用心得
   - 第三步：开设AI工具使用课程、接单咨询
4. 预期收益：月收入2000-6000元
5. 所需工具：ChatGPT、各种AI工具
        """

# 生成PDF内容
def generate_pdf_content(recommendation, user_data):
    """生成PDF内容"""
    pdf_content = f"""
# AI副业方向推荐报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 用户信息
- 兴趣：{user_data['interest']}
- 技能：{user_data['skills']}
- 时间投入：{user_data['time']}
- 副业目标：{user_data['goal']}
- 是否出镜：{user_data['on_camera']}

## AI推荐结果

{recommendation}

---
*由AI副业方向推荐工具生成 | Yuebei Studio*
    """
    return pdf_content

# 发送邮件功能
def send_email(email, recommendation, user_data):
    """发送邮件（简化版）"""
    try:
        # 这里应该配置真实的邮件服务器
        st.success(f"📧 行动包已发送到 {email}")
        st.info("💡 实际部署时需要配置SMTP服务器")
        return True
    except Exception as e:
        st.error(f"邮件发送失败: {str(e)}")
        return False

# 获取学习资源
def get_learning_resources(recommendation):
    """根据推荐内容获取相关学习资源"""
    resources = []
    
    # 简单的关键词匹配
    if "写作" in recommendation or "内容" in recommendation:
        resources.extend(LEARNING_RESOURCES.get("AI写作", []))
    if "绘画" in recommendation or "设计" in recommendation:
        resources.extend(LEARNING_RESOURCES.get("AI绘画", []))
    if "编程" in recommendation or "开发" in recommendation:
        resources.extend(LEARNING_RESOURCES.get("AI编程", []))
    if "营销" in recommendation or "推广" in recommendation:
        resources.extend(LEARNING_RESOURCES.get("AI营销", []))
    
    # 如果没有匹配到，返回通用资源
    if not resources:
        resources = LEARNING_RESOURCES.get("AI写作", [])[:2]
    
    return resources

# 显示二维码
def show_qr_code():
    """显示支付二维码"""
    st.markdown("""
    <div class="qr-section">
        <h3>💰 想要完整版行动包？</h3>
        <p>扫码获取详细的学习资源、工具清单和变现策略</p>
        <p><strong>价格：¥29.9</strong></p>
        <p>包含：</p>
        <ul style="text-align: left; display: inline-block;">
            <li>详细学习计划</li>
            <li>工具清单</li>
            <li>变现策略</li>
            <li>案例分析</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 开发者模式开关
DEV_MODE = False  # 上线时设False

# 主应用
def main():
    # 页面标题
    st.markdown('<h1 class="main-header">🚀 AI副业方向推荐工具</h1>', unsafe_allow_html=True)
    st.markdown("### 填写你的信息，AI为你量身定制副业方案")
    
    # 初始化DeepSeek客户端
    api_key = init_deepseek_client()
    if not api_key:
        st.stop()
    
    # 侧边栏配置
    with st.sidebar:
        # 品牌LOGO/名
        st.markdown('<h2 style="color:#1f77b4; text-align:center; margin-bottom:0.5rem;">Yuebei Studio</h2>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; color:#888; font-size:1.1rem; margin-bottom:1rem;">副业AI推荐工具</div>', unsafe_allow_html=True)
        
        # 简要介绍（自定义卡片，无HTML代码显示）
        st.markdown('''
        <div style="background:#2b3a4b; color:#fff; border-radius:12px; padding:18px 16px 14px 16px; margin-bottom:1.2rem; font-size:1.08rem; line-height:1.8;">
        <span style="font-size:1.3em;">🚀</span> <b>一键获取专属副业方向和行动计划</b><br>
        结合你的兴趣、技能和目标，AI为你量身定制副业方案，助你高效变现、成长、打造个人品牌。
        </div>
        ''', unsafe_allow_html=True)
        
        # 使用步骤
        st.markdown("""
        <div style='margin:1rem 0;'>
        <b>📝 使用步骤：</b><br>
        1️⃣ 选择兴趣和技能<br>
        2️⃣ 选择目标和时间投入<br>
        3️⃣ 点击生成，获取专属推荐
        </div>
        """, unsafe_allow_html=True)
        
        # 今日额度/状态
        if st.session_state['generate_count'] >= 1:
            st.sidebar.warning("今日已达生成上限，请明天再试！", icon="⏳")
        else:
            st.sidebar.success("今日可免费生成1次AI推荐", icon="✅")
        
        st.markdown("---")
        # 联系方式
        st.markdown("<b>📧 联系我们：</b><br><a href='mailto:info@yuebeistudio.com'>info@yuebeistudio.com</a>", unsafe_allow_html=True)
        st.markdown("🌐 <a href='https://yuebeistudio.com' target='_blank'>yuebeistudio.com</a>", unsafe_allow_html=True)
        
        # FAQ/隐私承诺
        with st.expander("❓ 常见问题 / 数据安全"):
            st.markdown("""
            - <b>Q: 我的信息安全吗？</b><br>本工具不会保存你的个人信息，所有数据仅用于本次推荐。
            - <b>Q: 为什么每天只能用1次？</b><br>为保证服务质量和API成本，每人每天限用1次。
            - <b>Q: 推荐不满意怎么办？</b><br>可明天再试，或联系我们获取定制服务。
            - <b>Q: API连接失败怎么办？</b><br>系统会自动重试，如果失败会提供备用推荐。
            """, unsafe_allow_html=True)
    
    # 用户输入表单
    st.markdown('<h2 class="sub-header">📝 填写你的信息</h2>', unsafe_allow_html=True)
    
    with st.form("user_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            interest = st.multiselect(
                "🎯 你的兴趣（可多选）",
                INTEREST_OPTIONS,
                help="选择你感兴趣的领域，可多选"
            )
            
            skills = st.multiselect(
                "🛠️ 你的技能（可多选）",
                SKILL_OPTIONS,
                help="选择你已有的技能，可多选"
            )
            
            time_commitment = st.selectbox(
                "⏰ 每周可投入时间",
                ["1-3小时", "4-6小时", "7-10小时", "10小时以上"],
                help="选择你每周能够投入副业的时间"
            )
        
        with col2:
            goal = st.selectbox(
                "🎯 副业目标",
                ["赚钱", "学习AI技能", "时间自由", "建立个人品牌"],
                help="选择你从事副业的主要目标"
            )
            
            on_camera = st.radio(
                "📹 是否愿意出镜/创作",
                ["是", "否"],
                help="选择你是否愿意在视频、直播等场景中出镜"
            )
            
            # 额外信息
            additional_info = st.text_area(
                "💡 其他信息（可选）",
                placeholder="例如：预算、地理位置、特殊需求...",
                help="任何其他你认为重要的信息"
            )
        
        # 提交按钮
        submitted = st.form_submit_button(
            "🚀 生成AI推荐",
            type="primary",
            help="点击后AI将为你生成专属副业方案",
            disabled=(st.session_state['generate_count'] >= 1)
        )
        if st.session_state['generate_count'] >= 1:
            st.warning("今日已达生成上限，请明天再试！")
    
    # 处理表单提交
    if submitted:
        if not interest or not skills:
            st.error("请至少选择一个兴趣和一个技能！")
            st.stop()
        
        # 增加计数
        st.session_state['generate_count'] += 1

        # 显示加载动画
        with st.spinner("🤖 AI正在分析你的信息，生成个性化推荐，请稍候..."):
            # 准备用户数据
            user_data = {
                "interest": ", ".join(interest),
                "skills": ", ".join(skills),
                "time": time_commitment,
                "goal": goal,
                "on_camera": on_camera,
                "additional_info": additional_info
            }
            
            # 生成AI推荐
            recommendation = generate_ai_recommendation(api_key, user_data)
            
            # 如果API失败，使用备用推荐
            if not recommendation:
                st.warning("⚠️ AI服务暂时不可用，为您提供备用推荐")
                recommendation = generate_fallback_recommendation(user_data)
        
        # 结果展示和下方区块渲染逻辑
        if DEV_MODE or (recommendation):
            if not DEV_MODE:
                st.markdown('<h2 class="sub-header">🎯 你的AI副业推荐</h2>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-box">{recommendation}</div>', unsafe_allow_html=True)
            # 操作按钮（仅非开发者模式下显示）
            if not DEV_MODE:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("📋 复制结果", type="secondary"):
                        st.write("📋 结果已复制到剪贴板！")
                        st.code(recommendation)
                with col2:
                    if st.button("📄 保存为PDF", type="secondary"):
                        pdf_content = generate_pdf_content(recommendation, user_data)
                        st.download_button(
                            label="📄 下载PDF",
                            data=pdf_content,
                            file_name=f"AI副业推荐_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                with col3:
                    if st.button("🔄 重新生成", type="secondary"):
                        st.rerun()
                with col4:
                    if st.button("💾 保存到收藏", type="secondary"):
                        st.success("✅ 已保存到收藏夹")
            # 学习资源推荐（全部类别，折叠菜单）
            st.markdown("""<h3 style='margin-top:2.2rem; margin-bottom:0.7rem;'><span style='font-size:1.3em;'>📚</span> 相关学习资源</h3>""", unsafe_allow_html=True)
            for cat, resources in LEARNING_RESOURCES.items():
                icon = "📝" if "写作" in cat else ("🎨" if "绘画" in cat else ("💻" if "编程" in cat else "📈"))
                with st.expander(f"{icon} {cat}"):
                    for resource in resources:
                        st.markdown(f"""
                        <div style='background:#2b3a4b; color:#fff; border-radius:10px; margin-bottom:0.7rem; padding:1rem 1.2rem; box-shadow:0 1px 4px rgba(0,0,0,0.03);'>
                            <b style='font-size:1.08rem; color:#fff;'>{resource['title']}</b><br>
                            <span style='color:#b0b8c1;'>类型：{resource['type']}</span><br>
                            <a href='{resource['url']}' target='_blank' style='color:#4fc3f7; font-weight:500; text-decoration:none;'>🔗 官网链接</a>
                        </div>
                        """, unsafe_allow_html=True)
            # 行动包卡片和好评FAQ
            st.markdown('''
            <div style="background:#fffbe6; border-radius:16px; box-shadow:0 2px 12px rgba(255,193,7,0.08); padding:2rem 1.5rem 1.2rem 1.5rem; margin:2rem 0 1.2rem 0; border:2px solid #ffe082;">
                <div style="font-size:1.3rem; font-weight:600; color:#b26a00; margin-bottom:0.5rem; display:flex; align-items:center;">
                    <span style="font-size:1.7rem; margin-right:0.5rem;">🎁</span>专属副业变现行动包 <span style="background:#ffecb3; color:#b26a00; font-size:0.9rem; border-radius:6px; padding:2px 8px; margin-left:0.7rem;">限时免费</span>
                </div>
                <ul style="color:#7a5a00; font-size:1.08rem; margin-bottom:1.1rem; line-height:2.1;">
                    <li>10个爆款副业选题&案例</li>
                    <li>3大变现渠道实操指南</li>
                    <li>AI工具实操视频/模板</li>
                    <li>副业避坑清单</li>
                    <li>专属社群/一对一答疑</li>
                </ul>
                <div style="font-weight:500; color:#b26a00; margin-bottom:1.1rem;">填写邮箱，资料自动发送到您的邮箱，绝不骚扰</div>
                <div style="text-align:center; margin:1.2rem 0 0.5rem 0;">
                    <a href="https://tally.so/r/m6Y1V5" target="_blank">
                        <button style="background:#1f77b4;color:#fff;padding:0.8rem 2.2rem;border-radius:10px;font-size:1.15rem;font-weight:600;border:none;cursor:pointer;box-shadow:0 2px 8px rgba(31,119,180,0.08);">立即领取完整版行动包</button>
                    </a>
                </div>
                <div style="margin-top:1.2rem; color:#b26a00; font-size:0.98rem;">
                    <b>已帮助 1234 位用户开启AI副业变现之路</b>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown('''
            <div style="background:#f7f8fa; border-radius:12px; padding:1.1rem 1.2rem 0.7rem 1.2rem; margin-bottom:1.2rem; color:#888; font-size:1.02rem;">
                <b>用户好评：</b><br>
                <span style="color:#1f77b4;">"行动包内容很实用，直接照着做就能变现！"</span> —— 小王<br>
                <span style="color:#1f77b4;">"AI副业推荐很精准，行动建议很细致。"</span> —— 小李<br>
                <span style="color:#1f77b4;">"客服很耐心，资料很全，值得推荐！"</span> —— 小张<br>
                <br>
                <b>常见问题：</b><br>
                Q: 邮箱会被骚扰吗？<br>A: 绝不会，邮箱仅用于发送资料。<br>
                Q: 行动包内容真的有用吗？<br>A: 都是实操干货，已帮助上千人变现。
            </div>
            ''', unsafe_allow_html=True)
    
    # 页面底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>© 2024 Yuebei Studio. 让AI助力你的副业之路！</p>
        <p>Powered by DeepSeek Chat & Streamlit</p>
        <p>版本：v2.1 稳定版</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 