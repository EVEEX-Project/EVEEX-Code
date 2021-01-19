import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EVEEX", # Replace with your own username
    version="0.1.0.5",
    author="EVEEX Team",
    author_email="alexandre.froehlich@ensta-bretagne.org",
    description="This project is a proof of concept (POC) for the whole project that consist in making a embedded video encoder and decoder on two different FPGA.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EVEEX-Project/EVEEX-Code",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)