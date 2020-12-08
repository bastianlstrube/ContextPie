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

bl_info = {
    "name": "General Pie: 'Spacebar'",
    "description": "General Functionality Pie Menu",
    "author": "Bastian L Strube, Frederik Storm",
    "blender": (2, 80, 0),
    "location": "3D View",
    "category": "Interface"}

import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)

# spawn an edit mode selection pie (run while object is in edit mode to get a valid output)
'''
# adding a "parenting" sub menues
class ParentingSubMenu(bpy.types.Menu):
    bl_label = "parent"
    bl_idname = "Static_Sub_Menu_Parenting"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.parent_set", text = "parent")
        layout.operator("object.parent_clear", text = "un-parent")
'''
# Sub Pie View Mode 
class VIEW3D_PIE_views(Menu):
    bl_label = "Views"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator_enum("VIEW3D_OT_view_axis", "type")
        pie.operator("view3d.localview", text="isolate select")
        pie.operator("VIEW3D_OT_view_persportho", text="Persp/Ortho", icon='RESTRICT_VIEW_OFF')
        pie.operator("view3d.view_camera", text="Camera")

# Pie Master Mode 
class VIEW3D_PIE_MT_spaceMaster(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = ""
    
    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie
        pie.operator("wm.toolbar", text = "handy tools", icon="TOOL_SETTINGS")    #W
        pie.operator("object.modifier_add", text = "modifier", icon="MODIFIER_ON") #E
        pie.operator("wm.call_menu_pie", text="views", icon='VIEW_CAMERA').name = "VIEW3D_PIE_views" #S
        pie.operator("wm.search_menu", text = "search", icon="VIEWZOOM") #N
        pie.operator("mesh.select_less", text = "shrink selection", icon="REMOVE") #NE
        pie.operator("mesh.select_more", text = "grow selection", icon="ADD")   #NW
        pie.menu("VIEW3D_MT_make_links", text = "link data", icon="LINKED")  #SE
        pie.menu("VIEW3D_MT_add", text = "add object", icon="MESH_MONKEY")  #SW
        
        #Static non pie menu 01
        #pie.separator()
        #pie.separator()
        #dropdown = pie.column()
        #gap = dropdown.column()
        #gap.separator()
        #gap.scale_y = 7
        #dropdown_menu = dropdown.box().column()
        #dropdown_menu.scale_y=1.3
        #dropdown_menu.operator("wm.toolbar", text = "toolbar")
        #dropdown_menu.menu("Static_Sub_Menu_Parenting")
        #dropdown_menu.menu("VIEW3D_MT_object_apply", text = "freeze transform")
        #dropdown_menu.operator("mesh.separate", text = "seperate")
        #dropdown_menu.operator("object.join", text = "join")


classes = [
    VIEW3D_PIE_MT_spaceMaster, 
    VIEW3D_PIE_views,
]

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'SPACE', 'PRESS')
        kmi.properties.name = "VIEW3D_PIE_MT_spaceMaster"
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

    bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_spaceMain")
  
