from setuptools import setup, find_packages

setup(
    name = "integratedblog",
    version = "0.1",
    packages = find_packages(),
    install_requires = [
        "Flask>=0.11.1",
        "oauth2client>=4.0.0",
        "BeautifulSoup4>=4.5.0",
        "markdown2>=2.3.8",
        "peewee>=3.13.2"
    ]
)
