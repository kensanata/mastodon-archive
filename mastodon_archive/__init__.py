import argparse
from . import archive
from . import text
from . import html
from . import media

def main():
    parser = argparse.ArgumentParser(
        description="""Archive your toots and favourites,
        and work with them.""")

    subparsers = parser.add_subparsers()


    parser_content = subparsers.add_parser(
        name='archive',
        help='archive your toots and favourites')
    parser_content.add_argument("--no-favourites", dest='skip_favourites', action='store_const',
                                const=True, default=False,
                                help='skip download of favourites')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=archive.archive)


    parser_content = subparsers.add_parser(
        name='media',
        help='download media referred to by toots in your archive')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=media.media)


    parser_content = subparsers.add_parser(
        name='text',
        help='search and export toots in the archive as plain text')
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


    parser_content = subparsers.add_parser(
        name='html',
        help='export toots and media in the archive as static HTML')
    parser_content.add_argument("--collection", dest='collection',
                                choices=['statuses', 'favourites'],
                                default='statuses',
                                help='export statuses or favourites')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=html.html)


    args = parser.parse_args()

    args.command(args)

if __name__ == "__main__":
    main()
