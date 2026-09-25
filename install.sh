#!/bin/sh

set -eu

repository='https://github.com/MyBlackHole/pdca-workflow.git'
runtime_skills='pdca pdca-assist pdca-plan pdca-do pdca-check pdca-act pdca-model pdca-implement pdca-verify'

fail() { printf '%s\n' "$*" >&2; exit 1; }
exists() { [ -e "$1" ] || [ -L "$1" ]; }

for tool in git stat readlink mkdir ln rm rmdir; do
    command -v "$tool" >/dev/null 2>&1 || fail "PDCA installation requires $tool."
done
case ${HOME:-} in /*) ;; *) fail 'HOME must be an absolute directory path.' ;; esac
home=$(CDPATH= cd -P "$HOME" && pwd -P) || exit 1
agents_root="$home/.agents"
pdca_root="$agents_root/pdca"
skills_dir="$agents_root/skills"

# Both GNU and BSD stat report the object itself (not a symlink's target).
if stat -c '%d:%i' "$home" >/dev/null 2>&1; then
    stat_style=gnu
elif stat -f '%d:%i' "$home" >/dev/null 2>&1; then
    stat_style=bsd
else
    fail 'PDCA installation requires GNU or BSD stat (device/inode identity).'
fi
identity() {
    if [ "$stat_style" = gnu ]; then stat -c '%d:%i' "$1";
    else stat -f '%d:%i' "$1"; fi
}
same_dir() {
    [ ! -L "$1" ] && [ -d "$1" ] && [ "$(identity "$1")" = "$2" ]
}

[ ! -L "$agents_root" ] || fail "Refusing symlink: $agents_root"
if ! exists "$agents_root"; then mkdir "$agents_root"; fi
[ -d "$agents_root" ] || fail "Not a directory: $agents_root"
agents_id=$(identity "$agents_root")
exists "$pdca_root" && fail "Refusing to install: central root already exists: $pdca_root"
if exists "$skills_dir"; then
    [ ! -L "$skills_dir" ] && [ -d "$skills_dir" ] || fail "Not a plain directory: $skills_dir"
    for skill in $runtime_skills; do
        exists "$skills_dir/$skill" && fail "Runtime skill path already exists: $skills_dir/$skill"
    done
fi

created_skills_dir=0
skills_id=''
pdca_id=''
linked_skills=''
pending_skill=''
pinned=0

cleanup_install() {
    status=$?
    trap - 0 HUP INT TERM
    [ "$status" -ne 0 ] || exit 0
    set +e
    # Stay in the directory opened before clone, even if its pathname was replaced.
    if [ "$pinned" -eq 1 ]; then
        for entry in $linked_skills; do
            skill=${entry%%:*}
            link_id=${entry#*:}
            if [ -L "./$skill" ] && [ "$(identity "./$skill")" = "$link_id" ] &&
               [ "$(readlink "./$skill")" = "$pdca_root/skills/$skill" ]; then
                rm -f "./$skill" || printf 'Could not remove created link: %s\n' "$skill" >&2
            elif exists "./$skill"; then
                printf 'Retained changed entry (not owned by this rollback): %s\n' "$skill" >&2
            fi
        done
        [ -z "$pending_skill" ] || printf 'Unconfirmed link operation; inspect entry: %s\n' "$pending_skill" >&2
    fi
    # Never recursively delete a checkout: another process may have added data.
    # Only remove unchanged, empty directories; retain nonempty/uncertain paths.
    if [ -n "$pdca_id" ]; then
        if same_dir "$agents_root" "$agents_id" && same_dir "$pdca_root" "$pdca_id"; then
            rmdir "$pdca_root" 2>/dev/null || printf 'Retained checkout for inspection: %s\n' "$pdca_root" >&2
        else
            printf 'Central path changed; no cleanup attempted: %s\n' "$pdca_root" >&2
        fi
    fi
    if [ "$created_skills_dir" -eq 1 ] && same_dir "$agents_root" "$agents_id" &&
       same_dir "$skills_dir" "$skills_id"; then
        rmdir "$skills_dir" 2>/dev/null || printf 'Retained nonempty discovery directory: %s\n' "$skills_dir" >&2
    fi
    exit "$status"
}
trap cleanup_install 0
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

if ! exists "$skills_dir"; then
    mkdir "$skills_dir"
    created_skills_dir=1
fi
skills_id=$(identity "$skills_dir")
same_dir "$agents_root" "$agents_id" && same_dir "$skills_dir" "$skills_id" || fail 'Discovery path changed.'
CDPATH= cd -P "$skills_dir"
[ "$(identity .)" = "$skills_id" ] || fail 'Discovery directory changed while opening it.'
pinned=1

check_paths() {
    same_dir "$agents_root" "$agents_id" && same_dir "$skills_dir" "$skills_id" &&
        same_dir "$pdca_root" "$pdca_id" || fail 'Installation directory identity changed; stopping.'
}

# Claim a fresh directory; clone relative to its pinned working directory.
mkdir "$pdca_root"
pdca_id=$(identity "$pdca_root")
(
    CDPATH= cd -P "$pdca_root"
    [ "$(identity .)" = "$pdca_id" ] || exit 1
    git clone "$repository" . --depth 1
)
check_paths

check_entries() {
    [ ! -L "$pdca_root/skills" ] && [ -d "$pdca_root/skills" ] || fail 'Invalid checkout: skills must be a plain directory.'
    for skill in $runtime_skills; do
        directory="$pdca_root/skills/$skill"
        file="$directory/SKILL.md"
        [ ! -L "$directory" ] && [ -d "$directory" ] && [ ! -L "$file" ] &&
            [ -f "$file" ] && [ -r "$file" ] && [ -s "$file" ] ||
            fail "Invalid checkout: require a readable, nonempty regular entry: skills/$skill/SKILL.md"
    done
}
check_entries

for skill in $runtime_skills; do
    check_paths
    exists "./$skill" && fail "Runtime skill path appeared during installation: $skills_dir/$skill"
    pending_skill=$skill
    # Explicit directory '.' fixes the basename; an existing directory named
    # after the skill is an EEXIST conflict, not a new destination to descend into.
    ln -s "$pdca_root/skills/$skill" .
    link_id=$(identity "./$skill")
    linked_skills="$linked_skills $skill:$link_id"
    pending_skill=''
    [ -L "./$skill" ] && [ "$(readlink "./$skill")" = "$pdca_root/skills/$skill" ] || fail "Created link changed: $skill"
done
check_paths
check_entries
for entry in $linked_skills; do
    skill=${entry%%:*}
    [ -L "./$skill" ] && [ "$(identity "./$skill")" = "${entry#*:}" ] &&
        [ "$(readlink "./$skill")" = "$pdca_root/skills/$skill" ] || fail "Created link changed: $skill"
done

printf '%s\n' \
    "PDCA root: $pdca_root" \
    "Skill discovery directory: $skills_dir" \
    'Runtime skill links: pdca, pdca-assist, pdca-plan, pdca-do, pdca-check, pdca-act, pdca-model, pdca-implement, pdca-verify' \
    'Start a new host session and invoke: $pdca' \
    "Update manually: git -C \"$pdca_root\" pull"
