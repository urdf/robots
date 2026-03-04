# urdf/robots

Robot definitions, URDF files, and STL meshes for [urdf.github.io](https://urdf.github.io).

Served at **[urdf.github.io/robots/](https://urdf.github.io/robots/)** via GitHub Pages.

---

## Structure

```
robot-car/          # each robot is a top-level directory
  robot-car.urdf
  robot-car.parts.json   # parts-based robots only
  parts/
  *.stl
catalog.json        # index consumed by the viewer and gallery
index.html          # filterable gallery at urdf.github.io/robots/
```

## Adding a robot

1. Create a directory with your URDF and mesh files.
2. Add an entry to `catalog.json`:

```json
{
  "id": "my_robot",
  "name": "My Robot",
  "label": "MyBot",
  "tags": ["wheeled", "beginner"],
  "up": "+Z",
  "urdf": "my_robot/my_robot.urdf"
}
```

3. Run `make validate` to catch any path errors before pushing.

The viewer at `urdf.github.io/?robot=my_robot` will load it once GitHub Pages deploys.

## `catalog.json` fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | ✓ | Matches directory name; used in `?robot=<id>` deep links |
| `name` | ✓ | Display name |
| `label` | ✓ | Short button label (keep under ~8 chars) |
| `tags` | ✓ | Array of strings for gallery filtering |
| `up` | ✓ | Up axis: `+Z`, `-Z`, `+Y`, etc. |
| `urdf` | one of | Path relative to repo root |
| `parts` | one of | Base path for parts-assembled robots (without `.parts.json`) |
| `package` | | ROS package name (for `package://` URIs) |

## Validation

```sh
make validate   # checks catalog ↔ directories and all paths exist
make lint       # validates JSON syntax only
```
