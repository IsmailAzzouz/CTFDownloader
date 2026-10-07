#!/usr/bin/env python3
"""Convenience script for listing challenges (calls `ctfdownloader list`)."""

import sys
from ctfdownloader.cli import main

if __name__ == "__main__":
    main(["list"] + sys.argv[1:])
