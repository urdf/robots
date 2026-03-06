#!/usr/bin/env python3
"""Generate robot-car wheel STL with tread blocks.

Axis: Z  (matches URDF <cylinder> convention — the joint's rpy handles orientation)
Center: origin
Outer radius: 32.5 mm   Width: 15 mm
Tread: 16 columns × 4 rows of raised rectangular blocks (1.5 mm proud)
"""

import struct
import numpy as np

# ─── Dimensions ───────────────────────────────────────────────────────────────
R_OUTER = 0.0325   # full outer radius (top of tread)
R_BASE  = 0.0310   # base cylinder radius
W       = 0.026    # wheel width (along Z)

N_SEG   = 64       # polygon count for smooth base cylinder
N_CIRC  = 16       # tread block columns around circumference
N_WIDE  = 7        # tread block rows along width
BLOCK_ARC_FRAC = 0.58   # fraction of arc slot occupied by block
BLOCK_Z_FRAC   = 0.62   # fraction of Z slot occupied by block

# ─── STL helpers ──────────────────────────────────────────────────────────────

def write_stl(filename, triangles):
    header = b'robot-car wheel' + b'\x00' * 65
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', len(triangles)))
        for v0, v1, v2 in triangles:
            v0, v1, v2 = np.asarray(v0, float), np.asarray(v1, float), np.asarray(v2, float)
            n = np.cross(v1 - v0, v2 - v0)
            ln = np.linalg.norm(n)
            if ln > 1e-14:
                n /= ln
            f.write(struct.pack('<3f', *n))
            f.write(struct.pack('<3f', *v0))
            f.write(struct.pack('<3f', *v1))
            f.write(struct.pack('<3f', *v2))
            f.write(struct.pack('<H', 0))

def quad(tris, v0, v1, v2, v3):
    """Append quad as two CCW triangles (v0→v1→v2→v3 order)."""
    tris.append((v0, v1, v2))
    tris.append((v0, v2, v3))

# ─── Build geometry ───────────────────────────────────────────────────────────

tris = []

# Base cylinder
for i in range(N_SEG):
    a0 = 2 * np.pi * i / N_SEG
    a1 = 2 * np.pi * (i + 1) / N_SEG
    c0, s0 = np.cos(a0), np.sin(a0)
    c1, s1 = np.cos(a1), np.sin(a1)

    b00 = (R_BASE * c0, R_BASE * s0, -W/2)
    b10 = (R_BASE * c1, R_BASE * s1, -W/2)
    b01 = (R_BASE * c0, R_BASE * s0,  W/2)
    b11 = (R_BASE * c1, R_BASE * s1,  W/2)

    quad(tris, b00, b10, b11, b01)                          # outer side
    tris.append(((0, 0, -W/2), b10, b00))                  # -Z cap
    tris.append(((0, 0,  W/2), b01, b11))                  # +Z cap

# Tread blocks
arc_slot = 2 * np.pi / N_CIRC
z_slot   = W / N_WIDE

for ci in range(N_CIRC):
    a_mid = arc_slot * (ci + 0.5)
    a0 = a_mid - arc_slot * BLOCK_ARC_FRAC / 2
    a1 = a_mid + arc_slot * BLOCK_ARC_FRAC / 2

    for wi in range(N_WIDE):
        z_mid = -W/2 + z_slot * (wi + 0.5)
        z0 = z_mid - z_slot * BLOCK_Z_FRAC / 2
        z1 = z_mid + z_slot * BLOCK_Z_FRAC / 2

        # 8 corners: base (R_BASE) and top (R_OUTER)
        c0a0 = np.array([R_BASE  * np.cos(a0), R_BASE  * np.sin(a0), z0])
        c1a0 = np.array([R_BASE  * np.cos(a1), R_BASE  * np.sin(a1), z0])
        c0a1 = np.array([R_BASE  * np.cos(a0), R_BASE  * np.sin(a0), z1])
        c1a1 = np.array([R_BASE  * np.cos(a1), R_BASE  * np.sin(a1), z1])
        t0a0 = np.array([R_OUTER * np.cos(a0), R_OUTER * np.sin(a0), z0])
        t1a0 = np.array([R_OUTER * np.cos(a1), R_OUTER * np.sin(a1), z0])
        t0a1 = np.array([R_OUTER * np.cos(a0), R_OUTER * np.sin(a0), z1])
        t1a1 = np.array([R_OUTER * np.cos(a1), R_OUTER * np.sin(a1), z1])

        quad(tris, t0a0, t1a0, t1a1, t0a1)     # outer face  (radially out)
        quad(tris, c0a0, t0a0, t0a1, c0a1)     # a0 side     (CW tangent)
        quad(tris, c1a0, c1a1, t1a1, t1a0)     # a1 side     (CCW tangent)
        quad(tris, c0a0, c1a0, t1a0, t0a0)     # z0 face     (−Z)
        quad(tris, t0a1, t1a1, c1a1, c0a1)     # z1 face     (+Z)

# ─── Write ────────────────────────────────────────────────────────────────────
out = 'wheel.stl'
write_stl(out, tris)
print(f"Written {out}  ({len(tris)} triangles, {N_CIRC}×{N_WIDE} tread blocks)")
