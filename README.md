# 🚀 AI副业方向推荐工具

一个基于AI的个性化副业方向推荐工具，帮助用户找到最适合的AI副业方向并制定具体行动计划。

## ✨ 功能特性

### 🎯 核心功能
- **智能推荐引擎**：基于用户兴趣、技能、时间投入等个性化推荐
- **三步行动计划**：提供具体可操作的行动建议
- **预期收益分析**：评估副业方向的潜在收益
- **工具清单推荐**：推荐所需的学习工具和资源

### 🎨 用户体验
- **响应式设计**：适配各种设备屏幕
- **美观界面**：现代化UI设计，用户体验友好
- **实时反馈**：AI分析过程可视化
- **一键操作**：复制、保存、重新生成等功能

### 💰 变现功能
- **引导购买**：展示完整版行动包
- **邮箱收集**：收集潜在客户信息
- **学习资源**：推荐相关学习材料
- **二维码支付**：便捷的支付方式

## 🛠️ 技术栈

- **前端框架**：Streamlit
- **AI模型**：DeepSeek Chat
- **编程语言**：Python 3.8+
- **部署平台**：Streamlit Cloud（可迁移到自有服务器）

## 📦 安装部署

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd Dinwei2

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. API配置
```bash
# 方法一：环境变量
export DEEPSEEK_API_KEY="your_api_key_here"

# 方法二：创建.env文件
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

### 3. 运行应用
```bash
# 基础版本
streamlit run app.py

# 增强版本（推荐）
streamlit run app_enhanced.py
```

## 🎮 使用指南

### 1. 填写信息
- **兴趣和爱好**：描述你感兴趣的事物
- **技能和经验**：列出已有的技能
- **时间投入**：选择每周可投入的时间
- **副业目标**：选择主要目标（赚钱/学习/自由/品牌）
- **是否出镜**：选择是否愿意在视频中出镜

### 2. 获取推荐
- 点击"生成AI推荐"按钮
- 等待AI分析（通常10-30秒）
- 查看个性化推荐结果

### 3. 后续行动
- 复制推荐结果
- 查看学习资源
- 下载PDF报告
- 获取完整版行动包

## 📁 项目结构

```
Dinwei2/
├── app.py                 # 基础版本应用
├── app_enhanced.py        # 增强版本应用（推荐）
├── requirements.txt       # Python依赖包
├── README.md             # 项目说明文档
├── config.md             # 配置说明文档
└── static/               # 静态资源文件夹
    └── pay.jpg           # 支付二维码图片
```

## 🔧 配置选项

### DeepSeek API设置
- **模型**：deepseek-chat（默认）
- **最大token**：1500
- **温度**：0.7（平衡创意和准确性）
- **API基础URL**：https://api.deepseek.com/v1

### 自定义配置
可以在代码中修改以下参数：
- 推荐提示词模板
- 学习资源数据库
- UI样式和布局
- 邮件发送配置

## 🚀 部署方案

### 1. Streamlit Cloud（推荐）
- 免费托管
- 自动部署
- 易于管理

### 2. 自有服务器
- 使用Docker部署
- 配置Nginx反向代理
- 设置SSL证书

### 3. 云平台部署
- AWS/GCP/Azure
- Heroku/Vercel
- 阿里云/腾讯云

## 💡 扩展功能

### 已实现功能
- ✅ 基础推荐引擎
- ✅ 结果展示模块
- ✅ 复制/保存功能
- ✅ 学习资源推荐
- ✅ 邮箱收集系统
- ✅ 引导变现模块

### 计划功能
- 🔄 PDF导出（完整版）
- 🔄 用户数据统计
- 🔄 推荐历史记录
- 🔄 多语言支持
- 🔄 移动端优化
- 🔄 数据可视化

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 代码规范
- 使用Python PEP 8规范
- 添加适当的注释
- 编写单元测试
- 更新文档

## 📞 联系我们

- **邮箱**：contact@yuebeistudio.com
- **网站**：yuebeistudio.com
- **GitHub**：[项目地址]

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- DeepSeek提供的强大AI模型
- Streamlit团队开发的优秀框架
- 所有贡献者和用户的支持

---

**让AI助力你的副业之路！** 🚀 