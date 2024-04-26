from setuptools import setup, find_packages

setup(
    name="gigax",
    version="0.1",
    description="Call LLM-powered NPCs from your game, at runtime.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/GigaxGames/gigax",
    author="Gigax team",
    author_email="tristan@gig.ax",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "outlines",
        "pydantic",
        "openai",
        "outlines",
        "transformers",
        "llama-cpp-python",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
    zip_safe=False,
)
