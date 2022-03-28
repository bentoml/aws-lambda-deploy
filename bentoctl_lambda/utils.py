import os

import fs
import boto3
from bentoml.bentos import Bento


def get_metadata(path: str):
    metadata = {}

    bento = Bento.from_fs(fs.open_fs(path))
    metadata["tag"] = bento.tag
    metadata["bentoml_version"] = ".".join(bento.info.bentoml_version.split(".")[:3])

    python_version_txt_path = "env/python/version.txt"
    python_version_txt_path = os.path.join(path, python_version_txt_path)
    with open(python_version_txt_path, "r") as f:
        python_version = f.read()
    metadata["python_version"] = ".".join(python_version.split(".")[:2])

    return metadata
