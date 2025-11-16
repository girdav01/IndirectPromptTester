"""Setup script for Indirect Prompt Tester."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="indirect-prompt-tester",
    version="0.1.0",
    description="Framework for generating and testing applications against indirect prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/IndirectPromptTester",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "boto3>=1.28.0",
        "pillow>=10.0.0",
        "python-docx>=1.1.0",
        "openpyxl>=3.1.0",
        "pypdf2>=3.0.0",
        "python-pptx>=0.6.23",
        "moviepy>=1.0.3",
        "pydub>=0.25.1",
        "requests>=2.31.0",
        "click>=8.1.7",
        "pyyaml>=6.0.1",
        "twilio>=8.10.0",
        "python-dotenv>=1.0.0",
        "jinja2>=3.1.2",
        "markdown>=3.5.1",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.1",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ipt=indirect_prompt_tester.cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

