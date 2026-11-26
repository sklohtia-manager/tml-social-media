"""tmlpub CLI: run | health | report | status | pause [platform] | resume [platform]."""
import json
import sys

from . import config, store, worker


def main(argv=None):
    args = (argv if argv is not None else sys.argv[1:]) or ["status"]
    cmd = args[0]
    if cmd == "run":
        print(json.dumps(worker.run_once(), default=str))
    elif cmd == "health":
        print(json.dumps(worker.health()))
    elif cmd == "report":
        text = worker.daily_report()
        print(text)
        if "--send" in args:
            worker.alert(text)
    elif cmd == "status":
        with store.connect() as db:
            for r in db.execute("SELECT key,state,local_time,attempts,last_error FROM items ORDER BY local_time"):
                print(dict(r))
        print(json.dumps({"dryRun": config.DRY_RUN, "privateOnly": config.PRIVATE_ONLY, "livePlatforms": sorted(config.ENABLED_PLATFORMS),
                          "paused": config.pause_file().exists()}))
    elif cmd in ("pause", "resume"):
        path = config.pause_file(args[1] if len(args) > 1 else None)
        config.STATE.mkdir(parents=True, exist_ok=True)
        if cmd == "pause":
            path.write_text("paused\n")
        elif path.exists():
            path.unlink()
        print(f"{cmd}d {args[1] if len(args) > 1 else 'all platforms'}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
