"""

Testing implementation of create_sandbox_directory

"""

import os
import sys
from re import T

sys.path.append("src/")
from dataclasses import dataclass

from create_dsa_sandbox import run


@dataclass
class ArgsObject:
    dsa_url: str = "https://sunycell.ccr.buffalo.edu/api/v1"
    username: str | None = None
    password: str | None = None
    item_id: str = "6a8d9cf7d5c6cb308f3bdb69"
    download_annotations: bool = True
    download_slide: bool = True
    download_files: bool = True
    output_path: str = os.path.join(os.path.dirname(__file__), "test_item")


def test(args):
    run(args)


if __name__ == "__main__":
    test(ArgsObject)
