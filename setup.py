from setuptools import setup, find_packages

setup(
    name="algtestprocess",
    version="0.1.6",
    packages=find_packages(),
    description="A Python package for algtestprocess",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tomas Jaros",
    author_email="tjaros.822@gmail.com",
    url="https://github.com/crocs-muni/algtest-pyprocess",
    install_requires=[
        "dominate~=2.6.0",
        "click~=8.1.2",
        "overrides~=6.1.0",
        "pandas~=1.4.2",
        "matplotlib~=3.5.1",
        "PyYAML~=6.0",
        "numpy~=1.23.4",
        "checksumdir~=1.2.0",
        "tabulate~=0.9.0",
        "seaborn",
    ],
    scripts=["bin/pyprocess"],
)
