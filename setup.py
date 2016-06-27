from setuptools import setup, find_packages

setup(
    name="pymfps",
    py_modules=["mfps"],
    entry_points={
        "console_scripts": [
            "pymfps=mfps:main",
        ],
    },
)
