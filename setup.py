#!/usr/bin/env python3
"""Setup script for py-dlp."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="py-dlp",
    version="2026.09.04",
    author="Py-dlp Developers",
    description="The Ultimate, Next-Generation Media Extractor and Downloader Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Beasgohan-code/Py-dlp",
    packages=find_packages(include=["pydlp", "pydlp.*"]),
    package_data={
        "pydlp": ["server/static/*"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pydlp=pydlp.main:main",
            "py-dlp=pydlp.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
