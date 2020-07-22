#!/usr/bin/env python3
# Copyright (C) 2017-2019  Alex Schroeder <alex@gnu.org>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import argparse
from . import archive
from . import replies
from . import text
from . import context
from . import html
from . import media
from . import split
from . import expire
from . import report
from . import followers
from . import following
from . import whitelist
from . import mutuals
from . import login
from . import fix

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
    parser_content.add_argument("--no-favourites", dest='skip_favourites',
                                action='store_const',
                                const=True, default=False,
                                help='skip download of favourites')
    parser_content.add_argument("--with-mentions", dest='with_mentions',
                                action='store_const',
                                const=True, default=False,
                                help='download mentions (notifications where you are mentioned)')
    parser_content.add_argument("--with-followers", dest='with_followers',
                                action='store_const',
                                const=True, default=False,
                                help='download followers (people following you)')
    parser_content.add_argument("--with-following", dest='with_following',
                                action='store_const',
                                const=True, default=False,
                                help='download following (the people you follow)')
    parser_content.add_argument("--no-stopping", dest='stopping',
                                action='store_const',
                                const=False, default=True,
                                help='do not stop after seeing 10 duplicates')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=archive.archive)


    parser_content = subparsers.add_parser(
        name='replies',
        help='archive missing toots you replied to')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=replies.replies)


    parser_content = subparsers.add_parser(
        name='media',
        help='download media referred to by toots in your archive')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.add_argument("--combine",
                                action="store_true",
                                help="combine archives in case they are split")
    parser_content.add_argument("--collection", dest='collection',
                                choices=['statuses', 'favourites'],
                                default='statuses',
                                help='export statuses or favourites')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.set_defaults(command=media.media)


    parser_content = subparsers.add_parser(
        name='text',
        help='search and export toots in the archive as plain text')
    parser_content.add_argument("--reverse", dest='reverse', action='store_const',
                                const=True, default=False,
                                help='reverse output, oldest first')
    parser_content.add_argument("--combine",
                                action="store_true",
                                help="combine archives in case they are split")
    parser_content.add_argument("--collection", dest='collection',
                                choices=['statuses', 'favourites', 'mentions', 'all'],
                                default='statuses',
                                help='export statuses, favourites, or mentions')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.add_argument("pattern", nargs='*',
                                help='regular expressions used to filter output')
    parser_content.set_defaults(command=text.text)


    parser_content = subparsers.add_parser(
        name='context',
        help='show a toot in context (i.e. with its ancestors and its descendants')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.add_argument("url",
                                help='URL of the toot to be included')
    parser_content.set_defaults(command=context.context)


    parser_content = subparsers.add_parser(
        name='html',
        help='export toots and media in the archive as static HTML')
    parser_content.add_argument("--combine",
                                action="store_true",
                                help="combine archives in case they are split")
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
        name='split',
        help='split an archive into two')
    parser_content.add_argument("--older-than", dest='weeks',
                                metavar='N', type=float, default=4,
                                help='split anything older than this many weeks')
    parser_content.add_argument("--confirmed", dest='confirmed',
                                action='store_const', const=True, default=False,
                                help='save the data after splitting')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=split.split)


    parser_content = subparsers.add_parser(
        name='expire',
        help='''delete older toots from the server and unfavour favourites
        if and only if they are in your archive''',
        epilog='''There is one problem you need to be aware of: if you expiring
        mentions, then the tool goes through all your notifications
        and looks at those of the type mention, and expires them if
        they are old enough. There are other types of notifications,
        however: follow, favourite, and reblog (at the time of this
        writing). As these are not archived, we also don't expire
        them. Thus, the list of notifications to look through keeps
        growing unless you use the "Clear notifications" menu in the
        Mastodon web client. Alternatively, you can use the
        --delete-other-notifications option together with
        --collection mentions.''')

    parser_content.add_argument("--collection", dest='collection',
                                choices=['statuses', 'favourites', 'mentions'],
                                default='statuses',
                                help='delete statuses, unfavour favourites, or clear mention notifications')
    parser_content.add_argument("--older-than", dest='weeks',
                                metavar='N', type=float, default=4,
                                help='expire anything older than this many weeks')
    parser_content.add_argument("--delete-other-notifications", dest='delete_others',
                                action='store_const', const=True, default=False,
                                help='clear follow, favourite, and reblog notifications')
    parser_content.add_argument("--confirmed", dest='confirmed',
                                action='store_const', const=True, default=False,
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
    parser_content.add_argument("--combine",
                                action="store_true",
                                help="combine archives in case they are split")
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
    parser_content.add_argument("--with-emoji", dest='with_emoji', action='store_const',
                                const=True, default=False,
                                help='include emoji count')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=report.report)


    parser_content = subparsers.add_parser(
        name='followers',
        help='''find followers who never mention you''')
    parser_content.add_argument("--block", dest='block', action='store_const',
                                const=True, default=False,
                                help='...and block them')
    parser_content.add_argument("--all", dest='all', action='store_const',
                                const=True, default=False,
                                help='consider all toots (ignore --newer-than)')
    parser_content.add_argument("--newer-than", dest='weeks',
                                metavar='N', type=int, default=12,
                                help='require interaction within this many weeks (default is 12)')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=followers.followers)


    parser_content = subparsers.add_parser(
        name='following',
        help='''find people you are following but who never mention you''')
    parser_content.add_argument("--unfollow", dest='unfollow', action='store_const',
                                const=True, default=False,
                                help='...and unfollow them')
    parser_content.add_argument("--all", dest='all', action='store_const',
                                const=True, default=False,
                                help='consider all toots (ignore --newer-than)')
    parser_content.add_argument("--newer-than", dest='weeks',
                                metavar='N', type=int, default=12,
                                help='require mention within this many weeks (default is 12)')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=following.following)


    parser_content = subparsers.add_parser(
        name='mutuals',
        help='''find people you are following and who follow you back''')
    parser_content.add_argument("--pace", dest='pace', action='store_const',
                                const=True, default=False,
                                help='avoid timeouts and pace requests')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=mutuals.mutuals)


    parser_content = subparsers.add_parser(
        name='whitelist',
        help='''print the whitelist to help you debug problems''')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=whitelist.print_whitelist)

    parser_content = subparsers.add_parser(
        name='fix-boosts',
        help='''mark all the boosts as not deleted (triggering their deletion)''')
    parser_content.add_argument("--combine",
                                action="store_true",
                                help="combine archives in case they are split")
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.add_argument("--confirmed", dest='confirmed',
                                action='store_const', const=True, default=False,
                                help='perform the change on the archive')
    parser_content.set_defaults(command=fix.fix_boosts)

    parser_content = subparsers.add_parser(
        name='login',
        help='login to the instance for testing purposes')
    parser_content.add_argument("user",
                                help='your account, e.g. kensanata@octogon.social')
    parser_content.set_defaults(command=login.login)


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
