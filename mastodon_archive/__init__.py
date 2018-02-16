import argparse
from . import archive
from . import text
from . import html
from . import media
from . import expire
from . import report

def main():
    parser = argparse.ArgumentParser(
        description="""Archive your toots and favourites,
        and work with them.""",
        epilog="""Once you have created archives in the current directory, you can
        use 'all' instead of your account and the commands will be run
        once for every archive in the directory.""")

    subparsers = parser.add_subparsers()


    parser_content = subparsers.add_parser(
        name='archive',
        help='archive your toots and favourites')
    parser_content.add_argument("--append-all", dest='append', action='store_const',
                                const=True, default=False,
                                help='download all toots and append to existing archive')
    parser_content.add_argument("--no-favourites", dest='skip_favourites',
                                action='store_const',
                                const=True, default=False,
                                help='skip download of favourites')
    parser_content.add_argument("--with-mentions", dest='with_mentions',
                                action='store_const',
                                const=True, default=False,
                                help='download mentions (notifications where you are mentioned)')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
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
                                choices=['statuses', 'favourites', 'mentions'],
                                default='statuses',
                                help='export statuses, favourites, or mentions')
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
    parser_content.add_argument("--toots-per-page", dest='toots',
                                metavar='N', type=int, default=2000,
                                help='how many toots per HTML page')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=html.html)


    parser_content = subparsers.add_parser(
        name='expire',
        help='''delete older toots from the server and unfavour favourites
if and only if they are in your archive''')
    parser_content.add_argument("--collection", dest='collection',
                                choices=['statuses', 'favourites'],
                                default='statuses',
                                help='delete statuses or unfavour favourites')
    parser_content.add_argument("--older-than", dest='weeks',
                                metavar='N', type=int, default=4,
                                help='expire toots older than this many weeks')
    parser_content.add_argument("--confirmed", dest='confirmed', action='store_const',
                                const=True, default=False,
                                help='perform the expiration on the server')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=expire.expire)



    parser_content = subparsers.add_parser(
        name='report',
        help='''report some numbers about your toots and favourites''')
    parser_content.add_argument("--all", dest='all', action='store_const',
                                const=True, default=False,
                                help='consider all toots (ignore --newer-than)')
    parser_content.add_argument("--newer-than", dest='weeks',
                                metavar='N', type=int, default=12,
                                help='only consider toots newer than this many weeks')
    parser_content.add_argument("--top", dest='top',
                                metavar='N', type=int, default=10,
                                help='only print the top N tags')
    parser_content.add_argument("--include-boosts", dest='include_boosts', action='store_const',
                                const=True, default=False,
                                help='include boosts')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=report.report)


    args = parser.parse_args()

    try:
        if hasattr(args, "command"):
            if hasattr(args, "user") and args.user == 'all':
                for user in core.all_accounts():
                    print(user)
                    args.user = user
                    args.command(args)
            else:
                args.command(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
