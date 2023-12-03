from setuptools import setup, find_packages

setup(
    name="algtestprocess",
    version="0.1.0",
    packages=find_packages(),
    description="A Python package for algtestprocess",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tomas Jaros",
    author_email="tjaros.822@gmail.com",
    url="https://github.com/crocs-muni/algtest-pyprocess",
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "pyprocess=pyprocess:main",
        ],
    },
)
