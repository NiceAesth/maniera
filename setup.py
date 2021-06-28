import pathlib
from setuptools import setup

with open('README.md', encoding="utf-8") as f:
    README = f.read()

# This call to setup() does all the work
setup(
    name="maniera",
    version="1.0.2",
    description="An osu! Mania PP and star rating calculator.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/NiceAesth/maniera",
    author="Nice Aesthetics",
    author_email="nice@aesth.dev",
    license="GPLv3+",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["maniera"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "maniera=maniera.__main__:main",
        ]
    },
    keywords="osu! osu"
)