from distutils.core import setup

setup(
    name='mastodon_backup',
    version='0.0.1',
    description="Utility for backing up your Mastodon content.",
    author="Alex Schroeder",
    packages=["mastodon_backup"],
    entry_points={
        "console_scripts": ["mastodon_backup=mastodon_backup:main"]
    },
    install_requires=[
        "mastodon.py",
        "pysmartdl",
        "progress",
        "html2text",
        
    ],
)
