#!/usr/bin/env bash
# Run on the owner's Mac (Claude Code can run it with approval). Securely stages ONE finished Media Studio export on the VPS.
#   bash stage_video.sh ~/Documents/Projects/TML-Media-Studio/exports/<contentId>  <admin>@<vps>
# The folder must contain video.mp4 and manifest.json (Media Studio export contract, ops/MEDIA_STUDIO_HANDOFF.md), and may
# contain captions.srt and thumbnail.jpg. Nothing is committed to Git; the copy goes over SSH to /var/lib/tml-social/incoming/<contentId>/.
set -euo pipefail
DIR="${1:?export folder}"; TARGET="${2:?admin@vps}"
ID="$(basename "$DIR")"
[[ "$ID" =~ ^TML-[A-Z0-9-]{2,40}$ ]] || { echo "Folder name must be the content ID (TML-...)"; exit 1; }
[ -f "$DIR/video.mp4" ] && [ -f "$DIR/manifest.json" ] || { echo "Need video.mp4 and manifest.json"; exit 1; }
python3 - "$DIR" "$ID" <<'PY'
import hashlib, json, sys
d, cid = sys.argv[1], sys.argv[2]
m = json.load(open(f"{d}/manifest.json"))
assert m.get("contentId") == cid, "manifest contentId must equal the folder name"
assert m.get("asset") == "video.mp4", "manifest asset must be video.mp4"
assert m.get("language") in ("en", "hi"), "manifest language must be en or hi"
h = hashlib.sha256(open(f"{d}/video.mp4", "rb").read()).hexdigest()
assert m.get("assetSha256") == h, f"assetSha256 does not match video.mp4 ({h})"
print("manifest OK:", cid, m.get("language"), m.get("title"))
PY
if command -v ffprobe >/dev/null; then
  ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt -show_entries format=duration -of default=nw=1 "$DIR/video.mp4"
else
  echo "ffprobe not installed: format not checked (brew install ffmpeg to enable)"
fi
read -r -p "Stage $ID on $TARGET? Type YES: " ok; [ "$ok" = "YES" ] || exit 1
ssh "$TARGET" "mkdir -m 700 /tmp/tml-stage-$ID"
scp -q "$DIR"/video.mp4 "$DIR"/manifest.json "$TARGET:/tmp/tml-stage-$ID/"
for f in captions.srt thumbnail.jpg; do if [ -f "$DIR/$f" ]; then scp -q "$DIR/$f" "$TARGET:/tmp/tml-stage-$ID/"; fi; done
ssh "$TARGET" "sudo install -d -o tmlsocial -g tmlsocial -m 750 /var/lib/tml-social/incoming/$ID && sudo install -o tmlsocial -g tmlsocial -m 640 /tmp/tml-stage-$ID/* /var/lib/tml-social/incoming/$ID/ && rm -rf /tmp/tml-stage-$ID && sudo ls -l /var/lib/tml-social/incoming/$ID"
echo "Staged. The worker picks it up on its next 5-minute cycle (dry run unless live mode is enabled)."
