#!/bin/bash

# push_all.sh - Push code to remote repositories
# Usage: ./push_all.sh [options] <tag> [commit message]
# Options:
#   --help              Show help information
#   --public <repo1> <repo2>  Specify two public repository addresses
#   --private <repo>    Specify private repository address
#   --private-dir <dir> Specify directory in private repository
#   --files <file1> <file2> ...  Specify files to push to private repository
#
# Examples:
#   ./push_all.sh v1.0.0 "Feature description"
#   ./push_all.sh --public origin github --private private v1.0.0

set -e

FORCE_PUSH_REQUIRED=false

check_and_sync_remote() {
    local repo_url="$1"
    local repo_name="$2"
    
    echo "Checking $repo_name repository status..."
    
    local remote_ref=$(timeout "$TIMEOUT_SECONDS" git ls-remote --heads "$repo_url" master | awk '{print $1}')
    local local_ref=$(git rev-parse HEAD)
    
    if [ -z "$remote_ref" ]; then
        echo " Cannot fetch remote reference for $repo_name, skipping sync check"
        FORCE_PUSH_REQUIRED=false
        return 0
    fi
    
    echo "Local HEAD: $(git rev-parse --short HEAD)"
    echo "$repo_name HEAD: $(echo "$remote_ref" | cut -c1-7)"
    
    if [ "$remote_ref" = "$local_ref" ]; then
        echo "✓ Local branch is identical to $repo_name"
        echo "  No changes to push"
        FORCE_PUSH_REQUIRED=false
        return 1
    fi
    
    local common_ancestor=$(git merge-base HEAD "$remote_ref")
    
    if [ "$common_ancestor" = "$remote_ref" ]; then
        echo "✓ Local branch is ahead of $repo_name (fast-forward possible)"
        echo "  Will push normally"
        FORCE_PUSH_REQUIRED=false
        return 0
    fi
    
    if [ "$common_ancestor" = "$local_ref" ]; then
        echo "⚠ Local branch is behind $repo_name"
        echo "  Using local-first strategy: will force push to override remote"
        FORCE_PUSH_REQUIRED=true
        return 0
    else
        echo "⚠ Branch divergence detected with $repo_name"
        echo "  Using local-first strategy: will force push to override remote"
        FORCE_PUSH_REQUIRED=true
        return 0
    fi
}

GITEE_TOKEN="f18ef8856eba961481c50aeb06221e87"
GITHUB_TOKEN="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"

TIMEOUT_SECONDS=60

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OSCHECKPERF_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

update_oscheckperf_version() {
    local version="$1"
    local script_file="$OSCHECKPERF_DIR/oscheckperf"

    if [ ! -f "$script_file" ]; then
        echo "Warning: oscheckperf file not found, skipping version update"
        return
    fi

    version="${version#v}"

    sed -i "s/^#-- Version:.*/#-- Version:     v${version}/" "$script_file"
    sed -i "s/echo \"Version: [0-9]\+\.[0-9]\+\.[0-9]\+\"/echo \"Version: ${version}\"/" "$script_file"

    echo "✓ Updated oscheckperf version to ${version}"
}

PUBLIC_REPO1_URL="https://gitee.com/panwanping/oscheckperf-tools.git"
PUBLIC_REPO2_URL="https://github.com/77557231/oscheckperf-tools.git"
PRIVATE_REPO="https://gitee.com/panwanping/private"
PRIVATE_DIR="oscheckperf"

