import setuptools
 
with open("README.md", "r") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="opponent_adjusted_nba_scraper",
    version="0.0.1",
    author="Oscar Gutierrez Altamirano",
    author_email="oscargutierreza617@gmail.com",
    description="A Python client for scraping data from stats.nba.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oscarg617/opponent_adjusted_nba_scraper",
    packages=setuptools.find_packages(),
 
    install_requires=[
    "pandas==1.5.2",
    "requests==2.28.1",
    "six==1.16.0",
    "Unidecode==1.3.6"
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
)