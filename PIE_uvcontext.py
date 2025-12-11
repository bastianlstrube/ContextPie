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

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

# Sub Sub Pie Menu for UV Unwrap
class SUBPIE_MT_uvPrimUnwrap(Menu):
    bl_label = "Unwrap"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.separator()
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("uv.cylinder_project")
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("uv.sphere_project")
        # SOUTH-EAST
        pie.operator("uv.cube_project")

# Sub Pie Menu for UV Unwrap
class SUBPIE_MT_uvUnwrap(Menu):
    bl_label = "Unwrap"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # Getting the current UV Editor Space
        uv_editor_space = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                # Get the active space of this area
                # (The Image Editor and UV Editor share the same space type)
                space = area.spaces.active
                if space:
                    uv_editor_space = space
                    break # Stop searching once we find one

        # WEST
        pie.operator("uv.smart_project")
        # EAST
        pie.operator("uv.follow_active_quads")
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Primitive Unwrap...').name = "SUBPIE_MT_uvPrimUnwrap"
        # NORTH
        if bpy.app.version >= (4,3,0):
            pie.operator("uv.unwrap", text='Minimum Stretch').method = 'MINIMUM_STRETCH'
        else:
            pie.operator("uv.unwrap", text='Angle Based').method = 'ANGLE_BASED'
        # NORTH-WEST
        if bpy.app.version >= (4,3,0):
            pie.operator("uv.unwrap", text='Angle Based').method = 'ANGLE_BASED'
        else:
            pie.separator()
        # NORTH-EAST
        pie.operator("uv.unwrap", text='Conformal').method = 'CONFORMAL'
        # SOUTH-WEST
        pie.operator("uv.lightmap_pack")
        # SOUTH-EAST
        if uv_editor_space:
            # access .uv_editor to get to the specific Live Unwrap settings
            pie.prop(uv_editor_space.uv_editor, "use_live_unwrap", text="Live Unwrap")
        else:
            pie.separator()

# Reference context menu: IMAGE_MT_uvs_context_menu
class IMAGE_PIE_MT_uvContext(Menu):
    bl_idname = "PIE_MT_context_uv"
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
        pie.operator("uv.mark_seam", text='Mark Seam').clear = False
        # SOUTH-EAST
        pie.operator("uv.mark_seam", text='Clear Seam').clear = True

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
    SUBPIE_MT_uvPrimUnwrap,
]


def register():

    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=IMAGE_PIE_MT_uvContext.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="UV Editor",
    )
