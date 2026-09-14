#!/bin/sh

set -eu

repository='https://github.com/MyBlackHole/pdca-workflow.git'
pdca_root="$HOME/.agents/pdca"
skills_dir="$HOME/.agents/skills"

if ! command -v git >/dev/null 2>&1; then
    echo 'PDCA installation requires Git.' >&2
    exit 1
fi

if [ -e "$pdca_root" ] || [ -L "$pdca_root" ]; then
    echo "Refusing to install: central root already exists: $pdca_root" >&2
    exit 1
fi

if [ -e "$skills_dir" ] || [ -L "$skills_dir" ]; then
    echo "Refusing to install: skill discovery path already exists: $skills_dir" >&2
    exit 1
fi

mkdir -p "$HOME/.agents"
# Claim a new directory before cloning so failure cleanup cannot own an
# installation that existed before this invocation.
mkdir "$pdca_root"
if git clone "$repository" "$pdca_root"  --depth 1; then
    :
else
    clone_status=$?
    rm -rf -- "$pdca_root"
    exit "$clone_status"
fi

# -T refuses a directory that appeared after the preflight instead of placing
# a nested link inside it.  That preserves the no-merge installer contract.
if ln -sT "$pdca_root/skills" "$skills_dir"; then
    :
else
    link_status=$?
    rm -rf -- "$pdca_root"
    exit "$link_status"
fi

printf '%s\n' \
    "PDCA root: $pdca_root" \
    "Skill discovery link: $skills_dir -> $pdca_root/skills" \
    'Start a new host session and invoke: $pdca' \
    "Update manually: git -C \"$pdca_root\" pull"
