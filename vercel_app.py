import streamlit as st
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置页面配置
st.set_page_config(
    page_title="AI副业推荐工具",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入主应用
from app_enhanced import main

if __name__ == "__main__":
    main() 