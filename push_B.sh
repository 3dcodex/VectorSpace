#!/bin/bash

default_branch="B"

echo "========================================"
echo "  VECTOR SPACE - B PUSH SCRIPT"
echo "========================================"
echo

# Ensure git is available
if ! command -v git &> /dev/null; then
    echo "Git is not installed or not in PATH."
    exit 1
fi

# Initialize git if needed
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init || exit 1
fi

# Ensure origin exists
if ! git remote get-url origin &> /dev/null; then
    echo "Setting remote origin..."
    git remote add origin https://github.com/3dcodex/VectorSpace.git || exit 1
fi

current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -z "$current_branch" ]; then
    current_branch="$default_branch"
fi

if [ "$current_branch" == "HEAD" ]; then
    current_branch="$default_branch"
fi

if [ "$current_branch" != "$default_branch" ]; then
    echo "You are currently on branch $current_branch."
    read -p "Push this branch instead of $default_branch? (y/N): " continue_push
    if [[ "$continue_push" != "y" && "$continue_push" != "Y" ]]; then
        echo "Push aborted. Switch to $default_branch and run the script again."
        exit 0
    fi
fi

echo
echo "Adding all files..."
git add . || exit 1

# Warn before committing if deletions are staged
has_deletions=$(git diff --cached --name-status | grep -c "^D")
if [ "$has_deletions" -gt 0 ]; then
    echo
    echo "WARNING: The following deletions are staged:"
    git diff --cached --name-status | grep "^D"
    echo
    read -p "Continue with commit and push including deletions? (y/N): " confirm_delete
    if [[ "$confirm_delete" != "y" && "$confirm_delete" != "Y" ]]; then
        echo "Commit aborted by user. Staged changes remain for review."
        exit 0
    fi
fi

# If there are staged changes, commit them before syncing with the remote branch
if ! git diff --cached --quiet; then
    echo
    read -p "Enter commit message (or press Enter for default): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Update $current_branch branch"
    fi

    echo
    echo "Creating commit on $current_branch..."
    git commit -m "$commit_msg" || exit 1
else
    echo
    echo "No staged changes found. Skipping commit."
fi

echo
echo "Fetching latest remote state..."
git fetch origin || exit 1

if ! git ls-remote --exit-code --heads origin "$current_branch" &> /dev/null; then
    echo
    echo "Pushing to new branch $current_branch..."
    git push -u origin "$current_branch" || exit 1
    echo
    echo "========================================"
    echo "  PUSH COMPLETE!"
    echo "========================================"
    exit 0
fi

ahead_count=$(git rev-list --left-right --count "$current_branch"...origin/"$current_branch" | awk '{print $1}')
behind_count=$(git rev-list --left-right --count "$current_branch"...origin/"$current_branch" | awk '{print $2}')

if [ "$behind_count" -gt 0 ]; then
    echo
    echo "Remote branch origin/$current_branch has $behind_count newer commit(s)."
    read -p "Run git pull --rebase origin $current_branch before push? (Y/n): " sync_now
    if [[ "$sync_now" != "n" && "$sync_now" != "N" ]]; then
        git pull --rebase origin "$current_branch" || {
            echo
            echo "========================================"
            echo "  REBASE STOPPED DUE TO CONFLICTS"
            echo "========================================"
            echo "Resolve the conflicted files, then run:"
            echo "  git add <fixed-files>"
            echo "  git rebase --continue"
            echo
            echo "If you want to cancel the rebase instead, run:"
            echo "  git rebase --abort"
            exit 0
        }
    else
        echo "Push aborted. Sync your branch first, then rerun the script."
        exit 0
    fi
fi

echo
echo "Pushing to branch $current_branch..."
git push -u origin "$current_branch" || exit 1

echo
echo "========================================"
echo "  PUSH COMPLETE!"
echo "========================================"
exit 0
