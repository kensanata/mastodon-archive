import argparse
from . import backup
from . import text

def main():
    parser = argparse.ArgumentParser(
        prog="Mastodon Backup",
        description="""Archive your toots and favourites,
        and work with them.""")

    subparsers = parser.add_subparsers()

    parser_content = subparsers.add_parser('archive')
    parser_content.add_argument("user")
    parser_content.set_defaults(command=backup.backup)

    parser_content = subparsers.add_parser('text')
    parser_content.add_argument("--reverse", dest='reverse', action='store_const',
                                const=True, default=False,
                                help='reverse output, oldest first')
    parser_content.add_argument("--collection", dest='collection',
                                choices=['statuses', 'favourites'],
                                default='statuses',
                                help='export statuses or favourites')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.add_argument("pattern", nargs='*',
                                help='regular expressions used to filter output')
    parser_content.set_defaults(command=text.text)

    args = parser.parse_args()

    args.command(args)

if __name__ == "__main__":
    main()
