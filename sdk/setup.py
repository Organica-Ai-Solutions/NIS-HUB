"""
Setup script for NIS HUB SDK

This package provides a Python SDK for connecting NIS nodes 
to the central NIS HUB coordination system.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nis-hub-sdk",
    version="1.0.0",
    author="Organica AI Solutions",
    author_email="contact@organica-ai.com",
    description="Python SDK for connecting to NIS HUB coordination system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Organica-Ai-Solutions/NIS-HUB",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.25.0",
        "websockets>=12.0",
        "pydantic>=2.5.0",
        "python-json-logger>=2.0.0",
        "asyncio-mqtt>=0.16.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
        ],
        "examples": [
            "rich>=13.7.0",
            "typer>=0.9.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "nis-hub-client=nis_hub_sdk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nis_hub_sdk": ["py.typed"],
    },
) 