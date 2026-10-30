from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mastodon_archive',
    version='1.4.9',
    description="Utility for backing up your Mastodon content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Schroeder",
    author_email="alex@gnu.org",
    url='https://github.com/kensanata/mastodon-archive#mastodon-archive',
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Development Status :: 5 - Production/Stable',
    ],
    license="GPL-3.0-or-later",
    packages=["mastodon_archive"],
    entry_points={
        "console_scripts": ["mastodon-archive=mastodon_archive:main"]
    },
    install_requires=[
        "mastodon.py",
        "progress",
        "html2text",
    ],
)
