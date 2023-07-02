import httpx

def GetAnswer(self, messages: str, model: str = "gpt-3.5-turbo"):
    captcha_code = "hadsa"
    if model == "gpt-4":
        chat_id = "quran---tafseer-saadi-pdf-wbgknt7zn"
    elif model == "gpt-3.5-turbo":
        chat_id = "chatbase--1--pdf-p680fxvnm"
    response = httpx.post("https://www.chatbase.co/api/fe/chat", json={"chatId": chat_id, "captchaCode": captcha_code, "messages": messages}, proxies=self.proxies)
    return response.text
