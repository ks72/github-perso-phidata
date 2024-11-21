# A minimal setup.py file for supporting editable installs

from setuptools import setup, find_packages

setup(
    name="my-learning-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "phidata",
        "streamlit",
        "duckduckgo-search",
        "wikipedia",
        "python-dotenv",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A learning agent built with phidata",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ks72/github-perso-phidata",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
