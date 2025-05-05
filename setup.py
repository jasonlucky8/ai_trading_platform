from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="ai_trading_platform",
    version="0.1.0",
    author="AI Trading Team",
    author_email="example@example.com",
    description="AI-driven quantitative trading platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai_trading_platform",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-trader=src.ui.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 