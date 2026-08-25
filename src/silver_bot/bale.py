import json, urllib.parse, urllib.request
class Bale:
    def __init__(self, token): self.base = f"https://tapi.bale.ai/bot{token}/"
    def call(self, method, **params):
        data = urllib.parse.urlencode(params).encode(); req = urllib.request.Request(self.base + method, data=data)
        with urllib.request.urlopen(req, timeout=10) as r: result = json.loads(r.read())
        if not result.get("ok"): raise RuntimeError(result.get("description", "Bale API error"))
        return result.get("result")
    def validate(self): return self.call("getMe")
    def send(self, chat_id, text): return self.call("sendMessage", chat_id=chat_id, text=text)
