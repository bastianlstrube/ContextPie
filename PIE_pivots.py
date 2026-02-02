# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class VIEW3D_PIE_MT_pivots(Menu):
    bl_idname = "PIE_MT_context_pivots"
    bl_label = "Pivots Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        if context.mode in ('EDIT_MESH', 'EDIT_CURVE', 'EDIT_LATTICE', 'EDIT_ARMATURE'):
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
            # SOUTH-WEST
            pie.operator("wm.call_menu_pie", text='Align...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_mesh_align"
            # SOUTH-EAST
            pie.separator()

        elif context.mode in ('OBJECT', 'POSE'):
            # WEST
            pie.operator("wm.call_menu_pie", text='Orientation...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_orientations_pie"
            # EAST
            pie.operator("wm.call_menu_pie", text='Pivot...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_pivot_pie"
            # SOUTH
            pie.operator("wm.call_menu_pie", text='Snap...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_snap"
            # NORTH
            pie.operator("wm.call_menu_pie", text='Proportional...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_proportional_obj"
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.operator("wm.call_menu_pie", text='Set Origin...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_set_origin"
            # SOUTH-WEST
            pie.separator()
            # SOUTH-EAST
            pie.separator()


registry = [
    VIEW3D_PIE_MT_pivots,
]


def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=VIEW3D_PIE_MT_pivots.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
        keymap_name="3D View",
    )
