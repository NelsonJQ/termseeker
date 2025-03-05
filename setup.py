from setuptools import setup, find_packages

setup(
    name="termun",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-docx",
        "pymupdf4llm",
        "requests",
        "beautifulsoup4",
        "html2text",
        "markdown2",
        "sentence-transformers",
        "scikit-learn",
        "duckduckgo-search",
        "polars"
    ],
    entry_points={
        "console_scripts": [
            "termun-cli=termun.src.cli:main_cli",
        ],
    },
    author="Nelson Jaimes Quintero",
    author_email="nelsonjaimesq@gmail.com",
    description="UN Terminology checker and corrector for parallel texts",
    url="https://github.com/NelsonJQ/termun",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
