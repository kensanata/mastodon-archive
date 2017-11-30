import argparse
import .backup

def main():
    parser = argparse.ArgumentParser("Mastodon Backup")

    subparsers = parser.add_subparsers()

    parser_content = subparsers.add_parser('content')
    parser_content.add_argument("user")
    parser_content.set_defaults(command=backup.backup)

    args = parser.parse_args()

    args.command()

if __name__ == "__main__":
    main()
    