# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

class VIEW3D_PIE_MT_gp_pivots(Menu):
    bl_idname = "PIE_MT_gp_pivots"
    bl_label = "Grease Pencil Workspace Settings"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        active_mode = context.mode

        if "EDIT" in active_mode:
            # Match the mesh edit mode transform layout
            # WEST / EAST
            pie.operator("wm.call_menu_pie", text='Orientation...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_orientations_pie"
            pie.operator("wm.call_menu_pie", text='Pivot...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_pivot_pie"
            # SOUTH / NORTH
            pie.operator("wm.call_menu_pie", text='Snap...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_snap"
            pie.operator("wm.call_menu_pie", text='Proportional...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_proportional_edt"
            # NW / NE / SW / SE
            pie.separator()
            pie.operator("wm.call_menu_pie", text='Set Origin...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_set_origin"
            pie.separator()
            pie.separator()
        else:
            # Active brush properties layout for Paint and Sculpt environments
            paint_struct = context.tool_settings.gpencil_sculpt if "SCULPT" in active_mode else context.tool_settings.gpencil_paint
            
            # WEST / EAST
            pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = "SUBPIE_MT_brush_falloff"
            pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = "SUBPIE_MT_brush_stroke"
            # SOUTH / NORTH
            pie.separator()
            pie.separator()
            # NORTH-WEST
            pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = "SUBPIE_MT_brush_symmetry"
            # NE / SW / SE
            pie.separator()
            pie.separator()
            pie.separator()

registry = [
    VIEW3D_PIE_MT_gp_pivots,
]

def register():
    keymaps = [
        "Grease Pencil Edit Mode", "Grease Pencil Sculpt Mode", "Grease Pencil Paint Mode",
        "Grease Pencil Stroke Edit Mode", "Grease Pencil Stroke Sculpt Mode", "Grease Pencil Stroke Paint Mode"
    ]
    for km in keymaps:
        try:
            WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
                pie_name=VIEW3D_PIE_MT_gp_pivots.bl_idname,
                hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
                keymap_name=km,
            )
        except Exception:
            pass