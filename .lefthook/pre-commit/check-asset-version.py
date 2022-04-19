# -*- coding: utf-8 -*-
"""Checks that changes in assets/ are reflected in the asset-version file."""
import subprocess
import sys


def is_asset(path: str) -> bool:
    return path.startswith("assets/")


def get_changed_assets() -> list[str]:
    p = subprocess.run(['git', 'diff', '--name-only', '--cached'],
                       capture_output=True,
                       check=True)
    if p.stderr:
        raise Exception("Git diff has failed.")
    return [line for line in p.stdout.decode('utf8').splitlines()]


def has_changed_assets():
    return any(is_asset(file) for file in get_changed_assets())


def has_updated_asset_version():
    return any(file == "assets/_ch-asset-version.txt"
               for file in get_changed_assets())


def main():
    if has_changed_assets() and not has_updated_asset_version():
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
