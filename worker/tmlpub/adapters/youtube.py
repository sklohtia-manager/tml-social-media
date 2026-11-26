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
        self.http, self.creds = http, creds  # creds: client_id, client_secret, refresh_token, channel_id (recorded at sign-in)
        self._token = None
        self._channel_ok = False

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

    def _channel(self):
        data, _ = self.http.call("GET", f"{API}/channels?part=id,snippet&mine=true", self._auth())
        items = data.get("items") or []
        return (items[0]["id"], items[0].get("snippet", {}).get("title")) if items else (None, None)

    def check_channel(self):
        """Fail closed unless the token belongs to the channel recorded (and confirmed by the owner) at sign-in."""
        if self._channel_ok:
            return
        expected = self.creds.get("channel_id")
        if not expected:
            raise AuthProblem("youtube.json has no confirmed channel_id; re-run youtube_auth.py")
        found, title = self._channel()
        if found != expected:
            raise AuthProblem(f"authorised YouTube channel {found} ({title}) is not the confirmed TML channel {expected}")
        self._channel_ok = True

    def health(self):
        found, title = self._channel()
        expected = self.creds.get("channel_id")
        return {"ok": bool(found) and found == expected, "channel": found, "title": title,
                "expected": expected, "match": found == expected}

    def upload(self, item, shorts=False):
        self.check_channel()
        size = os.path.getsize(item["asset_path"])
        title = (item["title"] or "")[:100]
        description = (item["caption"] or "") + f"\n\nRef: {item['key']}"
        status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
        private_test = json.loads(item["manifest"] or "{}").get("visibility") == "private"
        if item["scheduled_utc"] and not private_test:
            status["publishAt"] = item["scheduled_utc"]  # private test: stays private, never scheduled to go public
        language = json.loads(item["manifest"] or "{}").get("language", "en")
        meta = {"snippet": {"title": title, "description": description[:5000], "categoryId": "27",
                            "defaultLanguage": language, "defaultAudioLanguage": language}, "status": status}
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
                "private_processed": st.get("privacyStatus") == "private" and st.get("uploadStatus") == "processed",
                "public": st.get("privacyStatus") == "public" and st.get("uploadStatus") == "processed",
                "scheduled": bool(st.get("publishAt")), "rejected": st.get("uploadStatus") in ("rejected", "failed")}