DEFAULT_FILES=(".trae/rules" ".trae/skills")
FILES=()    

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            echo "Usage: $0 [options] <tag> [commit message]"
            echo "Options:"
            echo "  --help              Show help information"
            echo "  --public <repo1> <repo2>  Specify two public repository addresses"
            echo "  --private <repo>    Specify private repository address"
            echo "  --private-dir <dir> Specify directory in private repository"
            echo "  --files <file1> <file2> ...  Specify files to push to private repository"
            echo "  --timeout <seconds> Network timeout in seconds (default: 60)"
            exit 0
            ;;
        --public)
            if [[ $# -ge 3 ]]; then
                PUBLIC_REPO1_URL="$2"
                PUBLIC_REPO2_URL="$3"
                shift 3
            else
                echo "Error: --public requires two repository addresses"
                exit 1
            fi
            ;;
        --private)
            if [[ $# -ge 2 ]]; then
                PRIVATE_REPO="$2"
                shift 2
            else
                echo "Error: --private requires one repository address"
                exit 1
            fi
            ;;
        --private-dir)
            if [[ $# -ge 2 ]]; then
                PRIVATE_DIR="$2"
                shift 2
            else
                echo "Error: --private-dir requires a directory name"
                exit 1
            fi
            ;;
        --files)
            shift
            while [[ $# -gt 0 && ! $1 =~ ^-- ]]; do
                FILES+=("$1")
                shift
            done
            ;;
        --timeout)
            if [[ $# -ge 2 ]]; then
                TIMEOUT_SECONDS="$2"
                shift 2
            else
                echo "Error: --timeout requires a number"
                exit 1
            fi
            ;;
        *)
            tag="$1"
            shift
            break
            ;;
    esac
done
if [ ${#FILES[@]} -eq 0 ]; then
    FILES=("${DEFAULT_FILES[@]}")
fi

if [ -z "$tag" ]; then
    echo "Usage: $0 [options] <tag> [commit message]"
    echo "Use --help for detailed help"
    exit 1
fi

tag="v${tag#v}"

commit_message="$*"

generate_tag_message() {
    local tag="$1"
    local message="$2"
    
    local commit_count=$(git rev-list --count HEAD ^$(git describe --abbrev=0 --tags 2>/dev/null || git rev-list --max-parents=0 HEAD))
    if [ -z "$commit_count" ]; then
        commit_count="N/A"
    fi
    
    echo "${tag} - ${message} Verified: ${commit_count}"
}

# Auto-generate commit message from git log commits
auto_generate_commit_message() {
    echo "========================================" >&2
    echo "  Auto-generating commit message" >&2
    echo "========================================" >&2
    
    # Get changes since last tag or beginning
    local last_tag=$(git describe --abbrev=0 --tags 2>/dev/null || echo "")
    
    local commit_range=""
    if [ -n "$last_tag" ]; then
        echo "Analyzing commits since tag: $last_tag" >&2
        commit_range="$last_tag..HEAD"
    else
        echo "Analyzing all commits (no previous tag found)" >&2
        commit_range="HEAD~5..HEAD"
        if ! git rev-parse "$commit_range" > /dev/null 2>&1; then
            commit_range="HEAD"
        fi
    fi
    
    # Extract commit subjects and generate summary
    local subjects=$(git log --oneline "$commit_range" --format="%s" 2>/dev/null)
    
    local summary_items=()
    local seen_items=()
    
    while IFS= read -r subject; do
        [ -z "$subject" ] && continue
        # Remove tag prefix if present (e.g., "v1.0.1:" -> "")
        subject=$(echo "$subject" | sed 's/^v[0-9]\+\.[0-9]\+\.[0-9]\+[: ]*//')
        # Capitalize first letter
        subject=$(echo "$subject" | sed 's/^[a-z]/\U&/')
        
        # Skip if already added
        local is_dup=0
        for seen in "${seen_items[@]}"; do
            if [ "$seen" = "$subject" ]; then
                is_dup=1
                break
            fi
        done
        [ $is_dup -eq 1 ] && continue
        
        seen_items+=("$subject")
        summary_items+=("$subject")
        
        # Limit to 5 items
        if [ ${#summary_items[@]} -ge 5 ]; then
            break
        fi
    done <<< "$subjects"
    
    # Format as numbered list
    local formatted_message=""
    local idx=1
    for item in "${summary_items[@]}"; do
        formatted_message="${formatted_message}${idx}) ${item} "
        idx=$((idx + 1))
    done
    
    # Trim trailing space
    formatted_message=$(echo "$formatted_message" | sed 's/ $//')
    
    # Fallback if no commits found
    if [ -z "$formatted_message" ]; then
        formatted_message="1) Minor updates and bug fixes"
    fi
    
    echo "Generated commit message:" >&2
    echo "$formatted_message" >&2
    echo "========================================" >&2
    
    # Return only the commit message (to stdout)
    echo "$formatted_message"
}

if [ -z "$commit_message" ]; then
    echo "Auto-generating commit message from git commits..."
    commit_message=$(auto_generate_commit_message)
    echo ""
    echo "Using auto-generated commit message:"
    echo "$commit_message"
    echo ""
fi

echo "========================================"
echo "  Push oscheckperf to remote repositories"
echo "========================================"
echo "Tag: $tag"
echo "Commit message: $commit_message"
echo "Public repo 1: gitee/database-benchmark-tools"
echo "Public repo 2: github/database-tools"
echo "Private repo: $PRIVATE_REPO"
echo "Private repo directory: $PRIVATE_DIR"
echo "Network timeout: ${TIMEOUT_SECONDS}s"
echo ""

if [ ! -d ".git" ]; then
    echo "Error: Current directory is not a git repository"
    exit 1
fi

echo "Updating oscheckperf version..."
update_oscheckperf_version "$tag"

echo "Staging all changes..."
git add -A

if git diff --cached --quiet; then
    echo "No changes to commit"
else
    echo "Committing changes..."
    git commit -m "$tag  $commit_message"
fi

tag_message=$(generate_tag_message "$tag" "$commit_message")

if ! git rev-parse "refs/tags/$tag" > /dev/null 2>&1; then
    echo "Creating tag $tag..."
    git tag -a "$tag" -m "$tag_message"
else
    echo "Tag $tag already exists, skipping creation"
    echo "Deleting old tag and recreating..."
    git tag -d "$tag"
    git tag -a "$tag" -m "$tag_message"
fi

echo "========================================"
echo "  Push to Gitee"
echo "========================================"
echo "Gitee target: Chinese users"
echo "README: Combined Chinese/English"
echo "========================================"

echo "Checking branch synchronization with Gitee..."
if ! check_and_sync_remote "$PUBLIC_REPO1_URL" "Gitee"; then
    echo "  Skipping push to Gitee (local is identical)"
else
    PUBLIC_REPO1_WITH_TOKEN=$(echo "$PUBLIC_REPO1_URL" | sed "s|https://|https://panwanping:${GITEE_TOKEN}@|g")

    echo "Pushing code to Gitee repository..."
    push_cmd="git push $PUBLIC_REPO1_WITH_TOKEN master"
    if $FORCE_PUSH_REQUIRED; then
        push_cmd="$push_cmd --force"
        echo "  Force push enabled"
    fi
    if timeout "$TIMEOUT_SECONDS" $push_cmd; then
        echo "✓ Successfully pushed code to gitee repository"
    else
        echo "✗ Failed to push code to gitee repository, continuing execution"
    fi
fi

echo "Pushing tag $tag to Gitee repository..."
if timeout "$TIMEOUT_SECONDS" git push "$PUBLIC_REPO1_WITH_TOKEN" "$tag" --force; then
    echo "✓ Successfully pushed tag to gitee repository"
else
    echo "✗ Failed to push tag to gitee repository, continuing execution"
fi

echo ""
echo "========================================"
echo "  Push to GitHub"
echo "========================================"
echo "GitHub target: International users"
echo "README: Combined Chinese/English"
echo "========================================"

# GitHub push with timeout tolerance - network issues are common
echo "Checking branch synchronization with GitHub..."
github_push_needed=true
if ! check_and_sync_remote "$PUBLIC_REPO2_URL" "GitHub"; then
    echo "  Skipping push to GitHub (local is identical)"
    github_push_needed=false
fi

if $github_push_needed; then
    PUBLIC_REPO2_WITH_TOKEN=$(echo "$PUBLIC_REPO2_URL" | sed "s|https://|https://77557231:${GITHUB_TOKEN}@|g")

    echo "Pushing code to GitHub repository..."
    push_cmd="git push $PUBLIC_REPO2_WITH_TOKEN master"
    if $FORCE_PUSH_REQUIRED; then
        push_cmd="$push_cmd --force"
        echo "  Force push enabled"
    fi
    if timeout "$TIMEOUT_SECONDS" $push_cmd; then
        echo "✓ Successfully pushed code to github repository"
    else
        echo "⚠ GitHub push timed out or failed (network issues common), ignoring and continuing"
    fi
else
    echo "  No need to push code to GitHub"
fi

echo "Pushing tag $tag to GitHub repository..."
if timeout "$TIMEOUT_SECONDS" git push "$PUBLIC_REPO2_WITH_TOKEN" "$tag" --force; then
    echo "✓ Successfully pushed tag to github repository"
else
    echo "⚠ GitHub tag push timed out or failed (network issues common), ignoring and continuing"
fi

echo ""
echo "========================================"
echo "  Push specified files to private repository"
echo "========================================"

temp_dir=$(mktemp -d)
echo "Created temporary directory: $temp_dir"

PRIVATE_REPO_WITH_TOKEN=$(echo "$PRIVATE_REPO" | sed "s|https://|https://oauth2:${GITEE_TOKEN}@|g")
if timeout "$TIMEOUT_SECONDS" git clone "$PRIVATE_REPO_WITH_TOKEN" "$temp_dir"; then
    echo "✓ Successfully cloned private repository"
else
    echo "✗ Failed to clone private repository (timeout or error), skipping private repository push"
    rm -rf "$temp_dir"
    echo ""
    echo "========================================"
    echo "✓ Push completed (private repository push failed)"
    echo "========================================"
    exit 0
fi

cd "$temp_dir"

if mkdir -p "$PRIVATE_DIR"; then
    echo "✓ Created directory: $PRIVATE_DIR"
    target_dir="$PRIVATE_DIR"
else
    echo "✗ Failed to create directory, uploading directly to root directory"
    target_dir="."
fi

for item in "${FILES[@]}"; do
    if [ -d "$OSCHECKPERF_DIR/$item" ]; then
        cp -r "$OSCHECKPERF_DIR/$item" "$target_dir/"
        echo "✓ Copied directory: $item to $target_dir"
    elif [ -f "$OSCHECKPERF_DIR/$item" ]; then
        cp "$OSCHECKPERF_DIR/$item" "$target_dir/"
        echo "✓ Copied file: $item to $target_dir"
    elif [ -d "../$item" ]; then
        cp -r "../$item" "$target_dir/"
        echo "✓ Copied directory: $item to $target_dir"
    elif [ -f "../$item" ]; then
        cp "../$item" "$target_dir/"
        echo "✓ Copied file: $item to $target_dir"
    else
        echo "✗ File or directory does not exist: $item"
    fi
done

if [ -d "$PRIVATE_DIR" ]; then
    git add "$PRIVATE_DIR/"
else
    git add .
fi

if git status --porcelain | grep -q "^[MADRC]"; then
    git commit -m "Update oscheckperf tool scripts - $tag"
    git remote set-url origin $(echo "$PRIVATE_REPO" | sed "s|https://|https://oauth2:${GITEE_TOKEN}@|g")
    if timeout "$TIMEOUT_SECONDS" git push origin master; then
        echo "✓ Successfully pushed files to private repository"
    else
        echo "✗ Failed to push files to private repository"
    fi
else
    echo "⚠ No changes to private repository files, forcing commit to ensure files are pushed"
    git commit --allow-empty -m "Force commit - Update oscheckperf tool scripts - $tag"
    git remote set-url origin $(echo "$PRIVATE_REPO" | sed "s|https://|https://oauth2:${GITEE_TOKEN}@|g")
    if timeout "$TIMEOUT_SECONDS" git push origin master; then
        echo "✓ Successfully pushed files to private repository"
    else
        echo "✗ Failed to push files to private repository"
    fi
fi

cd "$OSCHECKPERF_DIR" || cd ..
rm -rf "$temp_dir"
echo "✓ Cleaned up temporary directory"

echo ""
echo "========================================"
echo "✓ Push completed"
echo "========================================"
