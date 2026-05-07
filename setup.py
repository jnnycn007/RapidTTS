# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import sys
from pathlib import Path
from typing import List, Union

import setuptools
from get_pypi_latest_version import GetPyPiLatestVersion


def read_txt(txt_path: Union[Path, str]) -> List[str]:
    with open(txt_path, "r", encoding="utf-8") as f:
        data = [v.rstrip("\n") for v in f]
    return data


def get_readme():
    root_dir = Path(__file__).resolve().parent
    readme_path = str(root_dir / "docs" / "doc_whl_rapidtts.md")
    print(readme_path)
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()
    return readme


MODULE_NAME = "rapidtts"

obtainer = GetPyPiLatestVersion()
try:
    latest_version = obtainer(MODULE_NAME)
except Exception:
    latest_version = "0.0.0"
VERSION_NUM = obtainer.version_add_one(latest_version, add_patch=True)

if len(sys.argv) > 2:
    match_str = " ".join(sys.argv[2:])
    matched_versions = obtainer.extract_version(match_str)
    if matched_versions:
        VERSION_NUM = matched_versions
sys.argv = sys.argv[:2]

setuptools.setup(
    name=MODULE_NAME,
    version=VERSION_NUM,
    platforms="Any",
    description="A text-to-speech framework for fast and high-quality speech synthesis.",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    author="SWHL",
    author_email="liekkaskono@163.com",
    url="https://github.com/RapidAI/RapidTTS",
    license="Apache-2.0",
    include_package_data=True,
    install_requires=read_txt("requirements.txt"),
    packages=setuptools.find_packages(include=[MODULE_NAME, f"{MODULE_NAME}.*"]),
    package_data={MODULE_NAME: ["configs/*.yaml"]},
    entry_points={"console_scripts": ["rapidtts=rapidtts.cli:main"]},
    keywords=["tts,rapidtts,melotts"],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.9,<4",
)
