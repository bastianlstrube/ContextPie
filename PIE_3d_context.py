# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


_GP_MODES = frozenset({
    'PAINT_GREASE_PENCIL', 'PAINT_GPENCIL',
    'SCULPT_GREASE_PENCIL', 'SCULPT_GPENCIL',
    'EDIT_GREASE_PENCIL', 'EDIT_GPENCIL',
})

_GP_KEYMAPS = (
    "Grease Pencil Paint Mode",
    "Grease Pencil Sculpt Mode",
    "Grease Pencil Edit Mode",
)


###-----------------------------------------------------------------------------###
###                          MAIN CONTEXT PIE MENU                              ###
###-----------------------------------------------------------------------------###

class VIEW3D_PIE_MT_context(Menu):
    bl_idname = "PIE_MT_context_pie"
    bl_label = "Context Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        mode = context.mode

        if mode in _GP_MODES:
            from .PIE_greasepencil_context import draw_gp_context_pie
            draw_gp_context_pie(pie, context)
        elif mode == 'EDIT_MESH':
            from .PIE_3d_context_editmesh import draw_context_editmesh
            draw_context_editmesh(pie, context)
        elif mode == 'EDIT_CURVE':
            from .PIE_3d_context_editcurve import draw_context_editcurve
            draw_context_editcurve(pie, context)
        elif mode == 'EDIT_ARMATURE':
            from .PIE_3d_context_armature import draw_context_editarmature
            draw_context_editarmature(pie, context)
        elif mode == 'POSE':
            from .PIE_3d_context_armature import draw_context_pose
            draw_context_pose(pie, context)
        elif mode == 'OBJECT':
            from .PIE_3d_context_object import draw_context_object
            draw_context_object(pie, context)
        elif mode == 'SCULPT':
            from .PIE_3d_context_paintsculpt import draw_context_sculpt
            draw_context_sculpt(pie, context)
        elif mode == 'PAINT_VERTEX':
            from .PIE_3d_context_paintsculpt import draw_context_paint_vertex
            draw_context_paint_vertex(pie, context)
        elif mode == 'PAINT_TEXTURE':
            from .PIE_3d_context_paintsculpt import draw_context_paint_texture
            draw_context_paint_texture(pie, context)


###-----------------------------------------------------------------------------###
###    BRUSH HELPERS — used by PIE_3d_context_paintsculpt via module import     ###
###-----------------------------------------------------------------------------###

def blender_uses_brush_assets():
    return 'asset_activate' in dir(bpy.ops.brush)


def draw_brush_operator(layout, brush_name: str, brush_icon: str = ""):
    """Draw a brush select operator with pre-4.3 icon support."""
    if blender_uses_brush_assets():
        op = layout.operator('brush.asset_activate', text="     " + brush_name,
                             icon_value=brush_icons.get(brush_icon, 0))
        op.asset_library_type = 'ESSENTIALS'
        if bpy.context.mode == 'SCULPT':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_sculpt.blend", "Brush", brush_name)
        elif bpy.context.mode == 'PAINT_VERTEX':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_vertex.blend", "Brush", brush_name)
        elif bpy.context.mode == 'PAINT_TEXTURE':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_texture.blend", "Brush", brush_name)
    else:
        if brush_icon:
            op = layout.operator("paint.brush_select", text="     " + brush_name,
                                 icon_value=brush_icons.get(brush_icon, 0))
            op.sculpt_tool = brush_icon.upper()
        else:
            layout.separator()


brush_icons = {}


def create_icons():
    global brush_icons
    icons_directory = Path(__file__).parent / "icons"
    for icon_path in icons_directory.iterdir():
        icon_value = bpy.app.icons.new_triangles_from_file(icon_path.as_posix())
        brush_name = icon_path.stem.split(".")[-1]
        brush_icons[brush_name] = icon_value


def release_icons():
    global brush_icons
    for value in brush_icons.values():
        bpy.app.icons.release(value)
    brush_icons = {}


###-----------------------------------------------------------------------------###
###                              REGISTRATION                                   ###
###-----------------------------------------------------------------------------###

registry = [
    VIEW3D_PIE_MT_context,
]


def register():
    create_icons()
    for keymap_name in ("3D View", "Sculpt") + _GP_KEYMAPS:
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=VIEW3D_PIE_MT_context.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
            keymap_name=keymap_name,
            on_drag=False,
        )


def unregister():
    release_icons()
