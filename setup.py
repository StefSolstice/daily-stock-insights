from setuptools import setup, find_packages

setup(
    name="daily-stock-insights",
    version="0.1.0",
    description="每日股票分析和技术指标监控工具",
    author="OpenClaw Assistant",
    packages=find_packages(),
    install_requires=[
        "tushare",
        "pandas",
        "numpy",
        "requests",
        "matplotlib"
    ],
    entry_points={
        "console_scripts": [
            "stock-insights=main:main",
        ],
    },
    python_requires=">=3.8",
)
