# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this addon is

**ContextPie** is a Blender extension (5.0+) providing three context-sensitive pie menus on right-mouse variants:
- `Shift+RMB` — context pie (main workhorse, mode/selection aware)
- `RMB` — mode selection pie
- `Ctrl+RMB` — pivots pie

Published on extensions.blender.org. No build step — it runs directly from source as a Blender extension.

## Development workflow

Install by pointing Blender's script directories at the parent folder of this repo, or zip the folder and install as an extension. After editing, use **Blender → Scripting → Reload Scripts** (or `bpy.ops.script.reload()`) to reload without restarting.

The `blender_studio_utils` directory is a **git submodule** — run `git submodule update --init` if it is empty.

## Architecture

### Registration pattern
`__init__.py` drives everything. Each module exposes a `registry` list of classes and optional `register()`/`unregister()` functions. `__init__.py` iterates `registry` calling `bpy.utils.register_class`, then calls `register()` for hotkeys. **Never call `bpy.utils.register_class` inside a module's own `register()` — that belongs in `registry`.**

### Hotkeys
All hotkeys go through `WM_OT_call_menu_pie_drag_only_cpie` in `op_pie_wrappers.py`, registered via `blender_studio_utils/hotkeys.py:register_hotkey()`. Each pie's `register()` function calls `WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(...)`. The `on_drag` flag makes the pie appear only on mouse drag, falling back to the default keymap action on click.

### Pie menu files
| File | Keymap | Trigger |
|---|---|---|
| `PIE_context.py` | 3D View + Sculpt | Shift+RMB |
| `PIE_context_node.py` | Node Editor | Shift+RMB |
| `PIE_mode.py` | 3D View | RMB |
| `PIE_pivots.py` | 3D View | Ctrl+RMB |
| `PIE_uvcontext.py` / `PIE_uvmode.py` / `PIE_uvpivots.py` | UV Editor | same pattern |

`SUBPIE_MT_*` classes are sub-pie menus called via `wm.call_menu_pie` with `.name = "SUBPIE_MT_..."`. They live either in the same file as their parent or in dedicated `SUBPIE_*.py` files.

### Conditional addon integration
Check for optional addons at draw time, never at register time:
```python
nw_loaded = "node_wrangler" in context.preferences.addons
has_bool_tool = any(name.endswith("bool_tool") for name in bpy.context.preferences.addons.keys())
looptools = "bl_ext.blender_org.looptools" in bpy.context.preferences.addons
```

## Pie menu conventions

**Directional semantics are consistent across all modes:**
- **NORTH** = merge/combine/join (Merge in Edit Mesh, Join/Bool in Object, Join Geometry in Node Editor)
- **SOUTH** = extrude/extend/add outward
- **WEST** = cut/knife/destructive tools
- **EAST** = connect/bridge/smooth

**Submenu directional clumping:** When a submenu is opened from a direction, its options must cluster toward that direction. The primary item goes at that exact slot; related secondary items fill adjacent slots; separators go on the opposite side. Example: a submenu opened from NORTH puts its primary item at N, secondary items at NW/NE/W, separators at SW/SE/S.

**Slot order** in `pie.operator(...)` calls: W(1), E(2), S(3), N(4), NW(5), NE(6), SW(7), SE(8). Always comment each slot.

**Extras dropdown** (slot 9+): use `pie.separator()` twice, then `pie.column()` with a gap sub-column (`scale_y = 8`) and a `.box().column()` for the items. See `draw_single_node` in `PIE_context_node.py` for the pattern.

**Node Wrangler merge modes** (for `node.nw_merge_nodes`):
- `merge_type='GEOMETRY'`: mode `'JOIN'`=Join Geometry, `'DIFFERENCE'`/`'UNION'`/`'INTERSECT'`=Mesh Boolean
- `merge_type='MATH'`: standard math operations (`'ADD'`, `'MULTIPLY'`, etc.)
- `merge_type='SHADER'`: `'MIX'`=Mix Shader, `'ADD'`=Add Shader
- `merge_type='MIX'`: Mix (color) node
- `merge_type='ALPHAOVER'` / `'DEPTH_COMBINE'`: Compositor only
