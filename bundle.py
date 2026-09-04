#!/usr/bin/env python3
"""Builds a standalone executable ZipApp bundle for Py-dlp."""

import os
import shutil
import tempfile
import zipapp

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
SOURCE_DIR = os.path.join(ROOT_DIR, "pydlp")


def build_zipapp():
    os.makedirs(DIST_DIR, exist_ok=True)
    target_path = os.path.join(DIST_DIR, "pydlp")

    temp_dir = tempfile.mkdtemp(prefix="pydlp_bundle_")
    try:
        # Copy pydlp package into bundle root
        shutil.copytree(SOURCE_DIR, os.path.join(temp_dir, "pydlp"))

        # Create __main__.py at root of zipapp
        with open(os.path.join(temp_dir, "__main__.py"), "w", encoding="utf-8") as f:
            f.write("from pydlp.main import main\nimport sys\n\nif __name__ == '__main__':\n    sys.exit(main())\n")

        # Compile zipapp with python3 interpreter shebang
        zipapp.create_archive(
            source=temp_dir,
            target=target_path,
            interpreter="/usr/bin/env python3",
            compressed=True,
        )
        os.chmod(target_path, 0o755)
        print(f"Successfully generated standalone executable: {target_path}")

        # Also create a .zipapp alias
        shutil.copy(target_path, os.path.join(DIST_DIR, "pydlp.zipapp"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    build_zipapp()
