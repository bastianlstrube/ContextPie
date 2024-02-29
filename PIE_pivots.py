# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import bpy
import addon_utils
from bpy.types import (
    Header,
    Menu,
    Panel,
)
from bpy.app.translations import contexts as i18n_contexts

'''
# Checking if addons exists
addon_list = [
    'EdgeFlow',
]
addon_dict = []
for addon in addon_list:
    addon_dict[addon] = addon_utils.enable(addon)


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
    bl_label    = "Pivots & Addons Pie"

    def draw(self, context):

        if context.mode == 'EDIT_MESH':

            def count_selected_items_for_objects_in_mode():
                selected_verts_len = 0
                selected_edges_len = 0
                selected_faces_len = 0
                for ob in context.objects_in_mode_unique_data:
                    v, e, f = ob.data.count_selected_items()
                    selected_verts_len += v
                    selected_edges_len += e
                    selected_faces_len += f
                return (selected_verts_len, selected_edges_len, selected_faces_len)

            is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
            selected_verts_len, selected_edges_len, selected_faces_len = count_selected_items_for_objects_in_mode()

            del count_selected_items_for_objects_in_mode

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            subPie = pie.operator("wm.call_menu_pie", text='Orientation', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_orientations_pie"
            # EAST
            subPie = pie.operator("wm.call_menu_pie", text='Pivot', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_pivot_pie"
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

            '''
            if is_vert_mode:
                
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
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                gap.separator()

            elif is_edge_mode:

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
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                gap.separator()

            elif is_face_mode:

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
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                gap.separator()
            '''
        if context.mode == 'EDIT_CURVE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            subPie = pie.operator("wm.call_menu_pie", text='Orientation', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_orientations_pie"
            # EAST
            subPie = pie.operator("wm.call_menu_pie", text='Pivot', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_pivot_pie"
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

        if context.mode == 'OBJECT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object
            sel = context.selected_objects

            if obj is not None and sel:
                # WEST
                subPie = pie.operator("wm.call_menu_pie", text='Orientation', icon = "RIGHTARROW_THIN")
                subPie.name = "VIEW3D_MT_orientations_pie"
                # EAST
                subPie = pie.operator("wm.call_menu_pie", text='Pivot', icon = "RIGHTARROW_THIN")
                subPie.name = "VIEW3D_MT_pivot_pie"
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

            else:
                # WEST
                subPie = pie.operator("wm.call_menu_pie", text='Orientation', icon = "RIGHTARROW_THIN")
                subPie.name = "VIEW3D_MT_orientations_pie"
                # EAST
                subPie = pie.operator("wm.call_menu_pie", text='Pivot', icon = "RIGHTARROW_THIN")
                subPie.name = "VIEW3D_MT_pivot_pie"
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
            subPie = pie.operator("wm.call_menu_pie", text='Orientation', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_orientations_pie"
            # EAST
            subPie = pie.operator("wm.call_menu_pie", text='Pivot', icon = "RIGHTARROW_THIN")
            subPie.name = "VIEW3D_MT_pivot_pie"
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


classes = [
    VIEW3D_PIE_MT_pivots,
]

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    #From this forum post: https://devtalk.blender.org/t/addon-shortcuts/2410/7
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', ctrl=True)
        kmi.properties.name = "VIEW3D_PIE_MT_pivots"
        addon_keymaps.append((km, kmi))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()


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
