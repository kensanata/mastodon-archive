from setuptools import setup

setup(
    name='mastodon_archive',
    version='0.0.1',
    description="Utility for backing up your Mastodon content",
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
        "console_scripts": ["mastodon_archive=mastodon_archive:main"]
    },
    install_requires=[
        "mastodon.py",
        "pysmartdl",
        "progress",
        "html2text",
    ],
)
