#!/usr/bin/env python3

"""Run blueman-manager directly from a configured source checkout."""

import gettext
import logging
import sys

gettext.textdomain("blueman")

from blueman.Functions import create_logger, create_parser, set_proc_title
from blueman.main.Manager import Blueman


def main() -> int:
    args = create_parser().parse_args()
    log_level = getattr(logging, args.LEVEL.upper(), logging.WARNING)
    create_logger(log_level, "blueman-manager", syslog=args.syslog)

    app = Blueman()
    set_proc_title()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
