# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Pivot Pie: 'Ctrl + Right Mouse'",
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}

from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

'''
# Checking if addons exists
addon_list = [
    'EdgeFlow',
]
addon_dict = []
for addon in addon_list:
    addon_dict[addon] = addon_utils.check(addon)


if addon_dict['EdgeFlow']:
    class VIEW3D_MT_edit_mesh_set_flow_pie(Menu):
        bl_label = "EdgeFlow"
        def draw(self, context):
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            
            pie.operator_enum("VIEW3D_MT_edit_mesh_set_flow.items")
'''

# Context Sensitive Add-ons Pie Menu
class VIEW3D_PIE_MT_pivots(Menu):
    bl_idname = "PIE_MT_context_pivots"
    bl_label    = "Pivots Pie"

    def draw(self, context):

        if context.mode in ('EDIT_MESH', 'EDIT_CURVE', 'EDIT_LATTICE', 'EDIT_ARMATURE'):

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            subPie = pie.operator("wm.call_menu_pie", text='Orientation...', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_orientations_pie"
            # EAST
            subPie = pie.operator("wm.call_menu_pie", text='Pivot...', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_pivot_pie"
            # SOUTH
            subPie = pie.operator("wm.call_menu_pie", text='Snap...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_snap"
            # NORTH
            subPie = pie.operator("wm.call_menu_pie", text='Proportional...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_proportional_edt"
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            subPie = pie.operator("wm.call_menu_pie", text='Set Origin...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_set_origin"
            # SOUTH-WEST
            subPie = pie.operator("wm.call_menu_pie", text='Align...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_mesh_align"
            # SOUTH-EAST
            pie.separator()

        if context.mode == 'OBJECT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object
            sel = context.selected_objects

            #if obj is not None and sel:
                # WEST
            subPie = pie.operator("wm.call_menu_pie", text='Orientation...', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_orientations_pie"
            # EAST
            subPie = pie.operator("wm.call_menu_pie", text='Pivot...', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_pivot_pie"
            # SOUTH
            subPie = pie.operator("wm.call_menu_pie", text='Snap...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_snap"
            # NORTH
            subPie = pie.operator("wm.call_menu_pie", text='Proportional...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_proportional_obj"
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            subPie = pie.operator("wm.call_menu_pie", text='Set Origin...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_set_origin"
            # SOUTH-WEST
            pie.separator()
            # SOUTH-EAST
            pie.separator()

            '''else:
                # WEST
                subPie = pie.operator("wm.call_menu_pie", text='Orientation', icon = "RIGHTARROW_THIN")
                subPie.name = "VIEW3D_MT_orientations_pie"
                # EAST
                subPie = pie.operator("wm.call_menu_pie", text='Pivot', icon = "RIGHTARROW_THIN")
                subPie.name = "VIEW3D_MT_pivot_pie"
                # SOUTH
                subPie = pie.operator("wm.call_menu_pie", text='Snap...', icon = "RIGHTARROW_THIN")
                subPie.name = "SUBPIE_MT_snap"
                # NORTH
                subPie = pie.operator("wm.call_menu_pie", text='Proportional...', icon = "RIGHTARROW_THIN")
                subPie.name = "SUBPIE_MT_proportional_obj"
                # NORTH-WEST
                pie.separator()
                # NORTH-EAST
                pie.separator()
                # SOUTH-WEST
                pie.separator()
                # SOUTH-EAST
                pie.separator()'''


        # Straight from Blenders Pie Addon Sculpt 'W' Menu
        if context.mode == 'SCULPT':

            #global brush_icons
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.separator()
            # EAST
            pie.separator()
            # SOUTH
            pie.separator()
            # NORTH
            pie.separator()
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.separator()
            # SOUTH-WEST
            pie.separator()
            # SOUTH-EAST
            pie.separator()

        if context.mode == 'POSE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object

            # WEST
            subPie = pie.operator("wm.call_menu_pie", text='Orientation...', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_orientations_pie"
            # EAST
            subPie = pie.operator("wm.call_menu_pie", text='Pivot...', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_pivot_pie"
            # SOUTH
            subPie = pie.operator("wm.call_menu_pie", text='Snap...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_snap"
            # NORTH
            subPie = pie.operator("wm.call_menu_pie", text='Proportional...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_proportional_obj"
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.separator()
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

"""
EMPTY PIE MENU

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()
        # EAST
        pie.separator()
        # SOUTH
        pie.separator()
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()

        # Static non pie menu
        pie.separator()

"""
