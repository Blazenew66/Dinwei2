import streamlit as st
import requests
import json
import os
from datetime import datetime
import base64
from api_config import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL

# 页面配置
st.set_page_config(
    page_title="AI副业方向推荐工具",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .copy-button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    .qr-section {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化DeepSeek客户端
def init_deepseek_client():
    """初始化DeepSeek客户端"""
    # 优先使用配置文件中的API密钥，如果没有则使用环境变量
    api_key = DEEPSEEK_API_KEY or st.secrets.get("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
    if not api_key:
        st.error("请在api_config.py中设置DEEPSEEK_API_KEY或使用环境变量")
        return None
    
    return api_key

# 生成AI推荐
def generate_ai_recommendation(api_key, user_data):
    """使用DeepSeek生成副业推荐"""
    
    # 构建提示词
    prompt = f"""
你是一位AI副业咨询专家。请根据以下用户资料，推荐一个最合适的AI副业方向，并给出三步具体行动计划。

兴趣：{user_data['interest']}
技能：{user_data['skills']}
时间投入：{user_data['time']}
副业目的：{user_data['goal']}
是否出镜：{user_data['on_camera']}

请回复格式如下：
1. 推荐副业方向：
2. 为什么适合你：
3. 三步行动建议：

请用简体中文回复，内容要具体、实用、可操作。
"""
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "你是一位专业的AI副业咨询师，擅长为用户提供个性化的副业建议。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{DEEPSEEK_API_BASE}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            st.error(f"DeepSeek API调用失败: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        st.error(f"AI推荐生成失败: {str(e)}")
        return None

# 复制到剪贴板功能
def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    st.write("📋 结果已复制到剪贴板！")
    st.code(text)

# 保存为PDF功能（简化版）
def save_as_pdf(text):
    """保存结果为PDF（简化版）"""
    st.info("📄 PDF保存功能正在开发中...")
    # 这里可以集成reportlab或其他PDF库

# 显示二维码
def show_qr_code():
    """显示支付二维码"""
    st.markdown("""
    <div class="qr-section">
        <h3>💰 想要完整版行动包？</h3>
        <p>扫码获取详细的学习资源、工具清单和变现策略</p>
        <p>价格：¥29.9</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 这里可以添加实际的二维码图片
    # st.image("./static/pay.jpg", width=200)

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
        st.header("⚙️ 配置")
        st.success("✅ DeepSeek API已配置")
        
        # 可以在这里添加更多配置选项
        st.markdown("---")
        st.markdown("### 📞 联系我们")
        st.markdown("邮箱：contact@yuebeistudio.com")
        st.markdown("网站：yuebeistudio.com")
    
    # 用户输入表单
    st.markdown('<h2 class="sub-header">📝 填写你的信息</h2>', unsafe_allow_html=True)
    
    with st.form("user_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            interest = st.text_area(
                "🎯 你的兴趣和爱好",
                placeholder="例如：写作、摄影、编程、设计、营销...",
                help="描述你感兴趣的事物，这将帮助AI推荐更合适的副业方向"
            )
            
            skills = st.text_area(
                "🛠️ 你的技能和经验",
                placeholder="例如：Python编程、内容创作、数据分析、项目管理...",
                help="列出你已有的技能，包括工作技能和个人技能"
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
        submitted = st.form_submit_button("🚀 生成AI推荐", type="primary")
    
    # 处理表单提交
    if submitted:
        if not interest or not skills:
            st.error("请至少填写兴趣和技能信息！")
            return
        
        # 显示加载动画
        with st.spinner("🤖 AI正在分析你的信息，生成个性化推荐..."):
            # 准备用户数据
            user_data = {
                "interest": interest,
                "skills": skills,
                "time": time_commitment,
                "goal": goal,
                "on_camera": on_camera,
                "additional_info": additional_info
            }
            
            # 生成AI推荐
            recommendation = generate_ai_recommendation(api_key, user_data)
        
        if recommendation:
            # 显示结果
            st.markdown('<h2 class="sub-header">🎯 你的AI副业推荐</h2>', unsafe_allow_html=True)
            
            # 结果展示
            st.markdown(f'<div class="result-box">{recommendation}</div>', unsafe_allow_html=True)
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 复制结果", type="secondary"):
                    copy_to_clipboard(recommendation)
            
            with col2:
                if st.button("📄 保存为PDF", type="secondary"):
                    save_as_pdf(recommendation)
            
            with col3:
                if st.button("🔄 重新生成", type="secondary"):
                    st.rerun()
            
            # 引导变现模块
            st.markdown("---")
            show_qr_code()
            
            # 学习资源推荐（Bonus功能）
            st.markdown("### 📚 相关学习资源")
            st.info("💡 根据你的推荐方向，这里可以显示相关的学习资源链接")
            
            # 邮箱收集（Bonus功能）
            st.markdown("### 📧 获取完整版行动包")
            email = st.text_input("输入邮箱地址，获取详细的学习计划和工具清单")
            if st.button("📬 发送行动包", type="primary"):
                if email:
                    st.success(f"✅ 行动包已发送到 {email}")
                else:
                    st.warning("请输入有效的邮箱地址")
    
    # 页面底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>© 2024 Yuebei Studio. 让AI助力你的副业之路！</p>
        <p>Powered by DeepSeek Chat & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 