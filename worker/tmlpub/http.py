"""Minimal HTTP client with an injectable transport (tests use a fake). Never logs request bodies or tokens."""
import json
import urllib.error
import urllib.request


class HttpError(Exception):
    def __init__(self, status, body, retry_after=None, transient=False):
        super().__init__(f"HTTP {status}")
        self.status, self.body, self.retry_after, self.transient = status, body, retry_after, transient


def urllib_transport(method, url, headers, body, timeout=120):
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()


class Http:
    def __init__(self, transport=None):
        self.transport = transport or urllib_transport

    def call(self, method, url, headers=None, body=None, json_body=None):
        headers = dict(headers or {})
        if json_body is not None:
            body = json.dumps(json_body).encode()
            headers["Content-Type"] = "application/json; charset=UTF-8"
        status, rheaders, data = self.transport(method, url, headers, body)
        if status >= 400:
            ra = rheaders.get("Retry-After") or rheaders.get("retry-after")
            raise HttpError(status, data[:500].decode("utf8", "replace"), float(ra) if ra and str(ra).isdigit() else None,
                            transient=status in (408, 429) or status >= 500)
        try:
            payload = json.loads(data) if data else {}
        except ValueError:
            payload = {}
        return payload, rheaders
