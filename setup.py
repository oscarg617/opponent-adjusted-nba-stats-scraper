'''Setup.py'''
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="opponent_adjusted_nba_scraper",
    version="1.0.22",
    author="Oscar Gutierrez Altamirano",
    author_email="oscargutierreza617@gmail.com",
    description="A Python client for scraping data from stats.nba.com and \
        opponent-adjusting players' stats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),

    install_requires=[
    "pandas==2.1.0",
    "requests==2.31.0",
    "six==1.16.0",
    "Unidecode==1.3.8"
    ],

    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    keywords=[
        "nba",
        "nba.com",
        "stats.nba.com",
        "sports",
        "basketball",
        ],

    package_data = {'opponent_adjusted_nba_scraper': ['opponent_adjusted_nba_scraper/utils/*.txt']}
)
