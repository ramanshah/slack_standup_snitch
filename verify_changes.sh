#! /bin/bash

# Display diffs between filename and filename.new; prompt user for
# verification; and either apply or discard the changes.
#
# Usage:
#
# bash verify_changes.sh filename

diff ${1} ${1}.new
echo '---'
read -p 'Is this change OK? (Y/N) ' choice
case "${choice}" in
    y|Y ) echo 'Applying changes.'; mv ${1}.new ${1};;
    * ) echo 'Reverting.'; rm ${1}.new;;
esac
