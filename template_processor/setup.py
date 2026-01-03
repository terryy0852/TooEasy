from setuptools import setup, find_packages
import os

# Read the README.md file for long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read the requirements.txt file for dependencies
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r', encoding='utf-8') as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="template-processor",
    version="0.1.0",
    author="Template Processor Team",
    author_email="info@templateprocessor.com",
    description="A simple yet powerful template processing engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/templateprocessor/template-processor",
    packages=find_packages(),
    package_data={
        'template_processor': ['templates/*'],
    },
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'template-processor=template_processor.cli:main',  # Optional CLI entry point
        ],
    },
)
