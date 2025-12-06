import os
import pathlib


def list_files_with_prefix(dir: pathlib.Path, asset_prefix: str) -> list[str]:
    return [f for f in os.listdir(dir) if f.startswith(asset_prefix)]
