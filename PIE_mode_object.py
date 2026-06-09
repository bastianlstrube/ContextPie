# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class SUBPIE_MT_objectSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator_enum("object.select_grouped", "type")


class CPIE_MT_mode_object(Menu):
    bl_idname = "CPIE_MT_mode_object"
    bl_label = "Mode Pie: Object"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        obj = context.object
        sel = context.selected_objects

        if obj and sel and obj.type in {'MESH', 'GPENCIL', 'GREASEPENCIL'}:
            # WEST EAST NORTH SOUTH N-W N-E
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"

        elif obj and sel and obj.type in {'CURVE', 'SURFACE', 'LATTICE', 'FONT'}:
            # WEST EAST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            pie.separator() # SOUTH 
            pie.separator() # NORTH
            pie.separator() # NW
            pie.separator() # NE
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"

        elif obj and sel and obj.type == 'ARMATURE':
            pie.operator_enum("OBJECT_OT_mode_set", "mode") # WEST
            pie.separator() # EAST
            pie.separator() # SOUTH
            pie.separator() # NORTH
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"

        elif obj and sel and obj.type in {'EMPTY', 'EMPTY'}: 
            pie.separator() # WEST
            pie.separator() # EAST 
            pie.separator() # SOUTH 
            pie.separator() # NORTH
            pie.separator() # NW
            pie.separator() # NE
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"


class CPIE_MT_mode_lattice(Menu):
    bl_idname = "CPIE_MT_mode_lattice"
    bl_label = "Mode Pie: Lattice"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST SOUTH NORTH N-W N-E
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        # SOUTH WEST
        pie.menu("VIEW3D_MT_edit_lattice_context_menu")


registry = [
    SUBPIE_MT_objectSelect,
    CPIE_MT_mode_object,
    CPIE_MT_mode_lattice,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    for menu, keymap_name in (
        (CPIE_MT_mode_object, "Object Mode"),
        (CPIE_MT_mode_lattice, "Lattice"),
    ):
        if keymap_name not in default_keymaps:
            continue
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=menu.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
            keymap_name=keymap_name,
            on_drag=True,
        )
