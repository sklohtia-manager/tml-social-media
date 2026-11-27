# Beta trial completion report: arrangements (owner-approved 28 Nov 2026)

**Due:** Thu 3 Dec 2026, **8:45 AM Melbourne** (trial start 26 Nov 08:45:11 AEDT; seven days). Read-only; no feature development during the trial.

## What is scheduled (confirmed 28 Nov 08:52, one-time tasks on the owner's cloud account)
| Time (Melbourne) | Task | Trigger | What it does |
|---|---|---|---|
| Sat 28 Nov 9:45 AM | Verify the Morning edition | `trig_01CuSChj9z25i4xjFvM3KV2q` | Read-only: Morning routine last run, Buffer posts per channel, duplicates; records a miss if there was one; never posts |
| Thu 3 Dec **8:30 AM** | **Owner reminder** | `trig_01MZxF77aC3vdbbPV8EnA73o` | Tells the owner the report is due at 8:45 AM, who runs it, where the result appears |
| Thu 3 Dec **8:50 AM** | Delivery check | `trig_01PiL2m9ZNLVGCD1WRy3uPgw` | Reads issue #17; summarises the report if posted, otherwise says it was not delivered and names the command and owner of the task |

**Important limit:** these cloud tasks cannot reach the server. The **report itself is not scheduled to run automatically**; it needs Claude Code (or Codex) on the Mac with SSH access. The tasks above remind, and check that it was delivered. They are **not** the execution.

## Assigned execution: Claude Code (Mac, SSH to the VPS)
At 8:45 AM Melbourne on Thu 3 Dec, with the owner's standing approval for this read-only run:
1. Run (read-only, from `news/BETA_TRIAL_START_REPORT.md`):
   ```
   sudo -u ledgernews env LEDGER_NEWS_DIR=/var/lib/two-market-ledger-news LEDGER_BETA_ENVIRONMENT=1 /usr/bin/python3 -B /opt/two-market-ledger-beta/current/ops/news/newsctl.py trial-report --days 7
   ```
2. Also record read-only: `systemctl is-active tml-news.timer tml-news-health.timer tml-news-backup.timer`; run, failure and alert counts since 26 Nov 08:45; the homepage "Last updated" age; the last backup time and integrity result; the production backup status; whether the 28 Nov reboot window happened and the timers recovered.
3. Post the result on issue #17 (counts, failures, alerts, freshness, recommendation). **Do not** change sources, rules, services or the website. **Do not** activate production publishing or indexing.
4. If it cannot be run at 8:45, say so on #17 immediately so the 8:50 AM delivery check reports it correctly.

## Decision it leads to (owner)
Continue, extend or conclude the beta trial. **Production news authorisation and website deployment remain separate decisions** (`OWNER_DECISIONS_2026-11-28.md` items 1–3).
