# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Context Pie: 'Shift + Right Mouse'",
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}


import bpy
from bpy.types import Menu
from .hotkeys import register_hotkey
from bpy.app.translations import contexts as i18n_contexts

# Sub Pie Menu for UV Unwrap
class SUBPIE_MT_uvUnwrap(Menu):
    bl_label = "Unwrap"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("uv.smart_project")
        # EAST
        pie.operator("uv.follow_active_quads")
        # SOUTH
        pie.operator("uv.cylinder_project")
        # NORTH
        pie.operator("uv.unwrap")
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        o = pie.operator('wm.context_toggle', text="Live Unwrap")
        o.data_path = 'tool_settings.use_live_unwrap'
        # SOUTH-WEST
        pie.operator("uv.sphere_project")
        # SOUTH-EAST
        pie.operator("uv.cube_project")

# Reference context menu: IMAGE_MT_uvs_context_menu
class IMAGE_PIE_MT_uvContext(Menu):
    bl_label    = "UV Context"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("uv.pin").clear = False
        # EAST
        pie.operator("uv.pin", text='Unpin').clear = True
        # SOUTH
        pie.operator("uv.minimize_stretch")
        # NORTH
        pie.operator("wm.call_menu_pie", text='Unwrap...').name = "SUBPIE_MT_uvUnwrap"
        # NORTH-WEST
        pie.operator("uv.pack_islands")
        # NORTH-EAST
        pie.operator("uv.average_islands_scale")
        # SOUTH-WEST
        pie.operator("mesh.mark_seam", text='Mark Seam').clear = False
        # SOUTH-EAST
        pie.operator("mesh.mark_seam", text='Clear Seam').clear = True

        # Static face menu
        pie.separator()
        pie.separator()

        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8

        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y=1

        dropdown_menu.operator("uv.stitch")
        dropdown_menu.operator("uv.weld")
        dropdown_menu.operator("uv.remove_doubles")


registry = [
    SUBPIE_MT_uvUnwrap,
    IMAGE_PIE_MT_uvContext,
]


def register():

    register_hotkey(
        'wm.call_menu_pie',
        op_kwargs={'name': 'IMAGE_PIE_MT_uvContext'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        key_cat="UV Editor",
    )