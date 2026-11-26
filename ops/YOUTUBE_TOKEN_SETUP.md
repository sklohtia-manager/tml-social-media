# YouTube token on your Mac: step by step

> **Status, 27 Nov 2026: done.** The owner completed the sign-in and confirmed the Two Market Ledger channel. The token is saved on the Mac (0600). Claude Code handles the transfer. **Don't ask the owner to repeat this** unless Google revokes access.

You do this once. Nothing secret is shown on screen or sent to Claude. Expect 10 minutes.

**Before you start:**
- The Google Cloud project `tml-publisher` is "In production" with the YouTube upload and read-only scopes (done 27 Nov 2026).
- Google's branding verification is **not** needed for this. Apps used by fewer than 100 people may click through the "unverified app" warning (Google help: "When is verification not needed").

## Step 1: download the Desktop client file
Google Cloud console → project **tml-publisher** → **Google Auth Platform → Clients** → your **Desktop** client → **Download JSON**. It saves as `client_secret_….json` in Downloads.

## Step 2: get the reviewed helper from a fixed, verified commit (into a private folder, not a Git folder)
Open **Terminal** and paste these lines **one at a time**:
```bash
mkdir -p ~/tml-private && cd ~/tml-private
```
```bash
curl -fsSL -o youtube_auth.py https://raw.githubusercontent.com/sklohtia-manager/tml-social-media/eaa81b7d48ccaa4dab2c43e20100820a0ffe2d84/worker/tools/youtube_auth.py
```
```bash
shasum -a 256 youtube_auth.py
```
The last command must print exactly:
`93c02792dbed1083cd7e2af70a3eb02fb87d3c80301a912c9c544875265edd30  youtube_auth.py`
If it doesn't match, stop and tell Claude.

The URL is pinned to reviewed commit `eaa81b7`, so later changes to the repository can't alter what you run. The helper uses only Python's standard library, talks only to Google, and prints no secrets.

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

## Step 5: move it to the VPS (Claude Code, with owner approval)
No copy goes through the shared `/tmp`. Install it straight from standard input, and refuse to overwrite an existing token:
```bash
ssh root@<vps> 'test ! -e /etc/tml-social/youtube.json'
ssh root@<vps> 'umask 077; install -o root -g tmlsocial -m 0640 /dev/stdin /etc/tml-social/youtube.json' < ~/tml-private/youtube.json
```
Then compare SHA-256 values only (never the contents), and check `stat` shows root:tmlsocial 640. The local copy is deleted only after the owner has seen the health result in step 6.

## Step 6: check it (still dry run, nothing is published)
On the VPS:
```bash
cd /opt/tml-social/worker && sudo -u tmlsocial env TMLPUB_DIR=/var/lib/tml-social TMLPUB_SECRETS=/etc/tml-social TMLPUB_REPO=/var/lib/tml-social/repo python3 -B -m tmlpub.cli health
```
Expect `"youtube": {"ok": true, "title": "Two Market Ledger", "match": true}`. Tell Claude the result (just ok/match, never the file).

**Revoking:** at any time, https://myaccount.google.com/permissions → Two Market Ledger → Remove access. Uploads stop immediately.
