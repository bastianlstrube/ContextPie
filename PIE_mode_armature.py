# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class SUBPIE_MT_armatureSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator_enum("armature.select_similar", "type")


class SUBPIE_MT_poseSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator_enum("pose.select_grouped", "type")


class CPIE_MT_mode_armature(Menu):
    bl_idname = "CPIE_MT_mode_armature"
    bl_label = "Mode Pie: Armature"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        # SOUTH
        op = pie.operator("armature.select_hierarchy", icon="OUTLINER_OB_ARMATURE", text='Select Child')
        op.direction = 'CHILD'
        op.extend = False
        # NORTH
        op = pie.operator("armature.select_hierarchy", icon="USER", text='Select Parent')
        op.direction = 'PARENT'
        op.extend = False
        # NW
        op = pie.operator("armature.select_hierarchy", text='Add Select Parents')
        op.direction = 'PARENT'
        op.extend = True
        # NE
        op = pie.operator("armature.select_hierarchy", text='Add Select Children')
        op.direction = 'CHILD'
        op.extend = True
        # SW
        pie.menu("VIEW3D_MT_edit_armature_names")
        # SE
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_armatureSelect"


class CPIE_MT_mode_pose(Menu):
    bl_idname = "CPIE_MT_mode_pose"
    bl_label = "Mode Pie: Pose"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        # SOUTH
        op = pie.operator("pose.select_hierarchy", icon="OUTLINER_OB_ARMATURE", text='Select Child')
        op.direction = 'CHILD'
        op.extend = False
        # NORTH
        op = pie.operator("pose.select_hierarchy", icon="USER", text='Select Parent')
        op.direction = 'PARENT'
        op.extend = False
        # NW
        op = pie.operator("pose.select_hierarchy", text='Add Select Parents')
        op.direction = 'PARENT'
        op.extend = True
        # NE
        op = pie.operator("pose.select_hierarchy", text='Add Select Children')
        op.direction = 'CHILD'
        op.extend = True
        # SW
        pie.menu("VIEW3D_MT_pose_context_menu", text="Pose Context Menu", icon="COLLAPSEMENU")
        # SE
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_poseSelect"


registry = [
    SUBPIE_MT_armatureSelect,
    SUBPIE_MT_poseSelect,
    CPIE_MT_mode_armature,
    CPIE_MT_mode_pose,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    for menu, keymap_name in (
        (CPIE_MT_mode_armature, "Armature"),
        (CPIE_MT_mode_pose, "Pose"),
    ):
        if keymap_name not in default_keymaps:
            continue
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=menu.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
            keymap_name=keymap_name,
            on_drag=True,
        )
