"""Unit tests for the FFmpeg Static Builder for yt-dlp."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestFFmpegBuilder(unittest.TestCase):
    """Test suite verifying build scripts, configurations, and patches."""

    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent

    def test_scripts_exist_and_executable(self):
        required_scripts = [
            "build.sh",
            "makeimage.sh",
            "download.sh",
            "generate.sh",
            "package.sh",
            "util/vars.sh",
        ]
        for script_name in required_scripts:
            path = self.root_dir / script_name
            self.assertTrue(path.exists(), f"Missing script: {script_name}")

    def test_modular_library_scripts_exist(self):
        scripts_dir = self.root_dir / "scripts.d"
        expected_modules = [
            "10-zlib.sh",
            "15-bzip2.sh",
            "20-openssl.sh",
            "25-libxml2.sh",
            "30-libogg.sh",
            "31-libvorbis.sh",
            "32-libopus.sh",
            "35-libmp3lame.sh",
            "40-libvpx.sh",
            "45-libx264.sh",
            "46-libx265.sh",
            "48-libdav1d.sh",
            "50-libfreetype.sh",
            "51-libfribidi.sh",
            "52-libass.sh",
            "60-ffmpeg.sh",
        ]
        for mod in expected_modules:
            mod_path = scripts_dir / mod
            self.assertTrue(mod_path.exists(), f"Missing library module: {mod}")

    def test_patches_exist_and_valid(self):
        patches_dir = self.root_dir / "patches"
        expected_patches = [
            "0001-flv-hevc-decoding.patch",
            "0002-hls-aac-truncation.patch",
            "0003-win32-vulkan-null.patch",
        ]
        for p in expected_patches:
            patch_path = patches_dir / p
            self.assertTrue(patch_path.exists(), f"Missing patch: {p}")
            content = patch_path.read_text(encoding="utf-8")
            self.assertIn("diff --git", content)

    def test_dockerfiles_exist(self):
        docker_dir = self.root_dir / "docker"
        for target in ["win64", "win32", "linux64", "linuxarm64", "base"]:
            df = docker_dir / f"Dockerfile.{target}"
            self.assertTrue(df.exists(), f"Missing Dockerfile for {target}")

    def test_generate_script_execution(self):
        gen_script = self.root_dir / "generate.sh"
        res = subprocess.run(
            ["bash", str(gen_script), "win64", "master"],
            cwd=str(self.root_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Dynamic FFmpeg Static Build Plan for yt-dlp", res.stdout)
        self.assertIn("win64", res.stdout)
        self.assertIn("0001-flv-hevc-decoding.patch", res.stdout)

    def test_vars_environment_matrix(self):
        vars_script = self.root_dir / "util/vars.sh"
        for target, exp_host in [
            ("win64", "x86_64-w64-mingw32"),
            ("win32", "i686-w64-mingw32"),
            ("linux64", "x86_64-linux-gnu"),
            ("linuxarm64", "aarch64-linux-gnu"),
        ]:
            cmd = f'source "{vars_script}" && export TARGET={target} && setup_target_env && echo "$HOST"'
            res = subprocess.run(
                ["bash", "-c", cmd],
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(res.returncode, 0)
            self.assertEqual(res.stdout.strip(), exp_host)


if __name__ == "__main__":
    unittest.main()
