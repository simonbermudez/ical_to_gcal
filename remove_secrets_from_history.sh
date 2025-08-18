#!/bin/bash

echo "WARNING: This will rewrite git history. Make sure you have a backup!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Create a backup branch
git branch backup-before-cleaning

# Remove sensitive strings from all commits
git filter-branch --force --index-filter \
  'git ls-files -z | xargs -0 sed -i \
    -e "s|https://outlook\.office365\.com/owa/calendar/26ca47ee7d564923b813f9bd4daed616@oncallhealth\.com/2d5e22e353b049498e5f7465242be4a716923625248163559482/calendar\.ics|YOUR_ICS_URL_HERE|g" \
    -e "s|da843d4492fca90a1a8aa0a22cee12ff8c02cff8fc6e41af2b1b8e916126d383@group\.calendar\.google\.com|YOUR_CALENDAR_ID_HERE|g" \
    -e "s|26ca47ee7d564923b813f9bd4daed616@oncallhealth\.com|YOUR_DOMAIN_HERE|g" \
  ' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "History cleaned! To push these changes:"
echo "  git push origin --force --all"
echo "  git push origin --force --tags"
echo ""
echo "Make sure all collaborators delete and re-clone the repository!"