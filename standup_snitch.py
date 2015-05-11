#! /usr/bin/env python3

# Using the Slack API:
# (1) Get recent history (midnight last night back to a specified
#     number of days before that) of a specified input channel.
# (2) Count how many of those days each user made a post in the channel.
# (3) Post a report to a specified output channel, calling out the
#     inactive users.
#
# Usage: python3 standup_snitch.py -t api_token.txt \
#                                  -d 7 \
#                                  -i input_channel.csv \
#                                  -o output_channel.csv \
#                                  -u users.csv \
#                                  -b SnitchBot

import slack_api
import time
import datetime
import csv
import argparse

def format_channel(channel_dict):
    return ''.join(['<#',
                    channel_dict['channel_id'],
                    '|',
                    channel_dict['channel_name'],
                    '>'])

def format_user(user_id, user_name):
    return ''.join(['<@',
                    user_id,
                    '|',
                    user_name,
                    '>'])

def get_message_history(token, channel, ts_start, ts_end):
    # 1000 messages is the maximum allowed by the API.
    history_raw = slack_api.call_slack('channels.history',
                                       {'token': token,
                                        'channel': channel,
                                        'latest': ts_end,
                                        'oldest': ts_start,
                                        'count': 1000})

    return [{'user': message['user'], 'ts': message['ts']}
            for message in history_raw['messages']
            if (message['type'] == 'message' and
                'user' in message and
                'ts' in message)]

def aggregate_activity(history, users, ts_start, duration_in_days):
    # For each user, have a list of duration_in_days False
    # values. Then idempotently turn these flags to True based on the
    # message history. The idea is to find the unique days on which
    # each user posted.
    user_activity_dict = {}
    for user_id in users:
        user_activity_dict[user_id] \
            = [False for _ in range(duration_in_days)]

    for message in history:
        try:
            day = int((float(message['ts']) - ts_start) / (3600 * 24))
            user_activity_dict[message['user']][day] = True
        except KeyError:
            # Post from someone we're not tracking
            pass

    user_activity_hist = {u: sum(user_activity_dict[u])
                          for u in user_activity_dict}

    return user_activity_hist

def introduction(input_channel, duration_in_days):
    fmt_string = "On how many of the last {:d} days did you check in on {:s}?"
    return fmt_string.format(duration_in_days, format_channel(input_channel))

def ascii_bar(username, frequency, username_width, frequency_width):
    format_string = ''.join(['{:>',
                             str(frequency_width),
                             '} {:<',
                             str(username_width),
                             '}'])

    return format_string.format('+' * frequency, username)

def sort_and_histogram(frequencies, users, duration_in_days):
    frequencies_decreasing = sorted(frequencies.items(),
                                    key = lambda x: x[1],
                                    reverse = True)

    longest_username = max(map(len, users.values()))

    return '\n'.join([ascii_bar(users[user_id],
                                frequency,
                                longest_username,
                                duration_in_days)
                      for user_id, frequency in frequencies_decreasing])

def conclusion(frequencies, users):
    non_posters = [user_id for user_id in frequencies
                   if frequencies[user_id] == 0]

    if len(non_posters) == 0:
        return 'Go team!'
    else:
        tag_items = [format_user(user_id, users[user_id])
                     for user_id in non_posters] + ['we miss you.']
        return ', '.join(tag_items)

def post_message(token, channel, text, bot_name):
    slack_api.call_slack('chat.postMessage',
                         {'token': token,
                          'channel': channel,
                          'text': text,
                          'username': bot_name})

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
parser.add_argument('-b', '--bot_name', help = 'display name of bot')
args = parser.parse_args()

duration_in_days = args.duration
bot_name = args.bot_name

# Read configuration from the specified files
with open(args.token_file) as token_file:
    token = token_file.read().strip()

with open(args.input_channel_file) as input_channel_file:
    # Take only the first line after the header
    input_channel = next(csv.DictReader(input_channel_file))

with open(args.output_channel_file) as output_channel_file:
    # Take only the first line after the header
    output_channel = next(csv.DictReader(output_channel_file))

with open(args.user_file) as user_file:
    users = {user['user_id']: user['user_name']
             for user in csv.DictReader(user_file)}

# Calculate the timestamp start of measurement time, based on a 24-hour day and
# based on accurate time on the host computer. Assumes no Daylight
# Savings boundaries in the period of interest. Be warned!
ts_now = time.time()
now = datetime.datetime.now()
last_night_midnight = datetime.datetime(now.year, now.month, now.day)
ts_end = int(ts_now - (now - last_night_midnight).total_seconds())
ts_start = ts_end - duration_in_days * 24 * 3600

# Slack API call to get history
message_history = get_message_history(token,
                                      input_channel['channel_id'],
                                      ts_start,
                                      ts_end)

# Calculate how many days each user posted
frequencies = aggregate_activity(message_history,
                                 users,
                                 ts_start,
                                 duration_in_days)

# Preamble
introduction = introduction(input_channel, duration_in_days)

# Sort these frequencies in decreasing order and make an ASCII histogram
text_histogram = sort_and_histogram(frequencies, users, duration_in_days)

# Call out non-posters or congratulate the team
conclusion = conclusion(frequencies, users)

# Assemble the full_message
full_message = '\n'.join([introduction,
                          '```',
                          text_histogram,
                          '```',
                          conclusion])

# Slack API call to publish summary
post_message(token, output_channel['channel_id'], full_message, bot_name)
