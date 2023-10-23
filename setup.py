import setuptools


def get_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()


# FIXME: add versioning form version.py file

setuptools.setup(
    name="streamlit-aggrid-redux",
    version="2023.10",
    author="JD Wood",
    author_email="j.d.wood83@gmail.com",
    description="Reimplementation of ag-grid component for streamlit",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/jwood983/streamlit-aggrid-redux",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        "streamlit >= 1.27",
        "pandas >= 1.2",
        "pyarrow >= 11.0",
        "numpy >= 1.24",
        "python-decouple >= 3.8"
    ]
)
