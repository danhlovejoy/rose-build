#!/bin/bash
# ============================================================
# build.sh — Canvas Build Pipeline
#
# Transforms source HTML files (with external CSS references)
# into Canvas-ready HTML files (with inline styles, body only).
#
# When used as a submodule (rose-build/build/build.sh):
#   Called from a course repo wrapper script. COURSE_ROOT env var
#   or auto-detected as the course repo root.
#
# Usage (from course repo root via wrapper):
#   ./build.sh                    # Build everything in this course
#   ./build.sh module1            # Build one module
#
# Usage (from rose/ workspace, legacy):
#   ./build.sh                    # Build all courses
#   ./build.sh aiml2003/module1   # Build one module
#   ./build.sh aiml2003           # Build one course
#
# Output goes to: build/output/ (relative to course or workspace root)
# Source files are never modified.
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Determine mode: submodule (inside a course repo) or workspace (rose/ root)
# If SCRIPT_DIR ends in rose-build/build, we're a submodule
if [[ "$SCRIPT_DIR" == */rose-build/build ]]; then
    # Submodule mode: course root is two levels up from script
    ROOT_DIR="${COURSE_ROOT:-$(dirname "$(dirname "$SCRIPT_DIR")")}"
    CSS_PATH="$SCRIPT_DIR/../course-styles.css"
    MODE="course"
else
    # Workspace/legacy mode: root is parent of build/
    ROOT_DIR="$(dirname "$SCRIPT_DIR")"
    CSS_PATH="$ROOT_DIR/course-styles.css"
    MODE="workspace"
fi

BUILD_DIR="$ROOT_DIR/build/output"
INLINER="$SCRIPT_DIR/inline_css.py"

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Canvas Build Pipeline${NC}"
echo "Root: $ROOT_DIR"
echo "CSS:  $CSS_PATH"
echo "Output: $BUILD_DIR"
echo ""

# Determine what to build
TARGET="${1:-all}"

build_dir() {
    local src_dir="$1"
    local no_recurse="${2:-}"
    local rel_path
    rel_path="$(python3 -c "import os; print(os.path.relpath('$src_dir', '$ROOT_DIR'))")"
    local out_dir="$BUILD_DIR/$rel_path"

    # Count HTML files (top-level only)
    local count
    count=$(find "$src_dir" -name '*.html' -maxdepth 1 | wc -l | tr -d ' ')
    if [ "$count" -eq 0 ]; then
        return
    fi

    local extra_flags=""
    if [ "$no_recurse" = "--no-recurse" ]; then
        extra_flags="--no-recurse"
    fi

    echo -e "${YELLOW}Building: $rel_path ($count files)${NC}"
    python3 "$INLINER" --css "$CSS_PATH" $extra_flags "$src_dir" "$out_dir"
    echo ""
}

if [ "$MODE" = "course" ]; then
    # Course repo mode: build modules + standalone HTML in course root
    if [ "$TARGET" = "all" ]; then
        # Build standalone HTML files at course root
        standalone_count=$(find "$ROOT_DIR" -maxdepth 1 -name '*.html' | wc -l | tr -d ' ')
        if [ "$standalone_count" -gt 0 ]; then
            build_dir "$ROOT_DIR" --no-recurse
        fi
        # Build each module
        for module_dir in "$ROOT_DIR"/module*/; do
            if [ -d "$module_dir" ]; then
                build_dir "$module_dir"
            fi
        done
    else
        target_dir="$ROOT_DIR/$TARGET"
        if [ -d "$target_dir" ]; then
            build_dir "$target_dir"
        else
            echo -e "${RED}ERROR: Directory not found: $target_dir${NC}"
            exit 1
        fi
    fi
else
    # Workspace mode (legacy): look for aiml*/ course dirs
    if [ "$TARGET" = "all" ]; then
        for course_dir in "$ROOT_DIR"/aiml*/; do
            if [ -d "$course_dir" ]; then
                standalone_count=$(find "$course_dir" -maxdepth 1 -name '*.html' | wc -l | tr -d ' ')
                if [ "$standalone_count" -gt 0 ]; then
                    build_dir "$course_dir" --no-recurse
                fi
                for module_dir in "$course_dir"module*/; do
                    if [ -d "$module_dir" ]; then
                        build_dir "$module_dir"
                    fi
                done
            fi
        done
    else
        target_dir="$ROOT_DIR/$TARGET"
        if [ -d "$target_dir" ]; then
            if ls "$target_dir"/module*/ 1>/dev/null 2>&1; then
                standalone_count=$(find "$target_dir" -maxdepth 1 -name '*.html' | wc -l | tr -d ' ')
                if [ "$standalone_count" -gt 0 ]; then
                    build_dir "$target_dir" --no-recurse
                fi
                for module_dir in "$target_dir"/module*/; do
                    if [ -d "$module_dir" ]; then
                        build_dir "$module_dir"
                    fi
                done
            else
                build_dir "$target_dir"
            fi
        else
            echo -e "${RED}ERROR: Directory not found: $target_dir${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}Build complete.${NC}"
echo "Output in: $BUILD_DIR"
echo ""
echo "Next step: upload to Canvas using the Canvas API or manual paste."
