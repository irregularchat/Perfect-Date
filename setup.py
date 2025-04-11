from setuptools import setup, find_packages

setup(
    name="perfect-date-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gradio>=4.14.0",
        "openai>=1.14.0",
        "python-dotenv>=1.0.1",
    ],
    author="Perfect Date Generator Team",
    author_email="example@example.com",
    description="A web application that generates personalized date ideas based on preferences",
    keywords="date, ideas, generator, openai, gradio",
    url="https://github.com/yourusername/perfect-date-generator",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 