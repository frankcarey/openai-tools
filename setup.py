import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openai-tools-frankcarey",
    version="0.0.1",
    author="Frank Carey",
    author_email="",
    description="Unofficial OpenAI client.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frankcarey/",
    packages=setuptools.find_packages([
        'requests',
        'marshmallow'
    ]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
