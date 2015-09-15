#! /bin/bash

# Remove a user from the user list.
#
# Usage:
#
# bash remove_user.sh users.csv user_to_remove
#
# Note this will create and destroy the file users.csv.new in the
# working directory.

sed "/${2}/d" ${1} > ${1}.new
bash verify_changes.sh ${1}
