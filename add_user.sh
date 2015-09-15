#! /bin/bash

# Add a user to the user list.
#
# Usage:
#
# bash add_user.sh users.csv new_user_name api_token.txt
#
# Note this will create and destroy the file users.csv.new in the
# working directory.

cp ${1} ${1}.new
python3 list_users.py < ${3} | grep ${2} >> ${1}.new
bash verify_changes.sh ${1}
