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
    "name": "UV Pivots Pie: 'Ctrl + Right Mouse'",
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


class IMAGE_PIE_MT_uvPivots(Menu):
    # label is displayed at the center of the pie menu.
    bl_label  = "UV Pivots"

    def draw(self, context):
        
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.separator()
        # EAST
        subPie = pie.operator("wm.call_menu_pie", text='Pivot...', icon = "RIGHTARROW_THIN")
        subPie.name = "IMAGE_MT_pivot_pie"
        # SOUTH
        pie.separator()
        #subPie = pie.operator("wm.call_menu_pie", text='Snap...', icon = "RIGHTARROW_THIN")
        #subPie.name = "SUBPIE_MT_snap"
        # NORTH
        subPie = pie.operator("wm.call_menu_pie", text='Proportional...', icon = "RIGHTARROW_THIN")
        subPie.name = "SUBPIE_MT_proportional_edt"
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


registry = [
    IMAGE_PIE_MT_uvPivots,
    ]

def register():

    register_hotkey(
        'wm.call_menu_pie',
        op_kwargs={'name': 'IMAGE_PIE_MT_uvPivots'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
        key_cat="UV Editor",
    )
