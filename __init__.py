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
    "name": "Context Pie",
    "blender": (4, 0, 0),
    "category": "Interface",
    "description": "Context Sensitive Pie Menu, following an ancient Mayan pie recipe",
    "author": "Bastian L Strube, Frederik Storm  + liberal lendings from Official Blender Menus",
    "version": (0, 8, 4, 0),
    "location": "View3D (Object, Mesh, Curve), UV Editor",
}

# Blender imports
modules = (PIE_context, PIE_mode , PIE_uvcontext, PIE_uvmode, PIE_spacebar, PIE_pivots)
if "bpy" in locals():
    import importlib

    for module in modules:
        importlib.reload(module)
else:
    from . import modules
import bpy


addon_keymaps = []

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()

if __name__ == "__main__":
    register()
