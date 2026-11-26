#!/usr/bin/env python3
"""Run on the owner's Mac (once). Creates youtube.json for the VPS worker without printing any secret.

  python3 youtube_auth.py ~/Downloads/client_secret_XXXX.json   # the OAuth "Desktop app" client file from Google Cloud

1. Opens the browser for Google sign-in (OAuth 2.0 with PKCE; the redirect goes only to 127.0.0.1 on this Mac).
2. Exchanges the code for a refresh token.
3. Reads which YouTube channel the account manages and asks you to confirm it is Two Market Ledger.
4. Only then writes ./youtube.json (mode 0600) including the confirmed channel_id. The worker refuses to upload if the
   token ever belongs to a different channel.
Copy youtube.json to the VPS as /etc/tml-social/youtube.json, then delete the local copy and the client_secret file.
Nothing secret is printed. Run it in a private folder, never inside a Git repository.
"""
import base64
import hashlib
import http.server
import json
import os
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
EXPECTED_TITLE = "Two Market Ledger"


def pkce_pair():
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def in_git_repo():
    try:
        return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True).stdout.strip() == "true"
    except FileNotFoundError:
        return False


def main(path):
    if in_git_repo():
        sys.exit("Refusing to run inside a Git repository (youtube.json must never be committed). Use a private folder.")
    client = json.load(open(path))
    client = client.get("installed") or client.get("web")
    if not client:
        sys.exit("This is not an OAuth client file. Download the 'Desktop app' client JSON from Google Cloud.")
    state, result = secrets.token_urlsafe(16), {}
    verifier, challenge = pkce_pair()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            if q.get("state", [""])[0] == state:
                result["code"] = q.get("code", [""])[0]
                result["error"] = q.get("error", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Two Market Ledger: response received. You can close this tab and return to Terminal.")

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    server.timeout = 300
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Opening the browser for Google sign-in. Sign in with the Google account that owns the Two Market Ledger channel,")
    print("and if asked, choose the Two Market Ledger channel (brand account).")
    webbrowser.open(url)
    while "code" not in result:
        server.handle_request()  # waits up to 5 minutes per request; press Ctrl-C to cancel
    if result.get("error") or not result.get("code"):
        sys.exit(f"Sign-in was not completed ({result.get('error') or 'no code'}). Nothing was saved.")
    data = urllib.parse.urlencode({"code": result["code"], "client_id": client["client_id"], "client_secret": client["client_secret"],
                                   "redirect_uri": redirect, "grant_type": "authorization_code", "code_verifier": verifier}).encode()
    try:
        tokens = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=30))
    except urllib.error.HTTPError as e:
        sys.exit(f"Google refused the code exchange (HTTP {e.code}). Nothing was saved. Run the script again.")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach Google ({e.reason}). If this mentions certificates, run 'Install Certificates.command' "
                 "from your Python folder in Applications, or use /usr/bin/python3. Nothing was saved.")
    if "refresh_token" not in tokens:
        sys.exit("No refresh token returned. Remove the app's access at https://myaccount.google.com/permissions and run again.")
    granted = set(tokens.get("scope", "").split())
    if not set(SCOPES.split()) <= granted:
        sys.exit("Not all permissions were granted (both YouTube boxes must be ticked). Nothing was saved. Run again.")

    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true",
                                 headers={"Authorization": "Bearer " + tokens["access_token"]})
    items = json.load(urllib.request.urlopen(req, timeout=30)).get("items") or []
    if len(items) != 1:
        sys.exit(f"This sign-in manages {len(items)} YouTube channels; expected exactly one. Nothing was saved. "
                 "Sign in again and pick the Two Market Ledger channel.")
    channel_id, title = items[0]["id"], items[0]["snippet"]["title"]
    print(f"\nAuthorised YouTube channel: {title}  (id {channel_id})")
    print(f"Check it at https://www.youtube.com/channel/{channel_id}")
    if title.strip() != EXPECTED_TITLE:
        print(f"WARNING: the channel name is not exactly '{EXPECTED_TITLE}'.")
    if input("Is this the Two Market Ledger channel? Type YES to save: ").strip() != "YES":
        sys.exit("Not confirmed. Nothing was saved. Revoke this sign-in at https://myaccount.google.com/permissions if it was the wrong account.")

    fd = os.open("youtube.json", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"client_id": client["client_id"], "client_secret": client["client_secret"], "refresh_token": tokens["refresh_token"],
                   "channel_id": channel_id, "channel_title": title}, f)
    print("\nWrote ./youtube.json (permissions 0600). Next: copy it to the VPS as /etc/tml-social/youtube.json (see the guide),")
    print("then delete this local copy and the client_secret file. Do not email, upload or paste it anywhere.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
