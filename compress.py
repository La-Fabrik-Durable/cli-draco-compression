#!/usr/bin/env python3
"""
Blender Draco Compression Script
CLI tool to compress 3D meshes with Draco compression using Blender

Usage:
    blender --background --python compress.py -- [options]

Options:
    -i, --input FILE              Input file (required in advanced mode)
    -o, --output FILE             Output file (default: input_compressed.glb)
    --draco-level LEVEL           Draco compression level 0-10 (default: 7)
    --resize-textures / --no-resize    Enable/disable texture resizing (default: enabled)
    --texture-size SIZE           Max texture size in pixels (default: 512)
    --batch                       Batch mode: input is a directory
    --output-dir DIR              Output directory for batch mode
    --format FORMAT               Output format: glb or gltf (default: glb)
    -q, --quiet                   Quiet mode (less output)
    -h, --help                    Show this help message

Examples:
    # Simple mode (all defaults)
    blender --background --python compress.py -- input.glb

    # Advanced mode
    blender --background --python compress.py -- -i input.glb -o output.glb --draco-level 10

    # Batch mode
    blender --background --python compress.py -- --batch ./models/ --output-dir ./compressed/
"""

import os
import sys
import io
import argparse
from contextlib import redirect_stdout
from pathlib import Path

import bpy
try:
    import bpy_types
except ImportError:
    bpy_types = None


SUPPORTED_IMPORT_FORMATS = {
    '.glb': 'gltf',
    '.gltf': 'gltf',
    '.obj': 'obj',
    '.ply': 'ply',
    '.stl': 'stl',
    '.x3d': 'x3d',
    '.wrl': 'x3d',
    '.3ds': '3ds',
    '.fbx': 'fbx',
    '.dae': 'dae',
}

SUPPORTED_OUTPUT_FORMATS = ['glb', 'gltf']


def file_name(filepath):
    return os.path.split(filepath)[1]


def file_suffix(filepath):
    return os.path.splitext(file_name(filepath))[1].lower()


def dir_path(filepath):
    return os.path.split(filepath)[0]


def get_import_operator(suffix):
    operators = {
        'gltf': bpy.ops.import_scene.gltf,
        'obj': bpy.ops.import_scene.obj,
        'ply': bpy.ops.import_mesh.ply,
        'stl': bpy.ops.import_mesh.stl,
        'x3d': bpy.ops.import_scene.x3d,
        '3ds': bpy.ops.import_scene.fbx,
        'fbx': bpy.ops.import_scene.fbx,
        'dae': bpy.ops.import_scene.dae,
    }
    return operators.get(suffix)


def get_output_extension(format_type):
    return '.glb' if format_type == 'glb' else '.gltf'


def import_mesh(filepath):
    suffix = file_suffix(filepath)
    if suffix not in SUPPORTED_IMPORT_FORMATS:
        raise ValueError(f"Unsupported input format: {suffix}")

    format_type = SUPPORTED_IMPORT_FORMATS[suffix]
    import_op = get_import_operator(format_type)

    if import_op is None:
        raise ValueError(f"Cannot import {suffix} format")

    stdout_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer):
        import_op(filepath=str(filepath))

    output = stdout_buffer.getvalue()
    return output


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    return len(bpy.data.objects) == 0


def resize_textures(target_size):
    resized_count = 0

    for image in bpy.data.images:
        if image.size[0] > target_size or image.size[1] > target_size:
            old_width = image.size[0]
            old_height = image.size[1]

            scale = min(target_size / old_width, target_size / old_height)
            new_width = int(old_width * scale)
            new_height = int(old_height * scale)

            image.scale(new_width, new_height)
            resized_count += 1
            print(f"  Resized '{image.name}': {old_width}x{old_height} -> {new_width}x{new_height}")

    return resized_count


def export_mesh(filepath, draco_level=7, format_type='glb'):
    export_kwargs = {
        'filepath': str(filepath),
        'export_draco_mesh_compression_enable': True,
        'export_draco_mesh_compression_level': draco_level,
        'export_format': 'GLB' if format_type == 'glb' else 'GLTF_SEPARATE',
    }

    stdout_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer):
        bpy.ops.export_scene.gltf(**export_kwargs)

    return stdout_buffer.getvalue()


def get_default_output(input_path, format_type='glb'):
    input_file = Path(input_path)
    suffix = get_output_extension(format_type)
    return str(input_file.parent / f"{input_file.stem}_compressed{suffix}")


