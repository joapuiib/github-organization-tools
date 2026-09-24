#!/usr/bin/env bash
# Bump the project version, commit, and tag it.
#
# Usage: bin/bump-version.sh [major|minor|patch] [-p|--push] [-r|--release] [-f|--force] [-n|--new-commit] [--dry]
#
# After pushing, it offers to create a GitHub release whose notes are written
# by Claude Code (`claude -p`) from the commits since the previous tag. The
# notes are shown for review before publishing. Pass -r/--release to skip the
# "create release?" question. Requires the `claude` and `gh` CLIs.
#
# By default, if HEAD has no tag pointing at it, the version bump is folded
# into HEAD via `git commit --amend`. Pass -n/--new-commit to always create a
# separate commit instead. If HEAD already has a tag, a new commit is always
# created (amending a tagged commit would orphan the tag).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$REPO_ROOT/ghot/ghot.py"

usage() {
    echo "Usage: $(basename "$0") [major|minor|patch] [-p|--push] [-r|--release] [-f|--force] [-n|--new-commit] [--dry]" >&2
    exit 1
}

BUMP=""
PUSH=""
RELEASE=""
FORCE=""
DRY=""
NEW_COMMIT=""

for arg in "$@"; do
    case "$arg" in
        major|minor|patch)
            BUMP="$arg"
            ;;
        -p|--push)
            PUSH="yes"
            ;;
        -r|--release)
            RELEASE="yes"
            ;;
        -f|--force)
            FORCE="yes"
            ;;
        -n|--new-commit)
            NEW_COMMIT="yes"
            ;;
        --dry)
            DRY="yes"
            ;;
        *)
            usage
            ;;
    esac
done

[[ -n "$BUMP" ]] || usage

cd "$REPO_ROOT"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "main" ]]; then
    echo "Error: must be on 'main' branch (currently on '$BRANCH')." >&2
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: working tree not clean. Commit or stash changes first." >&2
    exit 1
fi

CURRENT_VERSION="$(grep -oP '(?<=__version__ = ")[^"]+' "$VERSION_FILE")"
if [[ -z "$CURRENT_VERSION" ]]; then
    echo "Error: could not find __version__ in $VERSION_FILE." >&2
    exit 1
fi

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

case "$BUMP" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
TAG="v$NEW_VERSION"

if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: tag $TAG already exists." >&2
    exit 1
fi

if [[ -n "$NEW_COMMIT" ]]; then
    MODE="new"
elif [[ -n "$(git tag --points-at HEAD)" ]]; then
    MODE="new"
else
    MODE="amend"
fi

echo "Bumping version: $CURRENT_VERSION -> $NEW_VERSION (tag $TAG, $MODE commit)"

if [[ -n "$DRY" ]]; then
    echo "Dry run: no changes made."
    exit 0
fi

if [[ -z "$FORCE" ]]; then
    read -r -p "Proceed with bump, commit and tag? [y/N] " REPLY
    case "$REPLY" in
        [yY]|[yY][eE][sS]) ;;
        *)
            echo "Aborted."
            exit 1
            ;;
    esac
fi

sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" "$VERSION_FILE"

git add "$VERSION_FILE"
if [[ "$MODE" == "amend" ]]; then
    ORIG_MSG="$(git log -1 --pretty=%B)"
    git commit --amend -m "$ORIG_MSG

Bump version to $NEW_VERSION."
else
    git commit -m "chore: bump version to $NEW_VERSION"
fi
git tag -a "$TAG" -m "$TAG"

echo "Created $MODE commit and tag $TAG."

if [[ -z "$PUSH" ]]; then
    read -r -p "Push commit and tag to origin? [y/N] " REPLY
    case "$REPLY" in
        [yY]|[yY][eE][sS])
            PUSH="yes"
            ;;
        *)
            PUSH="no"
            ;;
    esac
fi

if [[ "$PUSH" == "yes" ]]; then
    if [[ "$MODE" == "amend" ]]; then
        git push --force-with-lease origin main
    else
        git push origin main
    fi
    git push origin "$TAG"
    echo "Pushed main and $TAG."
else
    if [[ "$MODE" == "amend" ]]; then
        echo "Skipped push. Run 'git push --force-with-lease origin main && git push origin $TAG' when ready."
    else
        echo "Skipped push. Run 'git push origin main && git push origin $TAG' when ready."
    fi
fi

create_release() {
    if ! command -v claude >/dev/null || ! command -v gh >/dev/null; then
        echo "Skipped release: the 'claude' and 'gh' CLIs are required." >&2
        return
    fi

    local prev_tag range notes_file prompt
    prev_tag="$(git describe --tags --abbrev=0 "$TAG^" 2>/dev/null || true)"
    range="${prev_tag:+$prev_tag..}$TAG"
    notes_file="$(mktemp --suffix=.md)"

    prompt="Write the GitHub release notes for $TAG of ghot (GitHub Organization Tools), \
a CLI to manage GitHub organization members and repositories from a CSV file. \
The commits${prev_tag:+ since $prev_tag} and the changed files are provided on stdin. \
Output only the Markdown body, with no preamble and no title. \
Group the changes under '### Features', '### Fixes' and '### Documentation', omitting empty sections. \
Write one bullet per user-facing change, merging related commits, and put commands and options in backticks. \
Leave out internal changes (tests, refactors, CI, version bumps). Write in English."

    echo "Generating release notes for $TAG${prev_tag:+ (since $prev_tag)}..."
    {
        echo "Commits:"
        git log --no-merges --format='- %s%n%b' "$range"
        echo "Changed files:"
        if [[ -n "$prev_tag" ]]; then git diff --stat "$prev_tag" "$TAG"; fi
    } | claude -p "$prompt" --tools "" > "$notes_file" || true
    if [[ ! -s "$notes_file" ]]; then
        echo "Error: could not generate release notes. Run 'gh release create $TAG --generate-notes' instead." >&2
        rm -f "$notes_file"
        return
    fi

    while true; do
        echo
        cat "$notes_file"
        echo
        read -r -p "Publish GitHub release $TAG with these notes? [y]es/[e]dit/[N]o " REPLY
        case "$REPLY" in
            [yY]|[yY][eE][sS])
                gh release create "$TAG" --verify-tag --title "$TAG" --notes-file "$notes_file"
                break
                ;;
            [eE]|[eE][dD][iI][tT])
                "${EDITOR:-vi}" "$notes_file"
                ;;
            *)
                echo "Skipped release. Run 'gh release create $TAG --generate-notes' when ready."
                break
                ;;
        esac
    done
    rm -f "$notes_file"
}

if [[ "$PUSH" != "yes" ]]; then
    exit 0
fi

if [[ -z "$RELEASE" ]]; then
    read -r -p "Create GitHub release with notes written by Claude? [y/N] " REPLY
    case "$REPLY" in
        [yY]|[yY][eE][sS])
            RELEASE="yes"
            ;;
    esac
fi

if [[ -n "$RELEASE" ]]; then
    create_release
fi
