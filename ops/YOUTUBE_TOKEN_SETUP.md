# YouTube token on your Mac: step by step

You do this once. Nothing secret is shown on screen or sent to Claude. Expect 10 minutes.

**Before you start:**
- The Google Cloud project `tml-publisher` is "In production" with the YouTube upload and read-only scopes (done 27 Nov 2026).
- Google's branding verification is **not** needed for this. Apps used by fewer than 100 people may click through the "unverified app" warning (Google help: "When is verification not needed").

## Step 1: download the Desktop client file
Google Cloud console → project **tml-publisher** → **Google Auth Platform → Clients** → your **Desktop** client → **Download JSON**. It saves as `client_secret_….json` in Downloads.

## Step 2: get the helper into a private folder (not a Git folder)
Open **Terminal** and paste:
```bash
mkdir -p ~/tml-private && cd ~/tml-private && curl -fsSLO https://raw.githubusercontent.com/sklohtia-manager/tml-social-media/main/worker/tools/youtube_auth.py
```

## Step 3: run it
```bash
python3 youtube_auth.py ~/Downloads/client_secret_*.json
```
Your browser opens:
1. Choose the Google account that owns the TML channel. If asked "Choose an account or brand account", choose **Two Market Ledger**.
2. "Google hasn't verified this app": click **Advanced → Go to Two Market Ledger (unsafe)**. It is your own app.
3. Tick **both** YouTube permissions and click **Continue**.
4. The tab says "response received". Return to Terminal.

## Step 4: confirm the channel
Terminal shows `Authorised YouTube channel: <name> (id UC…)`. Open the link it prints and check it is the Two Market Ledger channel, then type **YES**.

The script saves `youtube.json` (readable only by you) containing the confirmed channel ID. The worker refuses to upload if the token ever belongs to a different channel.

If it says a certificate error: run **Applications → Python 3.x → Install Certificates.command**, or use `/usr/bin/python3` instead of `python3`.

## Step 5: move it to the VPS (after the dry-run worker is installed)
Claude Code on your Mac can do this with your approval, or you can run:
```bash
scp ~/tml-private/youtube.json <admin>@<vps>:/tmp/ && ssh <admin>@<vps> 'sudo install -o root -g tmlsocial -m 640 /tmp/youtube.json /etc/tml-social/youtube.json && rm /tmp/youtube.json'
```
Then delete the local copies:
```bash
rm ~/tml-private/youtube.json ~/Downloads/client_secret_*.json
```

## Step 6: check it (still dry run, nothing is published)
On the VPS:
```bash
cd /opt/tml-social/worker && sudo -u tmlsocial env TMLPUB_DIR=/var/lib/tml-social TMLPUB_SECRETS=/etc/tml-social TMLPUB_REPO=/var/lib/tml-social/repo python3 -B -m tmlpub.cli health
```
Expect `"youtube": {"ok": true, "title": "Two Market Ledger", "match": true}`. Tell Claude the result (just ok/match, never the file).

**Revoking:** at any time, https://myaccount.google.com/permissions → Two Market Ledger → Remove access. Uploads stop immediately.
