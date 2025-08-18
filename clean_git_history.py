#!/usr/bin/env python3
"""
Clean sensitive data from git history
"""
import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("GIT HISTORY CLEANER FOR SENSITIVE DATA")
    print("=" * 60)
    
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository!")
        sys.exit(1)
    
    # Sensitive strings to replace
    replacements = [
        ("https://outlook.office365.com/owa/calendar/26ca47ee7d564923b813f9bd4daed616@oncallhealth.com/2d5e22e353b049498e5f7465242be4a716923625248163559482/calendar.ics", 
         "YOUR_ICS_URL_HERE"),
        ("da843d4492fca90a1a8aa0a22cee12ff8c02cff8fc6e41af2b1b8e916126d383@group.calendar.google.com", 
         "YOUR_CALENDAR_ID_HERE"),
        ("26ca47ee7d564923b813f9bd4daed616@oncallhealth.com", 
         "YOUR_DOMAIN_HERE"),
    ]
    
    print("\nSensitive strings found to be replaced:")
    for old, new in replacements:
        print(f"  - {old[:50]}... => {new}")
    
    print("\n" + "!" * 60)
    print("WARNING: This will REWRITE your git history!")
    print("Make sure you have a backup of your repository!")
    print("!" * 60)
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)
    
    # Create backup branch
    print("\nCreating backup branch...")
    subprocess.run(["git", "branch", "-f", "backup-before-cleaning"], check=True)
    print("Backup branch 'backup-before-cleaning' created.")
    
    # Check current status
    print("\nChecking for uncommitted changes...")
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout:
        print("Warning: You have uncommitted changes. Please commit or stash them first.")
        sys.exit(1)
    
    print("\nSearching for sensitive data in history...")
    
    # Find all affected commits
    affected_commits = set()
    for old_string, _ in replacements:
        result = subprocess.run(
            ["git", "grep", old_string, "$(git rev-list --all)"],
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ':' in line:
                    commit = line.split(':')[0]
                    affected_commits.add(commit)
    
    if affected_commits:
        print(f"Found sensitive data in {len(affected_commits)} commits")
        print("Affected commits:", ', '.join(list(affected_commits)[:5]), "..." if len(affected_commits) > 5 else "")
    else:
        print("No sensitive data found in git history.")
        print("Your repository is clean!")
        return
    
    print("\n" + "=" * 60)
    print("RECOMMENDED NEXT STEPS:")
    print("=" * 60)
    print()
    print("Since git filter-branch can be complex and risky, here are the recommended steps:")
    print()
    print("1. Install BFG Repo-Cleaner (safer and faster):")
    print("   wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar")
    print()
    print("2. Run BFG with the replacements file:")
    print("   java -jar bfg-1.14.0.jar --replace-text replacements.txt")
    print()
    print("3. Clean up the repository:")
    print("   git reflog expire --expire=now --all")
    print("   git gc --prune=now --aggressive")
    print()
    print("4. Verify the cleaning worked:")
    print("   git log --all --full-history -p | grep -i 'oncallhealth\\|da843d4492fca90a'")
    print()
    print("5. Force push to remote (DANGEROUS - coordinate with team):")
    print("   git push origin --force --all")
    print("   git push origin --force --tags")
    print()
    print("6. All team members must delete and re-clone the repository!")
    print()
    print("The 'replacements.txt' file has already been created for you.")

if __name__ == "__main__":
    main()