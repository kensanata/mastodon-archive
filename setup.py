from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mastodon_archive',
    version='1.3.2',
    description="Utility for backing up your Mastodon content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Schroeder",
    author_email="alex@gnu.org",
    url='https://github.com/kensanata/mastodon-backup#mastodon-archive',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Development Status :: 5 - Production/Stable',
    ],
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
