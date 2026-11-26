# VPS publishing worker: dry-run installation (owner-approved 27 Nov 2026)

**What this installs:** an isolated service on the existing Hostinger VPS. It has its own system user `tmlsocial`, its own directories (`/opt/tml-social`, `/var/lib/tml-social`, `/etc/tml-social`) and its own systemd units (`tml-social*.service` and `.timer`).

**What it does not touch:** the production website, the beta website, Nginx, the private dashboard and the financial database. It opens no ports and publishes nothing. `TMLPUB_DRY_RUN=1` is set, and the list of live platforms is empty.

**Why it isn't installed yet:** this needs SSH access to the VPS, which exists only on the owner's Mac. No Mac was connected to the cloud session. Use one of the two options below.

## Option 1 (easiest): paste this prompt into Claude Code on your Mac
Open Terminal, run `claude` in any folder, and paste:

```
Install the Two Market Ledger publishing worker on my Hostinger VPS in DRY-RUN mode only. Use my usual SSH login for the VPS (the same one used for the beta). Do not change the website, beta site, Nginx, any database or any other service. Do not ask me for passwords in chat; if SSH asks for one, let me type it in the terminal.
1. ssh to the VPS. Report: hostname, OS, `python3 --version` (needs 3.9+), `git --version`, `free -m`, `df -h /`, `nproc`, and `systemctl list-units --type=service --state=running | head -40`.
2. Clone the public repo to a temporary review folder: `git clone --depth 1 https://github.com/sklohtia-manager/tml-social-media /root/tml-social-review` and print `git -C /root/tml-social-review log -1 --oneline`.
3. Run the tests there: `cd /root/tml-social-review/worker && python3 -B -m unittest discover -s tests` (must say OK).
4. Install: `sudo bash /root/tml-social-review/worker/install.sh --enable-timers`.
5. Verify, and show me the output of each:
   - `cat /etc/tml-social/worker.env` (must show TMLPUB_DRY_RUN=1 and an empty TMLPUB_PLATFORMS)
   - `systemctl is-enabled tml-social.timer tml-social-daily.timer` (both "enabled" means they start automatically after a restart)
   - `systemctl list-timers 'tml-social*'`
   - `grep Persistent /etc/systemd/system/tml-social*.timer`
   - `sudo systemctl start tml-social.service && journalctl -u tml-social -n 30 --no-pager` (expect "dryRun": true and 13 manual video records)
   - `cd /opt/tml-social/worker && sudo -u tmlsocial env TMLPUB_DIR=/var/lib/tml-social TMLPUB_SECRETS=/etc/tml-social TMLPUB_REPO=/var/lib/tml-social/repo python3 -B -m tmlpub.cli status`
   - pause test: run the same command with `pause`, then `run` (expect "paused": true), then `resume`
   - `... python3 -B -m tmlpub.cli health` (expect "not configured" for YouTube and Meta; that is correct before setup)
   - `... python3 -B -m tmlpub.cli report`
   - `systemctl status nginx --no-pager | head -5` and confirm the website is still up: `curl -sI https://twomarketledger.com | head -1` and `curl -sI https://beta.twomarketledger.com | head -1` (same status codes as before the install)
6. Do NOT reboot the VPS unless I say so. Do NOT set TMLPUB_DRY_RUN=0. Report every result back to me.
```

## Option 2: connect your Mac to the cloud session
Desktop app → Settings → Claude Code → Remote Control → add a folder (for example, the website checkout). Then tell the cloud session "Mac connected". It will run the same steps through your Mac and report back.

## Restart behaviour
- The timers are `enabled` (they start at boot) and `Persistent=true` (a cycle missed while the VPS was down runs at the next boot).
- The worker itself is a one-shot run every 5 minutes, so there is no long-running process to crash.
- A real reboot test briefly interrupts the website, so it is optional: if you want one, choose a quiet time (for example 1:00 AM, away from the 9:30 / 3:15 / 7:30 posts), run `sudo reboot`, then check `systemctl list-timers 'tml-social*'` once the VPS is back.

## Rollback (removes only the worker)
```
sudo systemctl disable --now tml-social.timer tml-social-daily.timer
sudo rm /etc/systemd/system/tml-social*.service /etc/systemd/system/tml-social*.timer && sudo systemctl daemon-reload
sudo rm -rf /opt/tml-social /var/lib/tml-social /etc/tml-social && sudo userdel tmlsocial
```
