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
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}

from bpy.utils import register_class, unregister_class
import importlib

module_names = (
    "hotkeys",
    "prefs",

    "PIE_context",
    "PIE_mode",
    "PIE_pivots",
    "PIE_uvcontext",
    "PIE_uvmode",
    "PIE_uvpivots",
    "PIE_spacebar",

    "SUBPIE_proportional_menu",
    "SUBPIE_snap_menu",
)


modules = [
    __import__(__package__ + "." + submod, {}, {}, submod)
    for submod in module_names
]


def register_unregister_modules(modules: list, register: bool):
    """Recursively register or unregister modules by looking for either
    un/register() functions or lists named `registry` which should be a list of
    registerable classes.
    """
    register_func = register_class if register else unregister_class
    un = 'un' if not register else ''

    for m in modules:
        if register:
            importlib.reload(m)
        if hasattr(m, 'registry'):
            for c in m.registry:
                try:
                    register_func(c)
                except Exception as e:
                    print(
                        f"Warning: Pie Menus failed to {un}register class: {c.__name__}"
                    )
                    print(e)

        if hasattr(m, 'modules'):
            register_unregister_modules(m.modules, register)

        if register and hasattr(m, 'register'):
            m.register()
        elif hasattr(m, 'unregister'):
            m.unregister()


def register():
    register_unregister_modules(modules, True)


def unregister():
    register_unregister_modules(reversed(modules), False)
