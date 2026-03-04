#!/usr/bin/env python3
"""Validate catalog.json is consistent with robot directories and all paths exist."""

import json
import os
import sys

# Top-level names that are not robots
NON_ROBOT = {'.git', 'scripts', 'node_modules', 'index.html', 'catalog.json',
             'Makefile', '.nojekyll', '.gitmodules', 'README.md'}


def main():
    errors = []
    warnings = []

    with open('catalog.json') as f:
        catalog = json.load(f)

    robots = catalog.get('robots', [])
    catalog_ids = {r['id'] for r in robots}

    # Directories that look like they should be robots
    robot_dirs = {
        name for name in os.listdir('.')
        if os.path.isdir(name) and name not in NON_ROBOT and not name.startswith('.')
    }

    # Directories without a catalog entry → warning (robot may be in progress)
    for d in sorted(robot_dirs - catalog_ids):
        warnings.append(f"directory '{d}' has no catalog.json entry")

    # Catalog entries without a directory → error (stale/wrong id)
    for id_ in sorted(catalog_ids - robot_dirs):
        errors.append(f"catalog entry '{id_}' has no matching directory")

    # Each entry's paths must exist on disk
    for r in robots:
        rid = r['id']
        if 'urdf' in r:
            if not os.path.isfile(r['urdf']):
                errors.append(f"[{rid}] urdf not found: {r['urdf']}")
        if 'parts' in r:
            parts_json_path = r['parts'] + '.parts.json'
            if not os.path.isfile(parts_json_path):
                errors.append(f"[{rid}] parts manifest not found: {parts_json_path}")
            else:
                with open(parts_json_path) as f:
                    manifest = json.load(f)
                # If contents are bundled, verify all parts are present
                if 'contents' in manifest:
                    for part in manifest.get('parts', []):
                        if part not in manifest['contents']:
                            errors.append(f"[{rid}] bundled contents missing part: {part} — run 'make bundle'")

    # Output
    for w in warnings:
        print(f"  warning: {w}")
    for e in errors:
        print(f"  error:   {e}")

    if errors:
        print(f"\nvalidate: FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    elif warnings:
        print(f"validate: OK — {len(robots)} robots ({len(warnings)} warning(s))")
    else:
        print(f"validate: OK — {len(robots)} robots, all paths verified")


if __name__ == '__main__':
    main()