def process_file(input_path, output_path=None, draco_level=7,
                 resize_textures_flag=True, texture_size=512,
                 format_type='glb', quiet=False):
    if not quiet:
        print(f"\n{'='*50}")
        print(f"Processing: {input_path}")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not quiet:
        original_size = os.path.getsize(input_path)
        print(f"Original size: {original_size / 1024:.2f} KB")

    if not clear_scene():
        raise RuntimeError("Failed to clear Blender scene")

    if not quiet:
        print("Importing mesh...")

    import_output = import_mesh(input_path)

    if len(bpy.data.objects) == 0:
        raise RuntimeError(f"No objects imported from {input_path}")

    if not quiet:
        mesh_count = sum(1 for obj in bpy.data.objects if isinstance(obj.data, bpy.types.Mesh))
        print(f"Imported {mesh_count} mesh(es)")

    if resize_textures_flag:
        if not quiet:
            print(f"Resizing textures (max: {texture_size}px)...")
        resized = resize_textures(texture_size)
        if not quiet and resized > 0:
            print(f"Resized {resized} texture(s)")

    if output_path is None:
        output_path = get_default_output(input_path, format_type)

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    if not quiet:
        print(f"Exporting with Draco compression (level={draco_level})...")

    export_output = export_mesh(output_path, draco_level, format_type)

    if not os.path.exists(output_path):
        raise RuntimeError(f"Export failed: {output_path} not created")

    final_size = os.path.getsize(output_path)

    if not quiet:
        original_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
        reduction = ((original_size - final_size) / original_size * 100) if original_size > 0 else 0
        print(f"\nOutput: {output_path}")
        print(f"Final size: {final_size / 1024:.2f} KB")
        if original_size > 0:
            print(f"Reduction: {reduction:.1f}%")
        print("Compression complete!")

    return output_path, final_size


def process_batch(input_dir, output_dir=None, draco_level=7,
                  resize_textures_flag=True, texture_size=512,
                  format_type='glb', quiet=False):
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    files_found = []
    for ext in SUPPORTED_IMPORT_FORMATS.keys():
        files_found.extend(Path(input_dir).glob(f"*{ext}"))
        files_found.extend(Path(input_dir).glob(f"*{ext.upper()}"))

    files_found = sorted(set(files_found))

    if not files_found:
        print(f"No supported files found in {input_dir}")
        return []

    if not quiet:
        print(f"\n{'='*50}")
        print(f"BATCH MODE")
        print(f"Input directory: {input_dir}")
        print(f"Files found: {len(files_found)}")

    results = []
    for i, file_path in enumerate(files_found, 1):
        if output_dir:
            input_file = Path(file_path)
            suffix = get_output_extension(format_type)
            output_path = os.path.join(output_dir, f"{input_file.stem}_compressed{suffix}")
        else:
            output_path = None

        if not quiet:
            print(f"\n[{i}/{len(files_found)}]")

        try:
            result_path, _ = process_file(
                str(file_path),
                output_path=output_path,
                draco_level=draco_level,
                resize_textures_flag=resize_textures_flag,
                texture_size=texture_size,
                format_type=format_type,
                quiet=quiet
            )
            results.append((str(file_path), result_path, True, None))
        except Exception as e:
            error_msg = str(e)
            if not quiet:
                print(f"ERROR: {error_msg}")
            results.append((str(file_path), None, False, error_msg))

    success_count = sum(1 for _, _, success, _ in results if success)
    fail_count = len(results) - success_count

    if not quiet:
        print(f"\n{'='*50}")
        print(f"BATCH COMPLETE")
        print(f"Total files: {len(results)}")
        print(f"Success: {success_count}")
        print(f"Failed: {fail_count}")

    return results


def main():
    argv = sys.argv
    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]

    parser = argparse.ArgumentParser(
        description='Compress 3D meshes with Draco compression using Blender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple mode (all defaults)
  blender --background --python compress.py -- input.glb

  # With options
  blender --background --python compress.py -- -i input.glb -o output.glb --draco-level 10

  # Batch mode
  blender --background --python compress.py -- --batch ./models/ --output-dir ./compressed/
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='Input file or directory (for batch mode)'
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
        choices=range(0, 11),
        help='Draco compression level 0-10 (default: 7)'
    )

    resize_group = parser.add_mutually_exclusive_group()
    resize_group.add_argument(
        '--resize-textures',
        action='store_true',
        default=True,
        help='Enable texture resizing (default: enabled)'
    )
    resize_group.add_argument(
        '--no-resize',
        action='store_false',
        dest='resize_textures',
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
        choices=SUPPORTED_OUTPUT_FORMATS,
        default='glb',
        help='Output format (default: glb)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode (less output)'
    )

    args = parser.parse_args(argv)

    input_path = args.input or args.input_file

    if not input_path:
        parser.print_help()
        print("\nError: Input file or directory is required")
        sys.exit(1)

    if args.batch or os.path.isdir(input_path):
        results = process_batch(
            input_path,
            output_dir=args.output_dir,
            draco_level=args.draco_level,
            resize_textures_flag=args.resize_textures,
            texture_size=args.texture_size,
            format_type=args.format,
            quiet=args.quiet
        )
        failed = [r for r in results if not r[2]]
        if failed:
            sys.exit(1)
    else:
        try:
            process_file(
                input_path,
                output_path=args.output,
                draco_level=args.draco_level,
                resize_textures_flag=args.resize_textures,
                texture_size=args.texture_size,
                format_type=args.format,
                quiet=args.quiet
            )
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
