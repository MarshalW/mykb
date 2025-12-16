from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mykb",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Wikipedia术语词库生成工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marshal/mykb",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "wikipedia",
        "markdownify",
        "pandas",
        "openpyxl",
        "tqdm",
        "wikitextparser",
        "bleach"
    ],
    entry_points={
        "console_scripts": [
            "mykb=mykb.cli:main",
        ],
    },
)