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
    "name": "UV Mode Pie: 'Right Mouse'",
    "description": "UV Mode Selection Pie Menu",
    "author": "Bastian L Strube, Frederik Storm",
    "version": (0, 1, 2),
    "blender": (2, 80, 0),
    "location": "UV Editor",
    "category": "Pie Menu"}

import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)
from bpy.app.translations import contexts as i18n_contexts

class SUBPIE_uvSelect(Menu):
    bl_label = "Select"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()
        # EAST
        pie.operator("uv.select_pinned", text="Pinned") 
        # SOUTH
        pie.operator("uv.select_overlap", text="Overlap")
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.operator("uv.select_linked", text="Island")

class SUBPIE_uvSticky(Menu):
    bl_label = "Sticky"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        o = pie.operator('wm.context_set_string', text="Location", icon="STICKY_UVS_LOC")
        o.data_path = 'space_data.uv_editor.sticky_select_mode'
        o.value = 'SHARED_LOCATION'
        # EAST
        pie.separator()
        # SOUTH
        o = pie.operator('wm.context_set_string', text="Vertex", icon="STICKY_UVS_VERT")
        o.data_path = 'space_data.uv_editor.sticky_select_mode'
        o.value = 'SHARED_VERTEX'
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        o = pie.operator('wm.context_set_string', text="Disabled", icon="STICKY_UVS_DISABLE")
        o.data_path = 'space_data.uv_editor.sticky_select_mode'
        o.value = 'DISABLED'
        # SOUTH-EAST
        pie.separator()

class SUBPIE_uvTools(Menu):
    bl_label = "UV Tools"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        o = pie.operator('wm.tool_set_by_id', text="Pinch")
        o.name = 'builtin_brush.Pinch'
        # EAST
        pie.separator()
        # SOUTH
        pie.separator()
        # NORTH
        o = pie.operator('wm.tool_set_by_id', text="Grab")
        o.name = 'builtin_brush.Grab'
        # NORTH-WEST
        o = pie.operator('wm.tool_set_by_id', text="Relax")
        o.name = 'builtin_brush.Relax'
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()

class IMAGE_PIE_MT_uvMode(Menu):
    # label is displayed at the center of the pie menu.
    bl_label  = "Switch UV Mode Pie"

    def draw(self, context):
        
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        obj = context.object
        scn = context.scene

        # WEST
        o = pie.operator('wm.context_toggle', text="Sync Selection", icon="UV_SYNC_SELECT")
        o.data_path = 'tool_settings.use_uv_select_sync'
        # EAST
        o = pie.operator('wm.context_set_string', text="Vertex", icon="UV_VERTEXSEL")
        o.data_path = 'tool_settings.uv_select_mode'
        o.value = 'VERTEX'
        # SOUTH
        o = pie.operator('wm.context_set_string', text="Face", icon="UV_FACESEL")
        o.data_path = 'tool_settings.uv_select_mode'
        o.value = 'FACE'
        # NORTH
        o = pie.operator('wm.context_set_string', text="Edge", icon="UV_EDGESEL")
        o.data_path = 'tool_settings.uv_select_mode'
        o.value = 'EDGE'
        # NORTH-WEST
        subPie = pie.operator("wm.call_menu_pie", text='Tools...')
        subPie.name = "SUBPIE_uvTools" 
        # NORTH-EAST
        o = pie.operator('wm.context_set_string', text="Islands", icon="UV_ISLANDSEL")
        o.data_path = 'tool_settings.uv_select_mode'
        o.value = 'ISLAND'
        # SOUTH-WEST
        subPie = pie.operator("wm.call_menu_pie", text='Sticky...')
        subPie.name = "SUBPIE_uvSticky"  
        # SOUTH-EAST
        subPie = pie.operator("wm.call_menu_pie", text='Select...')
        subPie.name = "SUBPIE_uvSelect"  

        # Static menu
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y=1
        dropdown_menu.scale_x=1.2
        
        dropdown_menu.menu("IMAGE_MT_uvs", text="UV menu", icon="COLLAPSEMENU")


classes = [
    SUBPIE_uvSelect,
    SUBPIE_uvSticky,
    SUBPIE_uvTools,
    IMAGE_PIE_MT_uvMode]

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='UV Editor')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "IMAGE_PIE_MT_uvMode"
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