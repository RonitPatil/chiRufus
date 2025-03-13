from setuptools import setup, find_packages

setup(
    name="Rufus",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "python-dotenv>=0.20.0",
    ],
    description="Rufus - an AI agent for scraping websites and generating structured content",
    author="Ronit Patil",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 