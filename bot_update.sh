#!/bin/bash

echo "=== UPDATING THE BOT ==="
git stash save -u 'Autostash before update'
git pull < /dev/null &&
echo "=== UPDATE COMPLETE ===" &&
exec ./main.py

# if anything went wrong...
echo "!!! UPDATE FAILED !!!"
git reset --hard
