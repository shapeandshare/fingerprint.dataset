import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shapeandshare-fingerprint-dataset",
    version="0.3.0",
    author="Joshua C. Burt",
    author_email="joshburt@shapeandshare.com",
    description="Generates file hash reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    python_requires=">=3.9",
    install_requires=["pydantic>=1.9.0", "tqdm>=4.63.0", "pandas>=1.4.1"],
)
