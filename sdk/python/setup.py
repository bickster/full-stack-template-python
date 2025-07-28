"""Setup configuration for FullStack API Python Client."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fullstack-api-client",
    version="1.0.0",
    author="FullStack Team",
    author_email="support@fullstack.com",
    description="Python client library for FullStack API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fullstack-app",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "typing-extensions>=4.0.0;python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fullstack-app/issues",
        "Source": "https://github.com/yourusername/fullstack-app",
    },
)
