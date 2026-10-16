#!/usr/bin/env python3
"""Read the build-neutral branding input for Meson and Autoconf."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex


KEYS = {
    "display_name": "BRAND_DISPLAY_NAME",
    "description": "BRAND_DESCRIPTION",
    "notification_app_name": "BRAND_NOTIFICATION_APP_NAME",
    "icon_name": "BRAND_ICON_NAME",
    "website": "BRAND_WEBSITE",
}


def load(path: Path) -> dict[str, str]:
    values = json.loads(path.read_text(encoding="utf-8"))
    missing = KEYS.keys() - values.keys()
    if missing:
        raise ValueError(f"Missing branding keys: {', '.join(sorted(missing))}")
    if any(not isinstance(values[key], str) or not values[key] for key in KEYS):
        raise ValueError("Branding values must be non-empty strings")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("branding", type=Path)
    parser.add_argument("key", nargs="?", choices=KEYS)
    parser.add_argument("--shell", action="store_true")
    args = parser.parse_args()
    values = load(args.branding)

    if args.shell:
        if args.key is not None:
            parser.error("key and --shell are mutually exclusive")
        for key, variable in KEYS.items():
            print(f"{variable}={shlex.quote(values[key])}")
    elif args.key is not None:
        print(values[args.key])
    else:
        parser.error("provide a key or --shell")


if __name__ == "__main__":
    main()
