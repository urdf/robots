#!/usr/bin/env python3
"""Inline part file contents into .parts.json for single-fetch loading.

Reads each *.parts.json, inlines the XML from its parts/ directory into a
'contents' field, and writes the file back in-place. The loader uses
'contents' if present, skipping the individual part fetches.

Run from the repo root: python3 scripts/bundle.py  (or: make bundle)
"""

import glob
import json
import os
import sys


def bundle_parts_json(path):
    with open(path) as f:
        manifest = json.load(f)

    parts = manifest.get('parts', [])
    if not parts:
        return False

    parts_dir = os.path.join(os.path.dirname(path), 'parts')
    if not os.path.isdir(parts_dir):
        print(f'  skip {path}: no parts/ directory', file=sys.stderr)
        return False

    contents = {}
    missing = []
    for part in parts:
        part_path = os.path.join(parts_dir, part)
        if os.path.isfile(part_path):
            with open(part_path) as f:
                contents[part] = f.read()
        else:
            missing.append(part)

    if missing:
        print(f'  error {path}: missing parts: {missing}', file=sys.stderr)
        sys.exit(1)

    manifest['contents'] = contents
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')

    print(f'  bundled {path}: {len(contents)} parts inlined')
    return True


def main():
    paths = sorted(glob.glob('*/*.parts.json'))
    if not paths:
        print('No *.parts.json files found.')
        return

    count = sum(1 for p in paths if bundle_parts_json(p))
    print(f'bundle: done ({count} file(s) updated)')


if __name__ == '__main__':
    main()
