#! /usr/bin/env python3

# Hit the Slack API to get a list of users with their internal Slack
# IDs.
#
# Usage: python3 list_users.py < api_token.txt > users.csv
#
# Typically you'll manually edit users.csv to pare the list down to
# the active people you want to monitor.

import slack_api
import csv
import sys

token = input().strip()
user_list = slack_api.call_slack('users.list',
                                 {'token': token})

user_list_writer = csv.writer(sys.stdout)

user_list_writer.writerow(['user_id', 'user_name'])

for member in user_list['members']:
    user_list_writer.writerow([member['id'], member['name']])
