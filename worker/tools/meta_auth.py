#!/usr/bin/env python3
"""Run on the owner's Mac (once). Creates meta.json (Page id, Instagram user id, long-lived Page token) without printing secrets.

  python3 meta_auth.py

You will be asked (hidden input) for: the App ID, the App Secret, and a short-lived User access token from the Graph API
Explorer with these permissions: pages_show_list, pages_read_engagement, pages_manage_posts, publish_video,
instagram_basic, instagram_content_publish, business_management. Writes ./meta.json (0600) for /etc/tml-social/meta.json.
"""
import getpass
import json
import os
import sys
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v21.0"


def get(path, **params):
    return json.load(urllib.request.urlopen(f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}"))


def main():
    app_id = getpass.getpass("App ID (hidden): ").strip()
    secret = getpass.getpass("App Secret (hidden): ").strip()
    short = getpass.getpass("Short-lived User token from Graph API Explorer (hidden): ").strip()
    long_user = get("oauth/access_token", grant_type="fb_exchange_token", client_id=app_id, client_secret=secret,
                    fb_exchange_token=short)["access_token"]
    pages = get("me/accounts", access_token=long_user, fields="id,name,access_token").get("data", [])
    page = next((p for p in pages if p["name"].strip().lower() == "two market ledger"), None)
    if not page:
        sys.exit("The 'Two Market Ledger' Page was not found for this user. Check the token's Page permissions.")
    ig = get(page["id"], fields="instagram_business_account", access_token=page["access_token"]).get("instagram_business_account")
    if not ig:
        sys.exit("No Instagram professional account is linked to the Page. Link it in the Page settings and run again.")
    fd = os.open("meta.json", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"page_id": page["id"], "ig_user_id": ig["id"], "page_token": page["access_token"]}, f)
    print(f"Wrote ./meta.json (0600) for Page '{page['name']}'. Copy it to the VPS as /etc/tml-social/meta.json. Do not share it.")


if __name__ == "__main__":
    main()
