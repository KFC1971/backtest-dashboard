from setuptools import setup, find_packages

setup(
    name="smart-money",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "numpy",
        "yfinance",
        "python-dateutil",
        "pytz",
    ],
    entry_points={
        'console_scripts': [
            'smart-money=smart_money.cli:main',
        ],
    },
)
