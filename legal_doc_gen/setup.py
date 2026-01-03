from setuptools import setup, find_packages

setup(
    name="legal-doc-gen",
    version="0.1.0",
    description="A powerful template processing engine for creating legal documents",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Legal Document Generator Team",
    author_email="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # No external dependencies required
    ],
    extras_require={
        "test": [
            "pytest>=6.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Text Processing :: Markup",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
