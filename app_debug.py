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
    page_title="AI副业方向推荐工具 - 调试版",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 调试模式
DEBUG_MODE = True

# 主标题
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
    .debug-box {
        background-color: #fff3cd !important;
        color: #856404 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        font-size: 0.9rem;
        font-family: monospace;
    }
    .error-box {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 选项配置
INTEREST_OPTIONS = [
    "写作", "摄影", "编程", "设计", "短视频", "自媒体", "AI绘画", "AI写作", 
    "AI编曲", "AI配音", "AI剪辑", "AI营销", "教育培训", "心理咨询", 
    "健康健身", "理财投资", "电商运营", "产品经理", "项目管理", "翻译", "其他"
]

SKILL_OPTIONS = [
    "内容创作", "视频剪辑", "平面设计", "Python编程", "数据分析", 
    "AI工具使用", "市场营销", "社群运营", "文案策划", "项目管理", 
    "产品设计", "摄影基础", "写作基础", "英语", "日语", "PPT制作", 
    "Excel", "演讲表达", "自律习惯", "其他"
]

# 学习资源
LEARNING_RESOURCES = {
    "AI写作": [
        {"title": "ChatGPT官方教程", "type": "官方文档", "url": "https://platform.openai.com/docs"},
        {"title": "Notion AI写作指南", "type": "教程", "url": "https://www.notion.so"},
        {"title": "秘塔写作猫", "type": "工具", "url": "https://xiezuocat.com"}
    ],
    "AI绘画": [
        {"title": "Midjourney官方", "type": "AI绘画", "url": "https://www.midjourney.com"},
        {"title": "Stable Diffusion", "type": "开源AI", "url": "https://stability.ai"},
        {"title": "DALL-E 2", "type": "OpenAI", "url": "https://openai.com/dall-e-2"}
    ],
    "AI编程": [
        {"title": "GitHub Copilot", "type": "AI编程助手", "url": "https://github.com/features/copilot"},
        {"title": "通义灵码", "type": "阿里云", "url": "https://tongyi.aliyun.com"},
        {"title": "Cursor编辑器", "type": "AI编程", "url": "https://cursor.sh"}
    ],
    "AI营销": [
        {"title": "Jasper AI", "type": "营销文案", "url": "https://www.jasper.ai"},
        {"title": "Copy.ai", "type": "文案生成", "url": "https://www.copy.ai"},
        {"title": "Grammarly", "type": "语法检查", "url": "https://www.grammarly.com"}
    ]
}

# 初始化会话状态
TODAY = date.today().isoformat()
if 'last_generate_date' not in st.session_state:
    st.session_state['last_generate_date'] = ''
if 'generate_count' not in st.session_state:
    st.session_state['generate_count'] = 0

# 新的一天自动重置
if st.session_state['last_generate_date'] != TODAY:
    st.session_state['last_generate_date'] = TODAY
    st.session_state['generate_count'] = 0

# 调试信息显示
if DEBUG_MODE:
    st.sidebar.markdown("### 🔧 调试信息")
    
    # 检查环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        st.sidebar.success("✅ API密钥已配置")
        st.sidebar.text(f"密钥长度: {len(api_key)}")
    else:
        st.sidebar.error("❌ API密钥未配置")
        st.sidebar.text("请在.env文件中设置DEEPSEEK_API_KEY")
    
    # 检查网络连接
    try:
        response = requests.get("https://api.deepseek.com/v1/models", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ DeepSeek API可访问")
        else:
            st.sidebar.warning(f"⚠️ DeepSeek API响应异常: {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"❌ 网络连接失败: {str(e)}")

# 初始化DeepSeek客户端
def init_deepseek_client():
    """初始化DeepSeek客户端"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if DEBUG_MODE:
        st.sidebar.markdown("### 🔍 API配置检查")
        if api_key:
            st.sidebar.success("✅ API密钥已找到")
        else:
            st.sidebar.error("❌ API密钥未找到")
            st.sidebar.markdown("""
            **解决方案：**
            1. 创建 `.env` 文件
            2. 添加：`DEEPSEEK_API_KEY=你的API密钥`
            3. 重启应用
            """)
    
    if not api_key:
        st.error("❌ 请在.env文件中设置DEEPSEEK_API_KEY")
        st.markdown("""
        **配置步骤：**
        1. 在项目根目录创建 `.env` 文件
        2. 在文件中添加：`DEEPSEEK_API_KEY=你的API密钥`
        3. 重启应用
        """)
        return None
    
    return api_key

# 生成AI推荐（带详细调试信息）
def generate_ai_recommendation(api_key, user_data):
    """使用DeepSeek生成副业推荐（带调试信息）"""
    
    if DEBUG_MODE:
        st.markdown('<div class="debug-box">🔍 开始API调用...</div>', unsafe_allow_html=True)
    
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
        if DEBUG_MODE:
            st.markdown(f'<div class="debug-box">🔄 第{attempt + 1}次尝试，超时时间{base_timeout * (attempt + 1)}秒</div>', unsafe_allow_html=True)
        
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
            
            if DEBUG_MODE:
                st.markdown(f'<div class="debug-box">📡 响应状态码: {response.status_code}</div>', unsafe_allow_html=True)
            
            if response.status_code == 200:
                result = response.json()
                if DEBUG_MODE:
                    st.markdown('<div class="debug-box">✅ API调用成功</div>', unsafe_allow_html=True)
                return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 401:
                st.error("❌ API密钥无效，请检查配置")
                if DEBUG_MODE:
                    st.markdown(f'<div class="debug-box">🔑 认证失败，请检查API密钥是否正确</div>', unsafe_allow_html=True)
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
                if DEBUG_MODE:
                    st.markdown(f'<div class="debug-box">❌ 错误响应: {response.text}</div>', unsafe_allow_html=True)
                return None
                
        except requests.exceptions.Timeout:
            if DEBUG_MODE:
                st.markdown(f'<div class="debug-box">⏰ 请求超时 (第{attempt + 1}次)</div>', unsafe_allow_html=True)
            if attempt < max_retries - 1:
                st.warning(f"⏰ 请求超时，正在重试... ({attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            else:
                st.error("❌ 网络连接超时，请检查网络连接或稍后再试")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ 网络连接失败，请检查网络连接")
            if DEBUG_MODE:
                st.markdown('<div class="debug-box">🌐 网络连接错误，请检查：<br>1. 网络连接是否正常<br>2. 防火墙是否阻止<br>3. 代理设置是否正确</div>', unsafe_allow_html=True)
            return None
        except Exception as e:
            if DEBUG_MODE:
                st.markdown(f'<div class="debug-box">❌ 未知错误: {str(e)}</div>', unsafe_allow_html=True)
            if attempt < max_retries - 1:
                st.warning(f"⚠️ 请求失败，正在重试... ({attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            else:
                st.error(f"❌ AI推荐生成失败: {str(e)}")
                return None
    
    return None

# 生成备用推荐
def generate_fallback_recommendation(user_data):
    """生成备用推荐"""
    interest = user_data['interest']
    skills = user_data['skills']
    goal = user_data['goal']
    
    if DEBUG_MODE:
        st.markdown('<div class="debug-box">🔄 使用备用推荐系统</div>', unsafe_allow_html=True)
    
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
        st.markdown('<h2 style="color:#1f77b4; text-align:center; margin-bottom:0.5rem;">Yuebei Studio</h2>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; color:#888; font-size:1.1rem; margin-bottom:1rem;">副业AI推荐工具</div>', unsafe_allow_html=True)
        
        # 简要介绍
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
            
            if DEBUG_MODE:
                st.markdown('<div class="debug-box">📊 用户数据已准备完成</div>', unsafe_allow_html=True)
            
            # 生成AI推荐
            recommendation = generate_ai_recommendation(api_key, user_data)
            
            # 如果API失败，使用备用推荐
            if not recommendation:
                st.warning("⚠️ AI服务暂时不可用，为您提供备用推荐")
                recommendation = generate_fallback_recommendation(user_data)
        
        # 结果展示
        if recommendation:
            st.markdown('<h2 class="sub-header">🎯 你的AI副业推荐</h2>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{recommendation}</div>', unsafe_allow_html=True)
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 复制结果", type="secondary"):
                    st.write("📋 结果已复制到剪贴板！")
                    st.code(recommendation)
            with col2:
                if st.button("🔄 重新生成", type="secondary"):
                    st.rerun()
            with col3:
                if st.button("💾 保存到收藏", type="secondary"):
                    st.success("✅ 已保存到收藏夹")
    
    # 页面底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>© 2024 Yuebei Studio. 让AI助力你的副业之路！</p>
        <p>Powered by DeepSeek Chat & Streamlit</p>
        <p>版本：v2.2 调试版</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 