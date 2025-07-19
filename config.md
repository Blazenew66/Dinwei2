# AI副业方向推荐工具 - 配置说明

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

#### 方法一：环境变量（推荐）
创建 `.env` 文件并添加：
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

#### 方法二：Streamlit Secrets
在 Streamlit Cloud 中设置 secrets：
```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
```

### 3. 运行应用
```bash
streamlit run app.py
```

## 🔧 配置选项

### DeepSeek API
- 获取地址：https://platform.deepseek.com/
- 模型：deepseek-chat（默认）
- API基础URL：https://api.deepseek.com/v1

### OpenAI API（可选）
如需使用 OpenAI 替代 DeepSeek，请修改 `app.py` 中的相关配置。

## 📁 项目结构
```
Dinwei2/
├── app.py              # 主应用文件
├── app_enhanced.py     # 增强版应用
├── requirements.txt    # 依赖包列表
├── config.md          # 配置说明
└── static/            # 静态资源文件夹（可选）
    └── pay.jpg        # 支付二维码图片
```

## 🎯 功能特性
- ✅ 用户输入表单
- ✅ AI副业推荐引擎
- ✅ 结果展示模块
- ✅ 引导变现模块
- ✅ 复制/保存功能
- ✅ 响应式设计

## 🔮 未来扩展
- PDF导出功能
- 邮箱收集系统
- 学习资源推荐
- 数据统计分析 