import streamlit as st
import requests
import json
import os
import time
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI副业方向推荐工具 - 稳定版",
    page_icon="🚀",
    layout="wide"
)

# 自定义CSS
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
    .result-box {
        background-color: #f0f4fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    .error-box {
        background-color: #fff5f5;
        color: #c53030;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        margin: 1rem 0;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'last_generate_date' not in st.session_state:
    st.session_state['last_generate_date'] = ''
if 'generate_count' not in st.session_state:
    st.session_state['generate_count'] = 0

# 新的一天自动重置
TODAY = date.today().isoformat()
if st.session_state['last_generate_date'] != TODAY:
    st.session_state['last_generate_date'] = TODAY
    st.session_state['generate_count'] = 0

# 兴趣和技能选项
INTEREST_OPTIONS = ["写作", "摄影", "编程", "设计", "短视频", "自媒体", "AI绘画", "AI写作", "AI编曲", "AI配音", "AI剪辑", "AI营销", "教育培训", "心理咨询", "健康健身", "理财投资", "电商运营", "产品经理", "项目管理", "翻译", "其他"]
SKILL_OPTIONS = ["内容创作", "视频剪辑", "平面设计", "Python编程", "数据分析", "AI工具使用", "市场营销", "社群运营", "文案策划", "项目管理", "产品设计", "摄影基础", "写作基础", "英语", "日语", "PPT制作", "Excel", "演讲表达", "自律习惯", "其他"]

# 初始化DeepSeek客户端
def init_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请在本地.env中设置DEEPSEEK_API_KEY")
        return None
    return api_key

# 生成AI推荐（增强版，带重试机制）
def generate_ai_recommendation(api_key, user_data):
    """使用DeepSeek生成副业推荐（带重试机制）"""
    
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

请用简体中文回复，内容要具体、实用、可操作。
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
                    {"role": "system", "content": "你是一位专业的AI副业咨询师，擅长为用户提供个性化的副业建议。"},
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

# 主应用
def main():
    st.markdown('<h1 class="main-header">🚀 AI副业方向推荐工具</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center; color:#666;">填写你的信息，AI为你量身定制副业方案</h3>', unsafe_allow_html=True)
    
    # 初始化API客户端
    api_key = init_deepseek_client()
    if not api_key:
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 📊 使用状态")
        if st.session_state['generate_count'] >= 1:
            st.warning("今日已达生成上限，请明天再试！", icon="⏳")
        else:
            st.success("今日可免费生成1次AI推荐", icon="✅")
        
        st.markdown("---")
        st.markdown("### 📝 使用步骤")
        st.markdown("1. 选择兴趣和技能")
        st.markdown("2. 填写目标和时间")
        st.markdown("3. 生成专属推荐")
        
        st.markdown("---")
        st.markdown("### 📧 联系我们")
        st.markdown("info@yuebeistudio.com")
        
        # 稳定性说明
        with st.expander("🔧 稳定性说明"):
            st.markdown("""
            - **重试机制**：API失败时自动重试3次
            - **备用推荐**：API不可用时提供基础推荐
            - **超时优化**：动态调整超时时间
            - **错误处理**：详细的错误提示和解决方案
            """)
    
    # 用户输入表单
    st.markdown("### 📝 填写你的信息")
    
    with st.form("user_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            interest = st.multiselect("🎯 你的兴趣（可多选）", INTEREST_OPTIONS)
            skills = st.multiselect("🛠️ 你的技能（可多选）", SKILL_OPTIONS)
            time_commitment = st.selectbox("⏰ 每周可投入时间", ["1-3小时", "4-6小时", "7-10小时", "10小时以上"])
        
        with col2:
            goal = st.selectbox("🎯 副业目标", ["赚钱", "学习AI技能", "时间自由", "建立个人品牌"])
            on_camera = st.radio("📹 是否愿意出镜/创作", ["是", "否"])
            additional_info = st.text_area("💡 其他信息（可选）", placeholder="例如：预算、地理位置、特殊需求...")
        
        submitted = st.form_submit_button("🚀 生成AI推荐", type="primary", disabled=(st.session_state['generate_count'] >= 1))
    
    # 处理表单提交
    if submitted:
        if not interest or not skills:
            st.error("请至少选择一个兴趣和一个技能！")
            st.stop()
        
        if st.session_state['generate_count'] >= 1:
            st.warning("今日已达生成上限，请明天再试！")
            st.stop()
        
        # 增加计数
        st.session_state['generate_count'] += 1
        
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
        
        # 结果展示
        if recommendation:
            st.markdown("### 🎯 你的AI副业推荐")
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
            
            # 高级版推广
            st.markdown("""
            <div style="background:#fffbe6; border-radius:16px; padding:2rem; margin:2rem 0; border:2px solid #ffe082;">
                <h3 style="color:#b26a00;">🎁 升级到高级版</h3>
                <p style="color:#7a5a00;"><strong>¥29.9</strong> 获得完整版行动包</p>
                <ul style="color:#7a5a00;">
                    <li>10个爆款副业选题&案例</li>
                    <li>3大变现渠道实操指南</li>
                    <li>AI工具实操视频/模板</li>
                    <li>副业避坑清单</li>
                    <li>专属社群/一对一答疑</li>
                </ul>
                <a href="https://tally.so/r/m6Y1V5" target="_blank">
                    <button style="background:#1f77b4;color:#fff;padding:0.8rem 2rem;border-radius:10px;font-size:1.1rem;font-weight:600;border:none;cursor:pointer;">
                        立即升级到高级版
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # 页面底部
    st.markdown("---")
    st.markdown('<p style="text-align:center; color:#666;">© 2024 Yuebei Studio. 让AI助力你的副业之路！</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 