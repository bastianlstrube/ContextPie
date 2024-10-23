# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from .hotkeys import register_hotkey

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
class SUBPIE_MT_views(Menu):

    bl_label = "Views"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator_enum("VIEW3D_OT_view_axis", "type")
        pie.operator("view3d.localview", text="isolate select")
        pie.operator("VIEW3D_OT_view_persportho", text="Persp/Ortho", icon='RESTRICT_VIEW_OFF')
        pie.operator("view3d.view_camera", text="Camera")

# Pie Master Mode 
class VIEW3D_PIE_MT_spaceMain(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Options"
    
    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie
        pie.operator("wm.toolbar", text = "handy tools", icon="TOOL_SETTINGS")    #W
        pie.operator("object.modifier_add", text = "modifier", icon="MODIFIER_ON") #E
        pie.operator("wm.call_menu_pie", text="views", icon='VIEW_CAMERA').name = "SUBPIE_MT_views" #S
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


registry = [
    VIEW3D_PIE_MT_spaceMain, 
    SUBPIE_MT_views,

]

def register():
    register_hotkey(
        'wm.call_menu_pie',
        op_kwargs={'name': 'VIEW3D_PIE_MT_spaceMain'},
        hotkey_kwargs={'type': "SPACE", 'value': "PRESS", 'ctrl': True},
        key_cat="3D View",
    )

