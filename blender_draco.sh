#!/bin/bash
# Blender Draco Compression - Unix Launcher
# Usage: ./blender_draco.sh [options] input_file
#
# Options:
#   -i FILE       Input file
#   -o FILE       Output file (default: input_compressed.glb)
#   --draco-level N    Compression level 0-10 (default: 7)
#   --resize-textures  Enable texture resizing (default)
#   --no-resize        Disable texture resizing
#   --texture-size N   Max texture size (default: 512)
#   --batch            Batch mode (input is directory)
#   --output-dir DIR   Output directory for batch mode
#   --format glb|gltf  Output format (default: glb)
#   -q, --quiet        Quiet mode
#   -h, --help        Show help
#
# Examples:
#   ./blender_draco.sh model.glb
#   ./blender_draco.sh -i model.glb -o compressed.glb --draco-level 10
#   ./blender_draco.sh --batch ./models/ --output-dir ./compressed/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPRESS_SCRIPT="$SCRIPT_DIR/compress.py"

# Blender paths for different systems
find_blender() {
    if [ -n "$BLENDER_PATH" ] && [ -f "$BLENDER_PATH" ]; then
        echo "$BLENDER_PATH"
        return 0
    fi

    case "$(uname -s)" in
        Linux*)
            for path in /usr/bin/blender /usr/local/bin/blender /opt/blender/blender "$HOME"/blender*/blender; do
                if [ -f "$path" ]; then
                    echo "$path"
                    return 0
                fi
            done
            ;;
        Darwin*)
            for path in /Applications/Blender.app/Contents/MacOS/Blender "$HOME/Applications/Blender.app/Contents/MacOS/Blender"; do
                if [ -f "$path" ]; then
                    echo "$path"
                    return 0
                fi
            done
            ;;
    esac

    if command -v blender &> /dev/null; then
        command -v blender
        return 0
    fi

    return 1
}

if [ ! -f "$COMPRESS_SCRIPT" ]; then
    echo "Error: compress.py not found in $SCRIPT_DIR" >&2
    exit 1
fi

BLENDER_EXE=$(find_blender)

if [ -z "$BLENDER_EXE" ]; then
    echo "Error: Blender not found!" >&2
    echo "" >&2
    echo "Please either:" >&2
    echo "  1. Install Blender from https://blender.org" >&2
    echo "  2. Set BLENDER_PATH environment variable" >&2
    echo "  3. Make sure 'blender' is in your PATH" >&2
    exit 1
fi

echo "Using Blender: $BLENDER_EXE"

# Build the command
CMD="$BLENDER_EXE --background --python '$COMPRESS_SCRIPT' --"

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -i|--input)
            CMD="$CMD -i '$2'"
            shift 2
            ;;
        -o|--output)
            CMD="$CMD -o '$2'"
            shift 2
            ;;
        -d|--output-dir)
            CMD="$CMD --output-dir '$2'"
            shift 2
            ;;
        --draco-level)
            CMD="$CMD --draco-level $2"
            shift 2
            ;;
        --texture-size)
            CMD="$CMD --texture-size $2"
            shift 2
            ;;
        --format)
            CMD="$CMD --format $2"
            shift 2
            ;;
        --batch)
            CMD="$CMD --batch"
            shift
            ;;
        --resize-textures)
            CMD="$CMD --resize-textures"
            shift
            ;;
        --no-resize)
            CMD="$CMD --no-resize"
            shift
            ;;
        -q|--quiet)
            CMD="$CMD -q"
            shift
            ;;
        -h|--help)
            CMD="$CMD --help"
            shift
            ;;
        -*)
            CMD="$CMD '$1'"
            shift
            ;;
        *)
            CMD="$CMD '$1'"
            shift
            ;;
    esac
done

echo ""
eval "$CMD"
exit $?
