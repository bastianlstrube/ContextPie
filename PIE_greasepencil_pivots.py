# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu


class VIEW3D_PIE_MT_gp_pivots(Menu):
    bl_idname = "PIE_MT_gp_pivots"
    bl_label = "Grease Pencil Workspace Settings"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        draw_gp_pivots_pie(pie, context)


###-----------------------------------------------------------------------------###
###          MODULE-LEVEL DRAW FUNCTION — called from main pivots pie           ###
###-----------------------------------------------------------------------------###

def draw_gp_pivots_pie(pie, context):
    active_mode = context.mode

    if "EDIT" in active_mode:
        # Same transform tools as mesh edit mode
        # WEST
        pie.operator("wm.call_menu_pie", text='Orientation...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_orientations_pie"
        # EAST
        pie.operator("wm.call_menu_pie", text='Pivot...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_pivot_pie"
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Snap...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_snap"
        # NORTH
        pie.operator("wm.call_menu_pie", text='Proportional...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_proportional_edt"
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Set Origin...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_set_origin"
        # SOUTH-WEST / SOUTH-EAST
        pie.separator()
        pie.separator()
    else:
        # Paint / Sculpt: reuse the generic brush tool-settings sub-pies from PIE_3d_pivots.
        # SUBPIE_MT_brush_falloff / stroke / symmetry are registered by PIE_3d_pivots.
        # Note: their _brush_path() helper only handles SCULPT and PAINT_TEXTURE natively;
        # GP modes will open the sub-pie but show limited content.
        # WEST
        pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = "SUBPIE_MT_brush_falloff"
        # EAST
        pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = "SUBPIE_MT_brush_stroke"
        # SOUTH
        pie.separator()
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = "SUBPIE_MT_brush_symmetry"
        # NORTH-EAST / SOUTH-WEST / SOUTH-EAST
        pie.separator()
        pie.separator()
        pie.separator()


registry = [
    VIEW3D_PIE_MT_gp_pivots,
]
