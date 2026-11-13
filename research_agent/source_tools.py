from __future__ import annotations

import re
import urllib.error
import urllib.request
from typing import Any


URL_RE = re.compile(r"https?://[^\s\]\)\"'<>]+", re.IGNORECASE)


def collect_urls(value: Any, *, limit: int = 40) -> list[str]:
    found: list[str] = []

    def visit(item: Any) -> None:
        if len(found) >= limit:
            return
        if isinstance(item, str):
            for raw in URL_RE.findall(item):
                url = raw.rstrip(".,;:")
                if url not in found:
                    found.append(url)
                    if len(found) >= limit:
                        return
        elif isinstance(item, dict):
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return found


def check_source_urls(urls: list[str], *, timeout_seconds: float = 8.0) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for url in urls:
        checks.append(_check_url(url, timeout_seconds=timeout_seconds))
    return checks


def _check_url(url: str, *, timeout_seconds: float) -> dict[str, Any]:
    headers = {"User-Agent": "research-agent/0.1 source verifier"}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                content_type = response.headers.get("content-type", "")
                return {
                    "url": url,
                    "reachable": True,
                    "status": response.status,
                    "content_type": content_type,
                    "method": method,
                }
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 405}:
                continue
            return {
                "url": url,
                "reachable": False,
                "status": exc.code,
                "error": str(exc),
                "method": method,
            }
        except Exception as exc:
            if method == "HEAD":
                continue
            return {
                "url": url,
                "reachable": False,
                "status": None,
                "error": str(exc),
                "method": method,
            }
    return {"url": url, "reachable": False, "status": None, "error": "unknown", "method": "GET"}
