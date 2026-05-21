# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

# Import all draw functions at the top of the file for maximum performance
from .PIE_3d_context_greasepencil import draw_gp_context_pie
from .PIE_3d_context_editmesh import draw_context_editmesh
from .PIE_3d_context_editcurve import draw_context_editcurve
from .PIE_3d_context_armature import draw_context_editarmature, draw_context_pose
from .PIE_3d_context_object import draw_context_object
from .PIE_3d_context_paintsculpt import (
    draw_context_sculpt, 
    draw_context_paint_vertex, 
    draw_context_paint_texture,
    create_icons,
    release_icons
)

_GP_MODES = frozenset({
    'PAINT_GREASE_PENCIL', 'PAINT_GPENCIL',
    'SCULPT_GREASE_PENCIL', 'SCULPT_GPENCIL',
    'EDIT_GREASE_PENCIL', 'EDIT_GPENCIL',
})

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
            draw_gp_context_pie(pie, context)
        elif mode == 'EDIT_MESH':
            draw_context_editmesh(pie, context)
        elif mode == 'EDIT_CURVE':
            draw_context_editcurve(pie, context)
        elif mode == 'EDIT_ARMATURE':
            draw_context_editarmature(pie, context)
        elif mode == 'POSE':
            draw_context_pose(pie, context)
        elif mode == 'OBJECT':
            draw_context_object(pie, context)
        elif mode == 'SCULPT':
            draw_context_sculpt(pie, context)
        elif mode == 'PAINT_VERTEX':
            draw_context_paint_vertex(pie, context)
        elif mode == 'PAINT_TEXTURE':
            draw_context_paint_texture(pie, context)


registry = [
    VIEW3D_PIE_MT_context,
]


def register():
    # Icons are loaded inside the paintsculpt submodule now
    create_icons()
    for keymap_name in ("3D View", "Sculpt", "Image Paint"):
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=VIEW3D_PIE_MT_context.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
            keymap_name=keymap_name,
            on_drag=False,
        )


def unregister():
    release_icons()