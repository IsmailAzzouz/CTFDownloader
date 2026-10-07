#!/usr/bin/env python3
"""Convenience script for downloading challenges (calls `ctfdownloader download`)."""

import sys
from ctfdownloader.cli import main

if __name__ == "__main__":
    main(["download"] + sys.argv[1:])
