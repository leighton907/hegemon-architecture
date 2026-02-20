import json
import os


def load_memory(path):
    manifest_path = os.path.join(path, "namespace_manifest.json")

    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            return json.load(f)

    return {}
