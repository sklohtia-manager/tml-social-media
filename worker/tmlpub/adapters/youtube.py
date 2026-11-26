"""YouTube Data API v3: OAuth refresh, resumable upload (private first, optional publishAt), status verification."""
import json
import os
from urllib.parse import urlencode

from . import AuthProblem, Uncertain
from ..http import HttpError

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
API = "https://www.googleapis.com/youtube/v3"


class YouTube:
    def __init__(self, http, creds):
        self.http, self.creds = http, creds  # creds: client_id, client_secret, refresh_token
        self._token = None

    def token(self):
        if self._token:
            return self._token
        try:
            data, _ = self.http.call("POST", TOKEN_URL, {"Content-Type": "application/x-www-form-urlencoded"},
                                     urlencode({"client_id": self.creds["client_id"], "client_secret": self.creds["client_secret"],
                                                "refresh_token": self.creds["refresh_token"], "grant_type": "refresh_token"}).encode())
        except HttpError as e:
            raise AuthProblem(f"YouTube token refresh failed (HTTP {e.status}); re-authorise the OAuth client") from None
        self._token = data["access_token"]
        return self._token

    def _auth(self):
        return {"Authorization": "Bearer " + self.token()}

    def health(self):
        data, _ = self.http.call("GET", f"{API}/channels?part=id,snippet&mine=true", self._auth())
        items = data.get("items") or []
        return {"ok": bool(items), "channel": items[0]["id"] if items else None}

    def upload(self, item, shorts=False):
        size = os.path.getsize(item["asset_path"])
        title = (item["title"] or "")[:100]
        description = (item["caption"] or "") + f"\n\nRef: {item['key']}"
        status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
        if item["scheduled_utc"]:
            status["publishAt"] = item["scheduled_utc"]
        meta = {"snippet": {"title": title, "description": description[:5000], "categoryId": "27"}, "status": status}
        try:
            _, headers = self.http.call("POST", UPLOAD_URL + "?uploadType=resumable&part=snippet,status",
                                        {**self._auth(), "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"},
                                        json_body=meta)
        except HttpError as e:
            if e.status in (401, 403):
                raise AuthProblem(f"YouTube upload refused (HTTP {e.status})") from None
            raise
        location = headers.get("Location") or headers.get("location")
        if not location:
            raise HttpError(502, "no resumable session", transient=True)
        with open(item["asset_path"], "rb") as f:
            try:
                data, _ = self.http.call("PUT", location, {**self._auth(), "Content-Type": "video/mp4"}, f.read())
            except HttpError as e:
                if e.transient:
                    raise Uncertain(f"YouTube upload interrupted (HTTP {e.status}); check YouTube Studio before any retry") from None
                raise
        if not data.get("id"):
            raise Uncertain("YouTube returned no video id")
        return {"remote_id": data["id"], "permalink": f"https://www.youtube.com/watch?v={data['id']}"}

    def verify(self, remote_id):
        data, _ = self.http.call("GET", f"{API}/videos?part=status,processingDetails&id={remote_id}", self._auth())
        items = data.get("items") or []
        if not items:
            return {"exists": False}
        st = items[0]["status"]
        return {"exists": True, "privacy": st.get("privacyStatus"), "upload": st.get("uploadStatus"),
                "public": st.get("privacyStatus") == "public" and st.get("uploadStatus") == "processed",
                "scheduled": bool(st.get("publishAt")), "rejected": st.get("uploadStatus") in ("rejected", "failed")}
