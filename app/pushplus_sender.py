from __future__ import annotations

import requests


def send_pushplus(title: str, content: str, token: str, topic: str = "", template: str = "html") -> dict:
    if not token:
        raise ValueError("PUSHPLUS_TOKEN is missing")
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": template or "html",
    }
    if topic:
        payload["topic"] = topic
    r = requests.post("https://www.pushplus.plus/send", json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        raise RuntimeError(f"PushPlus failed: {data}")
    return data
