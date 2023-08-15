from distutils.core import setup

setup(
    name="staticmap2",
    packages=["staticmap2"],
    version="0.2",
    description="A small, python-based library for creating map images with lines and markers.",
    author="Christoph Lingg",
    author_email="christoph@komoot.de",
    url="https://github.com/komoot/staticmap",
    download_url="https://github.com/komoot/staticmap/tarball/0.1",
    keywords="static map image osm",
    classifiers=[],
    install_requires=["Pillow", "requests", 'futures;python_version<"3.2"'],
)
