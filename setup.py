import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# FIXME: add versioning form version.py file

setuptools.setup(
    name="streamlit-aggrid-redux",
    version="0.1.0",
    author="JD Wood",
    author_email="j.d.wood83@gmail.com",
    description="Streamlit component implementation of ag-grid",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jwood983/streamlit-aggrid",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "streamlit >= 0.75",
        "simplejson >= 3.0",
        "pandas >= 1.2",
        "pyarrow >= 11.0",
        "numpy"
    ]
)
