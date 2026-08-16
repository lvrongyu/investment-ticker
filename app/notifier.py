from __future__ import annotations

import subprocess


def macos_notify(title: str, message: str) -> None:
    script = ["display notification", repr(message), "with title", repr(title)]
    subprocess.run(["osascript", "-e", " ".join(script)], check=False)
