#!/usr/bin/env python3
"""Run on the owner's Mac (once). Creates youtube.json for the VPS worker without printing any secret.

  python3 youtube_auth.py ~/Downloads/client_secret_XXXX.json   # the OAuth "Desktop app" client file from Google Cloud

Opens the browser for Google sign-in (the channel's account), receives the code on 127.0.0.1, exchanges it for a
refresh token and writes ./youtube.json (mode 0600). Copy that file to the VPS: /etc/tml-social/youtube.json.
"""
import http.server
import json
import os
import secrets
import sys
import urllib.parse
import urllib.request
import webbrowser

SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def main(path):
    client = json.load(open(path))
    client = client.get("installed") or client.get("web")
    state, code = secrets.token_urlsafe(16), {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            if q.get("state", [""])[0] == state:
                code["value"] = q.get("code", [""])[0]
            self.send_response(200); self.end_headers()
            self.wfile.write(b"Two Market Ledger: authorisation received. You can close this tab.")

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent", "state": state})
    print("Opening the browser for Google sign-in. Choose the Two Market Ledger channel account.")
    webbrowser.open(url)
    while "value" not in code:
        server.handle_request()
    data = urllib.parse.urlencode({"code": code["value"], "client_id": client["client_id"], "client_secret": client["client_secret"],
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    tokens = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data))
    if "refresh_token" not in tokens:
        sys.exit("No refresh token returned. Remove the app's access at myaccount.google.com/permissions and run again.")
    fd = os.open("youtube.json", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"client_id": client["client_id"], "client_secret": client["client_secret"], "refresh_token": tokens["refresh_token"]}, f)
    print("Wrote ./youtube.json (0600). Copy it to the VPS as /etc/tml-social/youtube.json. Do not share it or paste it anywhere.")


if __name__ == "__main__":
    main(sys.argv[1])
