#! /usr/bin/env python3

# Using the Slack API:
# (1) Get recent history (midnight last night back to a specified
#     number of days before that) of a specified input channel.
# (2) Count how many of those days each user made a post in the channel.
# (3) Post a report to a specified output channel, calling out the
#     inactive users.
#
# Usage: python3 standup_snitch.py -t api_token.txt \
#                                  -d 14 \
#                                  -i input_channel.csv \
#                                  -o output_channel.csv \
#                                  -u users.csv

import datetime
import csv
import argparse

def format_channel(channel_dict):
    return ''.join(['<#',
                    channel_dict['channel_id'],
                    '|',
                    channel_dict['channel_name'],
                    '>'])

def format_user(user_dict):
    return ''.join(['<@',
                    user_dict['user_id'],
                    '|',
                    user_dict['user_name'],
                    '>'])

# Command line flags
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--token_file', help = 'file with API token')
parser.add_argument('-d', '--duration', type = int,
                    help = 'duration to check in days')
parser.add_argument('-i', '--input_channel_file',
                    help = 'file with Slack channel to monitor')
parser.add_argument('-o', '--output_channel_file',
                    help = 'file with Slack channel to write to')
parser.add_argument('-u', '--user_file', help = 'file with user list')
args = parser.parse_args()
duration_in_days = args.duration

# Read configuration from the specified files
with open(args.token_file) as token_file:
    token = token_file.read().strip()

with open(args.input_channel_file) as input_channel_file:
    input_reader = csv.DictReader(input_channel_file)
    for row in input_reader:
        # The last line is the one that survives
        input_channel = row

with open(args.output_channel_file) as output_channel_file:
    output_reader = csv.DictReader(output_channel_file)
    for row in output_reader:
        # The last line is the one that survives
        output_channel = row

with open(args.user_file) as user_file:
    user_reader = csv.DictReader(user_file)
    users = [user for user in user_reader]

print(token)
print(format_channel(input_channel))
print(format_channel(output_channel))
print(format_user(users[0]))

# Should subclass tzinfo to flag the local times with Chicago
# timezone.

# Midnight last night, Chicago time, all the way back to
# duration_in_days days before that
now = datetime.datetime.now()
end_of_period = datetime.datetime(now.year, now.month, now.day)
start_of_period = end_of_period - datetime.timedelta(days = duration_in_days)

# Need to convert these to UNIX time to ship to Slack

# Slack API call to get history

# Histogram messages, chunking by day

# Sort by message count; build text histogram; list the non-participants
print("On how many of the last", duration_in_days,
      "days did you check in on", format_channel(input_channel) + "?",
      "\n")

print('```')
print('```')

print(', '.join(map(format_user, users)) + ', we miss you.')

# Slack API call to publish summary
