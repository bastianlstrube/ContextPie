# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class SUBPIE_MT_meshSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("mesh.region_to_loop", text='Boundary')
        # EAST
        pie.operator("mesh.select_edge_ring_multi", text='Ring')
        # SOUTH
        pie.operator("mesh.select_edge_loop_multi", text='Loop')
        # NORTH
        pie.operator("mesh.select_nth", text='Checker Deselect')
        # NORTH-WEST
        pie.operator("mesh.select_all", text='Invert').action = 'INVERT'
        # NORTH-EAST
        pie.operator("mesh.select_mirror", text='Mirror')
        # SOUTH-WEST
        pie.operator("mesh.loop_to_region", text='Inside')
        # SOUTH-EAST
        pie.operator("mesh.select_linked", text='Linked')


# Sub Pie for mesh face split/separate operators
class SUBPIE_MT_separate(Menu):
    bl_label = "Split/Separate"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("mesh.split")
        # EAST
        pie.operator("mesh.separate", text='By Loose Parts').type = 'LOOSE'
        # SOUTH
        pie.operator("mesh.rip_move")
        # NORTH
        pie.separator()

        # NORTH-WEST
        pie.operator("mesh.edge_split", text='Split By Edge').type = 'EDGE'
        # NORTH-EAST
        pie.operator("mesh.separate", text='By Material').type = 'MATERIAL'
        # SOUTH-WEST
        pie.operator("mesh.edge_split", text='Split By Vertex').type = 'VERT'
        # SOUTH-EAST
        pie.operator("mesh.separate", text='Selection').type = 'SELECTED'


class CPIE_MT_mode_editmesh(Menu):
    bl_idname = "CPIE_MT_mode_editmesh"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
        # SOUTH
        pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
        # NORTH
        pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'
        # NORTH-WEST — reserved for a normals sub-pie
        pie.separator()
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Split/Separate...').name = "SUBPIE_MT_separate"
        # SOUTH-WEST
        pie.menu("VIEW3D_MT_edit_mesh_context_menu", text="Context Menu", icon="COLLAPSEMENU")
        # SOUTH-EAST
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_meshSelect"


registry = [
    SUBPIE_MT_meshSelect,
    SUBPIE_MT_separate,
    CPIE_MT_mode_editmesh,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    if "Mesh" not in default_keymaps:
        return
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=CPIE_MT_mode_editmesh.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        keymap_name="Mesh",
        on_drag=True,
    )
