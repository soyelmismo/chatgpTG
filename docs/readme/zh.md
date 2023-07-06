- 机器人：https://t.me/chismegptbpt

[![zh](https://img.shields.io/badge/变量-zh-orange)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/zh.md)

## 命令：
- /new - 开始新对话。
- /img - 生成图片。
- /retry - 重新生成上一次机器人的回答。
- /chat_mode - 选择对话模式。
- /model - 显示AI模型。
- /api - 显示API。
- /lang - 查看可用语言。
- /status - 查看当前配置：模型、对话模式和API。
- /reset - 将配置恢复为默认值。
- /search - 在互联网上搜索。
- /help - 再次显示此消息。

## 特点：
- 调用函数！（直接连接到GPT的插件，6月份的模型>）。
- 本地JSON数据库。
- 非常模块化和可定制。
- 使用/search命令让GPT访问互联网！
- 发送文本文件、PDF或URL，机器人可以分析它们！
- 添加任意数量的OpenAI反向代理和相应的模型！
- 多语言支持。
- 读取图像中的文本。
- 转录音频。

# 重要提示：
- 自定义API必须遵循OpenAI的相同结构，即 "https://domain.dom/v1/..."。

## 设置
1. 获取你的[OpenAI API](https://openai.com/api/)密钥。

2. 获取你的Telegram机器人令牌，可以在[@BotFather](https://t.me/BotFather)处获取。

3. 编辑 `config/api.example.json` 文件，配置你的API-KEY或添加自定义API。

4. 添加你的Telegram令牌、Mongo数据库，修改`docker-compose.example.yml`中的其他变量，并将`docker-compose.example.yml`重命名为`docker-compose.yml`。

5. 🔥 从终端进入目录并**运行**：
    ```bash
    docker-compose up --build
    ```
# 星星历史记录

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## 参考资料
1. 来源：<a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>