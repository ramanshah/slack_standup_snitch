#! /usr/bin/env python3

# Hit the Slack API to get a list of users with their internal Slack
# IDs.
#
# Usage: python3 list_users.py < api_token.txt > users.csv
#
# Typically you'll manually edit users.csv to pare the list down to
# the active people you want to monitor.

import urllib.request
import urllib.parse
import csv
import sys
import json

token = input().strip()
token_encoded = urllib.parse.urlencode({'token': token}).encode()
response = urllib.request.urlopen('https://slack.com/api/users.list',
                                  data = token_encoded)

user_list = json.loads(response.read().decode())
user_list_writer = csv.writer(sys.stdout)

user_list_writer.writerow(['user_id', 'user_name'])

if user_list['ok']:
    for member in user_list['members']:
        user_list_writer.writerow([member['id'], member['name']])
else:
    raise Exception('Slack API returned error', user_list['error'])
