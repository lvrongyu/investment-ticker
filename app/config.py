from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRET_ENV = ROOT / "secrets" / "pushplus.env"


def _load_env_file(path: Path = SECRET_ENV) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config() -> dict:
    _load_env_file()
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    cfg.setdefault("pushplus", {})
    cfg.setdefault("finnhub", {})
    cfg["pushplus"]["token"] = cfg["pushplus"].get("token") or os.getenv("PUSHPLUS_TOKEN", "")
    cfg["pushplus"]["topic"] = cfg["pushplus"].get("topic") or os.getenv("PUSHPLUS_TOPIC", "")
    cfg["finnhub"]["token"] = cfg["finnhub"].get("token") or os.getenv("FINNHUB_TOKEN", "")
    return cfg
