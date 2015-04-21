#! /usr/bin/env python3

# Hit the Slack API to get a list of users with their internal Slack
# IDs.
#
# Usage: python3 list_channels.py < api_token.txt > input_channel.csv
#        python3 list_channels.py < api_token.txt > output_channel.csv
#
# Remove all but two lines from each file: input_channel.csv should
# have a header and the line for the file you want to
# monitor. Similarly, output_channel.csv should have a header and the
# line for the file you want to send the report to.

import urllib.request
import urllib.parse
import csv
import sys
import json

token = input().strip()
token_encoded = urllib.parse.urlencode({'token': token}).encode()
response = urllib.request.urlopen('https://slack.com/api/channels.list',
                                  data = token_encoded)

channel_list = json.loads(response.read().decode())
channel_list_writer = csv.writer(sys.stdout)

channel_list_writer.writerow(['channel_id', 'channel_name'])

if channel_list['ok']:
    for channel in channel_list['channels']:
        channel_list_writer.writerow([channel['id'], channel['name']])
else:
    raise Exception('Slack API returned error', channel_list['error'])
mv
