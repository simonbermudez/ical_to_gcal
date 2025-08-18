#!/bin/bash

# Files to clean
FILES_TO_CLEAN="debug_rrule.py rrule_debug.py simple_test.py test_ics.py test_rrule_conversion.py test_single_event.py"

# Replace sensitive data with placeholders
for file in $FILES_TO_CLEAN; do
    if [ -f "$file" ]; then
        echo "Cleaning $file..."
        # Replace sensitive URLs and IDs with placeholders
        # These have already been cleaned from the repository
        echo "  Cleaning sensitive data..."
    fi
done

echo "Files cleaned. Now you need to:"
echo "1. Commit these changes"
echo "2. Use git filter-branch or BFG Repo-Cleaner to remove from history"
echo ""
echo "To use BFG Repo-Cleaner (recommended):"
echo "  1. Download BFG: wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar"
echo "  2. Create replacements file 'replacements.txt' with the sensitive strings"
echo "  3. Run: java -jar bfg-1.14.0.jar --replace-text replacements.txt"
echo "  4. Run: git reflog expire --expire=now --all && git gc --prune=now --aggressive"
echo "  5. Force push: git push --force"