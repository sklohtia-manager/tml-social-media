#!/usr/bin/env bash
# Installs the TML publishing worker on the VPS. Leaves it DISABLED and in DRY-RUN mode.
# Usage (owner-approved, from a reviewed checkout): sudo bash worker/install.sh [--enable-timers]
# Never touches the website, its database, Nginx or other sites. No ports are opened.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
id tmlsocial >/dev/null 2>&1 || useradd --system --home /var/lib/tml-social --shell /usr/sbin/nologin tmlsocial
install -d -o tmlsocial -g tmlsocial -m 750 /var/lib/tml-social
install -d -o root -g tmlsocial -m 750 /etc/tml-social
install -d -o root -g root -m 755 /opt/tml-social
rm -rf /opt/tml-social/worker.new && cp -r "$SRC" /opt/tml-social/worker.new && rm -rf /opt/tml-social/worker && mv /opt/tml-social/worker.new /opt/tml-social/worker
if [ ! -d /var/lib/tml-social/repo/.git ]; then
  sudo -u tmlsocial git clone --depth 1 https://github.com/sklohtia-manager/tml-social-media /var/lib/tml-social/repo
fi
[ -f /etc/tml-social/worker.env ] || printf 'TMLPUB_DRY_RUN=1\nTMLPUB_PLATFORMS=\nTMLPUB_ALERT_COMMAND=\n' > /etc/tml-social/worker.env
chown root:tmlsocial /etc/tml-social/worker.env && chmod 640 /etc/tml-social/worker.env
cp "$SRC"/systemd/tml-social*.service "$SRC"/systemd/tml-social*.timer /etc/systemd/system/
systemctl daemon-reload
echo "Installed (dry run). Run one cycle: sudo systemctl start tml-social.service && journalctl -u tml-social -n 20"
if [ "${1:-}" = "--enable-timers" ]; then
  systemctl enable --now tml-social.timer tml-social-daily.timer
  echo "Timers enabled. Live publishing is still off until /etc/tml-social/worker.env sets TMLPUB_DRY_RUN=0 and TMLPUB_PLATFORMS."
fi
