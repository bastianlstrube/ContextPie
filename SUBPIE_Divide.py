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

import os
from pathlib import Path

import bpy
from bpy.types import Menu
from .hotkeys import register_hotkey

from bpy.app.translations import contexts as i18n_contexts

# Sub Pie for mesh face divisions
class SUBPIE_MT_divideFaces(Menu):
    bl_label = "Divide"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
        # EAST
        pie.operator("mesh.bevel", text='Bevel')
        # SOUTH
        pie.separator()
        # NORTH
        pie.operator("mesh.poke")
        

        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("mesh.subdivide", text='Subdivide')
        # SOUTH-WEST
        pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
        # SOUTH-EAST
        pie.separator()

        ''' # Static face menu
            pie.separator()
            pie.separator()
            dropdown = pie.column()
            gap = dropdown.column()
            gap.separator()
            gap.scale_y = 8
            dropdown_menu = dropdown.box().column()
            dropdown_menu.scale_y=1
            dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
            dropdown_menu.operator("mesh.bisect")
            dropdown_menu.operator("mesh.flip_normals")
            dropdown_menu.operator("mesh.rip_move", text = "Extract Faces")'''

# Sub Pie for mesh edge divisions
class SUBPIE_MT_divideEdges(Menu):
    bl_label = "Divide"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
        # EAST
        pie.operator("mesh.bevel", text='Bevel')
        # SOUTH
        pie.separator()
        # NORTH
        pie.operator("mesh.poke")
        

        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("mesh.subdivide", text='Subdivide')
        # SOUTH-WEST
        pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
        # SOUTH-EAST
        pie.separator()

        '''     # Static edge menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
                dropdown_menu.operator("transform.edge_crease", text = "Crease Tool")
                dropdown_menu.operator("mesh.mark_sharp", text = "Mark Sharp").clear = False
                dropdown_menu.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
                dropdown_menu.operator("mesh.subdivide", text = "Add Division To Edge")
                dropdown_menu.operator("mesh.edge_split")
                dropdown_menu.operator("mesh.edge_rotate").use_ccw=False
                dropdown_menu.operator("mesh.edge_rotate").use_ccw=True
                dropdown_menu.operator("mesh.rip_move", text = "Detach Components")
                subPie = dropdown_menu.operator("wm.call_menu_pie", text='Separate')
                subPie.name = "SUBPIE_MT_separate"
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Circularize Component")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Edit Edge Flow")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Offset Edge Loop Tool")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Insert Edgeloop Tool")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Connect Components")'''

# Sub Pie for mesh Vertice divisions
class SUBPIE_MT_divideVertices(Menu):
    bl_label = "Divide"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
        # EAST
        pie.operator("mesh.bevel", text='Bevel')
        # SOUTH
        pie.separator()
        # NORTH
        pie.operator("mesh.poke")
        

        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("mesh.bevel", text='Bevel')
        # SOUTH-WEST
        pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
        # SOUTH-EAST
        pie.separator()

        '''                # Static Vert menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
                dropdown_menu.operator("mesh.bisect", text = "Bisect")
                dropdown_menu.operator("transform.edge_crease", text = "Crease Tool")
                separatePie = dropdown_menu.operator("wm.call_menu_pie", text='Separate...').name = "SUBPIE_MT_separate"
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Crease Tool", icon="ops.generic.select")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Connect Components")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Circularize Component")'''