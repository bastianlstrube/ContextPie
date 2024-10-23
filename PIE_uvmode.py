# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Context Pie: Mode Selection 'Right Mouse'",
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


class SUBPIE_MT_uvSelect(Menu):
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

class SUBPIE_MT_uvSticky(Menu):
    bl_label = "Sticky"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        o = pie.operator('wm.context_set_string', text="Location", icon="STICKY_UVS_LOC")
        o.data_path = 'tool_settings.uv_sticky_select_mode'
        o.value = 'SHARED_LOCATION'
        # EAST
        pie.separator()
        # SOUTH
        o = pie.operator('wm.context_set_string', text="Vertex", icon="STICKY_UVS_VERT")
        o.data_path = 'tool_settings.uv_sticky_select_mode'
        o.value = 'SHARED_VERTEX'
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        o = pie.operator('wm.context_set_string', text="Disabled", icon="STICKY_UVS_DISABLE")
        o.data_path = 'tool_settings.uv_sticky_select_mode'
        o.value = 'DISABLED'
        # SOUTH-EAST
        pie.separator()

class SUBPIE_MT_uvTools(Menu):
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
    bl_label  = "Switch UV Mode"

    def draw(self, context):
        
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        obj = context.object
        scn = context.scene

        if not context.tool_settings.use_uv_select_sync:
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
            subPie.name = "SUBPIE_MT_uvTools" 
            # NORTH-EAST
            o = pie.operator('wm.context_set_string', text="Islands", icon="UV_ISLANDSEL")
            o.data_path = 'tool_settings.uv_select_mode'
            o.value = 'ISLAND'
            # SOUTH-WEST
            subPie = pie.operator("wm.call_menu_pie", text='Sticky...')
            subPie.name = "SUBPIE_MT_uvSticky"  
            # SOUTH-EAST
            subPie = pie.operator("wm.call_menu_pie", text='Select...')
            subPie.name = "SUBPIE_MT_uvSelect" 
        else:
            # WEST
            o = pie.operator('wm.context_toggle', text="Sync Selection", icon="UV_SYNC_SELECT")
            o.data_path = 'tool_settings.use_uv_select_sync'
            # EAST
            pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
            # SOUTH
            pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
            # NORTH
            pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'
            # NORTH-WEST
            subPie = pie.operator("wm.call_menu_pie", text='Tools...')
            subPie.name = "SUBPIE_MT_uvTools" 
            # NORTH-EAST
            o = pie.operator('wm.context_set_string', text="Islands", icon="UV_ISLANDSEL")
            o.data_path = 'tool_settings.uv_select_mode'
            o.value = 'ISLAND'
            # SOUTH-WEST
            subPie = pie.operator("wm.call_menu_pie", text='Sticky...')
            subPie.name = "SUBPIE_MT_uvSticky"  
            # SOUTH-EAST
            subPie = pie.operator("wm.call_menu_pie", text='Select...')
            subPie.name = "SUBPIE_MT_uvSelect" 

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


registry = [
    SUBPIE_MT_uvSelect,
    SUBPIE_MT_uvSticky,
    SUBPIE_MT_uvTools,
    IMAGE_PIE_MT_uvMode]

def register():

    register_hotkey(
        'wm.call_menu_pie_drag_only_cpie',
        op_kwargs={'name': 'IMAGE_PIE_MT_uvMode'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        key_cat="UV Editor",
    )