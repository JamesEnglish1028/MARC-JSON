from setuptools import setup, find_packages

setup(
    name="marc-converter",
    version="0.1.0",
    description="Convert MARC records to KBART/Excel/CSV inventory files via Flask web app.",
    author="James English",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "requests",
        "pymarc",
        "openpyxl"
    ],
    entry_points={
        "console_scripts": [
            "marc-converter=marc_converter.__main__:app.run"
        ]
    },
)