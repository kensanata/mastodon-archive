import argparse
from . import backup


def main():
    parser = argparse.ArgumentParser("Mastodon Backup")

    subparsers = parser.add_subparsers()

    parser_content = subparsers.add_parser('archive')
    parser_content.add_argument("user")
    parser_content.set_defaults(command=backup.backup)

    args = parser.parse_args()

    args.command(args)


if __name__ == "__main__":
    main()
