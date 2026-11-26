"""Meta Graph API: Instagram Reels and Facebook Reels via resumable upload of the local file (no public media URL needed)."""
import os
import time

from . import AuthProblem, Uncertain
from ..http import HttpError

GRAPH = "https://graph.facebook.com/v21.0"


class Meta:
    def __init__(self, http, creds, sleep=time.sleep):
        self.http, self.creds, self.sleep = http, creds, sleep  # creds: page_id, ig_user_id, page_token

    def _p(self):
        return {"Authorization": "OAuth " + self.creds["page_token"]}

    def _call(self, method, url, **kw):
        try:
            return self.http.call(method, url, **kw)
        except HttpError as e:
            if e.status in (401, 403) or '"code":190' in (e.body or "").replace(" ", ""):
                raise AuthProblem(f"Meta token or permission problem (HTTP {e.status})") from None
            raise

    def health(self):
        page, _ = self._call("GET", f"{GRAPH}/{self.creds['page_id']}?fields=id,name", headers=self._p())
        ig, _ = self._call("GET", f"{GRAPH}/{self.creds['ig_user_id']}?fields=id,username", headers=self._p())
        return {"ok": bool(page.get("id") and ig.get("id")), "page": page.get("name"), "instagram": ig.get("username")}

    def _upload_bytes(self, url, path):
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            try:
                data, _ = self.http.call("POST", url, {**self._p(), "offset": "0", "file_size": str(size)}, f.read())
            except HttpError as e:
                if e.transient:
                    raise Uncertain(f"Meta upload interrupted (HTTP {e.status})") from None
                raise
        return data

    def instagram_reel(self, item):
        ig = self.creds["ig_user_id"]
        created, _ = self._call("POST", f"{GRAPH}/{ig}/media", headers=self._p(),
                                json_body={"media_type": "REELS", "upload_type": "resumable", "caption": item["caption"] or "",
                                           "share_to_feed": True})
        container, uri = created.get("id"), created.get("uri")
        if not container or not uri:
            raise HttpError(502, "no container", transient=True)
        self._upload_bytes(uri, item["asset_path"])
        for _ in range(60):  # wait up to ~10 minutes for processing
            st, _ = self._call("GET", f"{GRAPH}/{container}?fields=status_code", headers=self._p())
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") == "ERROR":
                raise HttpError(422, "Instagram rejected the video during processing")
            self.sleep(10)
        else:
            raise Uncertain("Instagram processing did not finish; check before retrying")
        try:
            pub, _ = self._call("POST", f"{GRAPH}/{ig}/media_publish", headers=self._p(), json_body={"creation_id": container})
        except HttpError as e:
            if e.transient:
                raise Uncertain(f"Instagram publish uncertain (HTTP {e.status})") from None
            raise
        media = pub.get("id")
        info, _ = self._call("GET", f"{GRAPH}/{media}?fields=permalink", headers=self._p())
        return {"remote_id": media, "permalink": info.get("permalink")}

    def facebook_reel(self, item):
        page = self.creds["page_id"]
        start, _ = self._call("POST", f"{GRAPH}/{page}/video_reels", headers=self._p(), json_body={"upload_phase": "start"})
        video_id, url = start.get("video_id"), start.get("upload_url")
        if not video_id or not url:
            raise HttpError(502, "no upload session", transient=True)
        self._upload_bytes(url, item["asset_path"])
        try:
            self._call("POST", f"{GRAPH}/{page}/video_reels", headers=self._p(),
                       json_body={"upload_phase": "finish", "video_id": video_id, "video_state": "PUBLISHED",
                                  "description": item["caption"] or ""})
        except HttpError as e:
            if e.transient:
                raise Uncertain(f"Facebook Reel finish uncertain (HTTP {e.status})") from None
            raise
        return {"remote_id": video_id, "permalink": None}

    def verify(self, remote_id, platform):
        fields = "permalink,media_type" if platform == "instagram_reels" else "status,permalink_url"
        data, _ = self._call("GET", f"{GRAPH}/{remote_id}?fields={fields}", headers=self._p())
        if platform == "instagram_reels":
            return {"exists": bool(data.get("permalink")), "public": bool(data.get("permalink")), "permalink": data.get("permalink")}
        st = (data.get("status") or {}).get("video_status")
        link = data.get("permalink_url")
        return {"exists": bool(data), "public": st == "ready" and bool(link), "permalink": ("https://www.facebook.com" + link) if link and link.startswith("/") else link,
                "rejected": st == "error"}

    # ---- content availability (read today's posts) and approved evergreen fallback (image posts) ----
    def recent_captions(self, since_unix):
        """Captions of Facebook Page and Instagram posts published since the given time."""
        fb, _ = self._call("GET", f"{GRAPH}/{self.creds['page_id']}/posts?fields=message,created_time&since={int(since_unix)}&limit=50",
                           headers=self._p())
        ig, _ = self._call("GET", f"{GRAPH}/{self.creds['ig_user_id']}/media?fields=caption,timestamp&limit=50", headers=self._p())
        return {"facebook": [p.get("message", "") for p in fb.get("data", [])],
                "instagram": [m.get("caption", "") for m in ig.get("data", [])
                              if m.get("timestamp", "")[:19] >= time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(since_unix))]}

    def publish_image(self, platform, image_url, caption):
        if platform == "facebook":
            data, _ = self._call("POST", f"{GRAPH}/{self.creds['page_id']}/photos", headers=self._p(),
                                 json_body={"url": image_url, "caption": caption, "published": True})
            return {"remote_id": data.get("post_id") or data.get("id"), "permalink": None}
        ig = self.creds["ig_user_id"]
        created, _ = self._call("POST", f"{GRAPH}/{ig}/media", headers=self._p(), json_body={"image_url": image_url, "caption": caption})
        for _ in range(30):
            st, _ = self._call("GET", f"{GRAPH}/{created['id']}?fields=status_code", headers=self._p())
            if st.get("status_code") == "FINISHED":
                break
            self.sleep(5)
        pub, _ = self._call("POST", f"{GRAPH}/{ig}/media_publish", headers=self._p(), json_body={"creation_id": created["id"]})
        info, _ = self._call("GET", f"{GRAPH}/{pub['id']}?fields=permalink", headers=self._p())
        return {"remote_id": pub["id"], "permalink": info.get("permalink")}
