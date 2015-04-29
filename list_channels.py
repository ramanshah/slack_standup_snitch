#! /usr/bin/env python3

# Hit the Slack API to get a list of users with their internal Slack
# IDs.
#
# Usage: python3 list_channels.py < api_token.txt > input_channel.csv
#        cp input_channel.csv output_channel.csv
#
# Remove all but two lines from each file: input_channel.csv should
# have a header and the line for the channel you want to
# monitor. Similarly, output_channel.csv should have a header and the
# line for the channel you want to send the report to.

import slack_api
import csv
import sys

token = input().strip()

channel_list = slack_api.call_slack('channels.list',
                                    {'token': token})

channel_list_writer = csv.writer(sys.stdout)

channel_list_writer.writerow(['channel_id', 'channel_name'])
for channel in channel_list['channels']:
    channel_list_writer.writerow([channel['id'], channel['name']])
