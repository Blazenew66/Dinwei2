import os

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
 
# 注意：在生产环境中，请使用环境变量而不是直接硬编码API密钥
# 例如：os.getenv("DEEPSEEK_API_KEY") 