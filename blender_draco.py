#!/usr/bin/env python3
"""
Blender Draco CLI - Python Launcher
Wrapper to launch Blender with the compression script

Usage:
    python blender_draco.py [options] input_file

Options:
    Same as compress.py

Examples:
    python blender_draco.py input.glb
    python blender_draco.py -i input.glb -o output.glb --draco-level 10
    python blender_draco.py --batch ./models/ --output-dir ./compressed/
"""

import os
import sys
import subprocess
import argparse


BLENDER_PATHS = {
    'windows': [
        r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 2.93\blender.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation\Blender 4.4\blender.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation\Blender 4.3\blender.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation\Blender 4.2\blender.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation\Blender 4.0\blender.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation\Blender 3.6\blender.exe"),
    ],
    'linux': [
        '/usr/bin/blender',
        '/usr/local/bin/blender',
        '/opt/blender/blender',
        os.path.expanduser('~/blender*/blender'),
    ],
    'macos': [
        '/Applications/Blender.app/Contents/MacOS/Blender',
        os.path.expanduser('~/Applications/Blender.app/Contents/MacOS/Blender'),
    ]
}


def find_blender():
    system = sys.platform

    if system.startswith('win'):
        paths = BLENDER_PATHS['windows']
    elif system == 'darwin':
        paths = BLENDER_PATHS['macos']
    else:
        paths = BLENDER_PATHS['linux']

    for path in paths:
        if '*' in path:
            import glob
            matches = glob.glob(path)
            if matches:
                return matches[0]
        elif os.path.exists(path):
            return path

    blender_env = os.environ.get('BLENDER_PATH')
    if blender_env and os.path.exists(blender_env):
        return blender_env

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Compress 3D meshes with Draco compression using Blender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blender_draco.py input.glb
  python blender_draco.py -i input.glb -o output.glb --draco-level 10
  python blender_draco.py --batch ./models/ --output-dir ./compressed/

Environment:
  BLENDER_PATH    Set custom path to Blender executable
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='Input file or directory'
    )

    parser.add_argument(
        '-i', '--input',
        dest='input_file',
        help='Input file (alternative to positional argument)'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output',
        help='Output file (default: input_compressed.glb)'
    )

    parser.add_argument(
        '--draco-level',
        type=int,
        default=7,
        help='Draco compression level 0-10 (default: 7)'
    )

    parser.add_argument(
        '--resize-textures',
        action='store_true',
        default=True,
        help='Enable texture resizing (default: enabled)'
    )

    parser.add_argument(
        '--no-resize',
        action='store_true',
        help='Disable texture resizing'
    )

    parser.add_argument(
        '--texture-size',
        type=int,
        default=512,
        help='Max texture size in pixels (default: 512)'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch mode: process all files in input directory'
    )

    parser.add_argument(
        '--output-dir', '-d',
        dest='output_dir',
        help='Output directory for batch mode'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['glb', 'gltf'],
        default='glb',
        help='Output format (default: glb)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode'
    )

    parser.add_argument(
        '--blender-path',
        dest='blender_path',
        help='Custom path to Blender executable'
    )

    args = parser.parse_args()

    blender_path = args.blender_path or find_blender()

    if not blender_path:
        print("Error: Blender not found!")
        print("\nPlease either:")
        print("  1. Install Blender from https://blender.org")
        print("  2. Set BLENDER_PATH environment variable")
        print("  3. Use --blender-path to specify location")
        sys.exit(1)

    if not os.path.exists(blender_path):
        print(f"Error: Blender not found at: {blender_path}")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    compress_script = os.path.join(script_dir, 'compress.py')

    if not os.path.exists(compress_script):
        print(f"Error: compress.py not found at: {compress_script}")
        sys.exit(1)

    if not args.input and not args.input_file:
        print("Error: Input file or directory is required")
        parser.print_help()
        sys.exit(1)

    input_path = args.input or args.input_file

    cmd = [
        blender_path,
        '--background',
        '--python', compress_script,
        '--'
    ]

    if args.input:
        cmd.append(args.input)
    else:
        cmd.extend(['-i', args.input_file])

    if args.output:
        cmd.extend(['-o', args.output])

    cmd.extend(['--draco-level', str(args.draco_level)])

    if args.no_resize:
        cmd.append('--no-resize')

    if args.texture_size != 512:
        cmd.extend(['--texture-size', str(args.texture_size)])

    if args.batch:
        cmd.append('--batch')

    if args.output_dir:
        cmd.extend(['--output-dir', args.output_dir])

    if args.format != 'glb':
        cmd.extend(['--format', args.format])

    if args.quiet:
        cmd.append('--quiet')

    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)


if __name__ == '__main__':
    main()
