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

# Blender imports
if "bpy" in locals():
    import importlib

    importlib.reload(PIE_context)
    importlib.reload(PIE_mode)
    importlib.reload(edgeloop)
    importlib.reload(PIE_uvcontext)
    importlib.reload(PIE_uvmode)
    importlib.reload(PIE_spacebar)
    importlib.reload(PIE_pivots)
else:
    from . import (PIE_context, PIE_mode , PIE_uvcontext, PIE_uvmode, PIE_spacebar, PIE_pivots)
import bpy


modules = (PIE_context, PIE_mode , PIE_uvcontext, PIE_uvmode, PIE_spacebar, PIE_pivots)

addon_keymaps = []

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()

if __name__ == "__main__":
    register()
