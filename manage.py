#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from pathlib import Path


def main():
    ROOT_DIR = Path(__file__).resolve().parent
    SRC_DIR = ROOT_DIR / "src"

    sys.path.append(str(SRC_DIR))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.core.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
