#!/usr/bin/env python3

from mastodon import Mastodon
import sys
import os.path
import json
import datetime

argv = sys.argv

if len(argv) != 2:
    print("Usage: %s username@instance" % argv[0])
    sys.exit(1)

(username, domain) = argv[1].split('@')

url = 'https://' + domain
client_secret = domain + '.client.secret'
user_secret = domain + '.user.' + username + '.secret'
status_file = domain + '.user.' + username + '.json'

if not os.path.isfile(client_secret):

    print("Registering app")
    Mastodon.create_app(
        'mastodon-backup',
        api_base_url = url,
        to_file = client_secret)

if not os.path.isfile(user_secret):

    print("Log in")
    mastodon = Mastodon(
        client_id = client_secret,
        api_base_url = url)
    
    url = mastodon.auth_request_url(
        client_id = client_secret,
        scopes=['read'])

    print("Visit the following URL and authorize the app:")
    print(url)

    print("Then paste the access token here:")
    token = sys.stdin.readline().rstrip()

    mastodon.log_in(
        username = username,
        code = token,
        to_file = user_secret,
        scopes=['read'])

else:

    mastodon = Mastodon(
        client_id = client_secret,
        access_token = user_secret,
        api_base_url = url)

print("Get user info")
user = mastodon.account_verify_credentials()

print("Get statuses (this may take a while)")
statuses = mastodon.account_statuses(user["id"])
statuses = mastodon.fetch_remaining(
    first_page = statuses)

print("Saving %d statuses" % len(statuses))

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None)

with open(status_file, mode = 'w', encoding = 'utf-8') as fp:
    data = json.dump(statuses, fp, default = date_handler)
    fp.close()
