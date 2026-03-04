// Generates chassis.stl for the 2WD Robot Car.
// Run:  node example/public/robots/robot-car/gen_chassis.cjs
//
// Shape is defined in URDF coordinates: Y = forward/back, X = left/right.
// After extrusion the geometry is rotated so it sits correctly in the viewer.

const THREE = require('three');
const path  = require('path');
const fs    = require('fs');

const thick = 0.003;
const bodyHW   = 0.062;
const rearHW   = 0.095;
const rearY    = 0.115;
const rearR    = 0.010;
const stepY    = 0.080;
const frontY   = -0.145;
const frontR   = bodyHW;

const s = new THREE.Shape();

s.moveTo(-rearHW + rearR, rearY);
s.lineTo(rearHW - rearR, rearY);
s.quadraticCurveTo(rearHW, rearY, rearHW, rearY - rearR);
s.lineTo(rearHW, stepY);
s.lineTo(bodyHW, stepY);
s.lineTo(bodyHW, frontY + frontR);
s.absarc(0, frontY + frontR, bodyHW, 0, -Math.PI, true);
s.lineTo(-bodyHW, stepY);
s.lineTo(-rearHW, stepY);
s.lineTo(-rearHW, rearY - rearR);
s.quadraticCurveTo(-rearHW, rearY, -rearHW + rearR, rearY);



function rectH(cx, cy, w, h, cr = 0.0008) {
  const p = new THREE.Path();
  p.moveTo(cx - w/2 + cr, cy - h/2);
  p.lineTo(cx + w/2 - cr, cy - h/2);
  p.quadraticCurveTo(cx + w/2, cy - h/2, cx + w/2, cy - h/2 + cr);
  p.lineTo(cx + w/2, cy + h/2 - cr);
  p.quadraticCurveTo(cx + w/2, cy + h/2, cx + w/2 - cr, cy + h/2);
  p.lineTo(cx - w/2 + cr, cy + h/2);
  p.quadraticCurveTo(cx - w/2, cy + h/2, cx - w/2, cy + h/2 - cr);
  p.lineTo(cx - w/2, cy - h/2 + cr);
  p.quadraticCurveTo(cx - w/2, cy - h/2, cx - w/2 + cr, cy - h/2);
  return p;
}

function circH(cx, cy, r) {
  const p = new THREE.Path();
  p.absarc(cx, cy, r, 0, Math.PI * 2, false);
  return p;
}


// Motor pass-through cutouts
// Centered at y=0.093 (rear zone, y>stepY=0.080) so the full hole stays within
// rearHW=0.095; at y=0.070 (body zone) bodyHW=0.062 < hole x-extent=0.081,
// which put the holes entirely outside the shape and caused earcut phantom geometry.
s.holes.push(rectH(-0.075, 0.093, 0.012, 0.014, 0.001));
s.holes.push(rectH( 0.075, 0.093, 0.012, 0.014, 0.001));

// Large center cutout
;(function () {
  const p = new THREE.Path();
  const cx = 0, cy = 0.050;
  p.moveTo(cx - 0.025, cy - 0.035);
  p.lineTo(cx - 0.025, cy - 0.018);
  p.lineTo(cx - 0.033, cy - 0.018);
  p.lineTo(cx - 0.033, cy + 0.002);
  p.lineTo(cx - 0.025, cy + 0.002);
  p.lineTo(cx - 0.025, cy + 0.018);
  p.lineTo(cx - 0.015, cy + 0.028);
  p.lineTo(cx + 0.015, cy + 0.028);
  p.lineTo(cx + 0.025, cy + 0.018);
  p.lineTo(cx + 0.025, cy + 0.002);
  p.lineTo(cx + 0.033, cy + 0.002);
  p.lineTo(cx + 0.033, cy - 0.018);
  p.lineTo(cx + 0.025, cy - 0.018);
  p.lineTo(cx + 0.025, cy - 0.035);
  p.lineTo(cx - 0.025, cy - 0.035);
  s.holes.push(p);
})();

// Wiring slots
s.holes.push(rectH(-0.025, 0.098, 0.018, 0.006, 0.001));
s.holes.push(rectH( 0.025, 0.098, 0.018, 0.006, 0.001));
s.holes.push(rectH(0,      0.090, 0.014, 0.004, 0.001));

// Front slots
s.holes.push(rectH(-0.025, -0.085, 0.018, 0.004, 0.001));
s.holes.push(rectH( 0.025, -0.085, 0.018, 0.004, 0.001));
s.holes.push(circH(0, -0.098, 0.006));

// Mounting holes
const hr = 0.002;
s.holes.push(circH(-0.080,  0.105, hr));
s.holes.push(circH( 0.080,  0.105, hr));
s.holes.push(circH(-0.080,  0.083, hr));
s.holes.push(circH( 0.080,  0.083, hr));
s.holes.push(circH(-0.020,  0.108, hr));
s.holes.push(circH( 0.020,  0.108, hr));
s.holes.push(circH(-0.048,  0.010, hr));
s.holes.push(circH( 0.048,  0.010, hr));
s.holes.push(circH(-0.048, -0.030, hr));
s.holes.push(circH( 0.048, -0.030, hr));
s.holes.push(circH( 0,     -0.020, hr));
s.holes.push(circH(-0.014, -0.065, hr));
s.holes.push(circH( 0.014, -0.065, hr));
s.holes.push(circH(-0.014, -0.052, hr));
s.holes.push(circH( 0.014, -0.052, hr));
s.holes.push(circH(-0.040, -0.062, hr));
s.holes.push(circH( 0.040, -0.062, hr));


const geo = new THREE.ExtrudeGeometry(s, {
  depth: thick, bevelEnabled: false, curveSegments: 48,
});
geo.rotateZ(-Math.PI / 2);


const posAttr = geo.getAttribute('position');
const index   = geo.getIndex();

const verts = [];
for (let i = 0; i < posAttr.count; i++)
  verts.push([posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i)]);

const tris = [];
if (index) {
  for (let i = 0; i < index.count; i += 3)
    tris.push([index.getX(i), index.getX(i + 1), index.getX(i + 2)]);
} else {
  for (let i = 0; i < posAttr.count; i += 3)
    tris.push([i, i + 1, i + 2]);
}

const buf = Buffer.alloc(84 + tris.length * 50);
buf.write('Binary STL — 2WD Robot Car Chassis v2', 0);
buf.writeUInt32LE(tris.length, 80);

let off = 84;
for (const [a, b, c] of tris) {
  const v0 = verts[a], v1 = verts[b], v2 = verts[c];
  const e1 = [v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]];
  const e2 = [v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]];
  const nx = e1[1]*e2[2] - e1[2]*e2[1];
  const ny = e1[2]*e2[0] - e1[0]*e2[2];
  const nz = e1[0]*e2[1] - e1[1]*e2[0];
  const len = Math.sqrt(nx*nx + ny*ny + nz*nz) || 1;
  buf.writeFloatLE(nx / len, off); off += 4;
  buf.writeFloatLE(ny / len, off); off += 4;
  buf.writeFloatLE(nz / len, off); off += 4;
  for (const v of [v0, v1, v2]) {
    buf.writeFloatLE(v[0], off); off += 4;
    buf.writeFloatLE(v[1], off); off += 4;
    buf.writeFloatLE(v[2], off); off += 4;
  }
  buf.writeUInt16LE(0, off); off += 2;
}

const out = path.join(__dirname, 'chassis.stl');
fs.writeFileSync(out, buf);
console.log(`Wrote ${out}  (${tris.length} triangles, ${buf.length} bytes)`);
