#!/usr/bin/env bash
# package_courses.sh — Build both standalone Canvas import cartridges in one shot.
#
# Runs build.sh --standalone for each course, then package_course_cartridge.py.
# Output: dist/aiml2003-canvas-import.imscc and dist/aiml2013-canvas-import.imscc.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

for course in aiml2003 aiml2013; do
    echo -e "${YELLOW}── ${course} ──${NC}"
    bash "$SCRIPT_DIR/build.sh" --standalone "$course"
    python3 "$SCRIPT_DIR/package_course_cartridge.py" "$course"
    echo ""
done

echo -e "${GREEN}Done.${NC} Cartridges are in dist/."
ls -lh "$ROOT_DIR/dist/"*.imscc 2>/dev/null || true
