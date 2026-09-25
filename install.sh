#!/bin/sh

set -eu

repository='https://github.com/MyBlackHole/pdca-workflow.git'
pdca_root="$HOME/.agents/pdca"
skills_dir="$HOME/.agents/skills"
runtime_skills='pdca pdca-assist pdca-plan pdca-do pdca-check pdca-act pdca-model pdca-implement pdca-verify'

created_skills_dir=0
linked_skills=''

cleanup_install() {
    status="$1"
    for skill in $linked_skills; do
        rm -f -- "$skills_dir/$skill"
    done
    if [ "$created_skills_dir" -eq 1 ]; then
        rmdir "$skills_dir" 2>/dev/null || true
    fi
    rm -rf -- "$pdca_root"
    exit "$status"
}

if ! command -v git >/dev/null 2>&1; then
    echo 'PDCA installation requires Git.' >&2
    exit 1
fi

if [ -e "$pdca_root" ] || [ -L "$pdca_root" ]; then
    echo "Refusing to install: central root already exists: $pdca_root" >&2
    exit 1
fi

skills_dir_preexisting=0
if [ -L "$skills_dir" ]; then
    echo "Refusing to install: skill discovery path is a symlink: $skills_dir" >&2
    exit 1
elif [ -e "$skills_dir" ]; then
    if [ ! -d "$skills_dir" ]; then
        echo "Refusing to install: skill discovery path is not a directory: $skills_dir" >&2
        exit 1
    fi
    skills_dir_preexisting=1
    for skill in $runtime_skills; do
        if [ -e "$skills_dir/$skill" ] || [ -L "$skills_dir/$skill" ]; then
            echo "Refusing to install: runtime skill path already exists: $skills_dir/$skill" >&2
            exit 1
        fi
    done
fi

mkdir -p "$HOME/.agents"
mkdir "$pdca_root"
if git clone "$repository" "$pdca_root" --depth 1; then
    :
else
    clone_status=$?
    rm -rf -- "$pdca_root"
    exit "$clone_status"
fi

for skill in $runtime_skills; do
    if [ ! -d "$pdca_root/skills/$skill" ]; then
        echo "Invalid checkout: missing runtime skill: skills/$skill" >&2
        cleanup_install 1
    fi
done

if [ "$skills_dir_preexisting" -eq 0 ]; then
    if [ -e "$skills_dir" ] || [ -L "$skills_dir" ]; then
        echo "Refusing to install: skill discovery path appeared during installation: $skills_dir" >&2
        cleanup_install 1
    fi
    mkdir "$skills_dir"
    created_skills_dir=1
fi

for skill in $runtime_skills; do
    destination="$skills_dir/$skill"
    if [ -e "$destination" ] || [ -L "$destination" ]; then
        echo "Refusing to install: runtime skill path appeared during installation: $destination" >&2
        cleanup_install 1
    fi
    if ln -s "$pdca_root/skills/$skill" "$destination"; then
        linked_skills="$linked_skills $skill"
    else
        link_status=$?
        cleanup_install "$link_status"
    fi
done

printf '%s\n' \
    "PDCA root: $pdca_root" \
    "Skill discovery directory: $skills_dir" \
    'Runtime skill links: pdca, pdca-assist, pdca-plan, pdca-do, pdca-check, pdca-act, pdca-model, pdca-implement, pdca-verify' \
    'Start a new host session and invoke: $pdca' \
    "Update manually: git -C \"$pdca_root\" pull"
