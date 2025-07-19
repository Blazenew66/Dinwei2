# 🔒 安全提示

## ⚠️ 重要安全提醒

您的API密钥已经配置在 `api_config.py` 文件中。为了保护您的账户安全，请注意以下事项：

### 🚨 安全注意事项

1. **不要提交到Git仓库**
   - 确保 `api_config.py` 已添加到 `.gitignore` 文件中
   - 不要将API密钥上传到公共代码仓库

2. **生产环境部署**
   - 在生产环境中，请使用环境变量而不是硬编码
   - 删除 `api_config.py` 文件，改用环境变量

3. **定期更换密钥**
   - 定期更换API密钥
   - 监控API使用情况

### 🔧 安全配置方法

#### 方法一：使用环境变量（推荐）
```bash
# 删除 api_config.py 文件
rm api_config.py

# 设置环境变量
export DEEPSEEK_API_KEY="your_api_key_here"
```

#### 方法二：使用Streamlit Secrets
在 Streamlit Cloud 中设置：
```toml
DEEPSEEK_API_KEY = "your_api_key_here"
```

#### 方法三：使用.env文件（本地开发）
```bash
# 创建 .env 文件
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

### 📋 检查清单

- [ ] 将 `api_config.py` 添加到 `.gitignore`
- [ ] 检查代码仓库中是否包含API密钥
- [ ] 设置API使用限制
- [ ] 监控异常使用情况

### 🆘 如果密钥泄露

1. 立即在DeepSeek平台撤销当前密钥
2. 生成新的API密钥
3. 更新所有使用该密钥的应用
4. 检查是否有异常使用记录

---

**记住：API密钥就像密码一样重要，请妥善保管！** 🔐 