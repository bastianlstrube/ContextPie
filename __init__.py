# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "ContextPie",
    "version": (0, 9, 13),
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}
bl_info_copy = bl_info.copy()

import bpy
from bpy.utils import register_class, unregister_class
import importlib

module_names = (
    "op_object_utils",
    "op_pie_wrappers",
    "blender_studio_utils",
    "hotkeys",
    "prefs",
    "PieAppender",

    "PIE_context",
    "PIE_mode",
    "PIE_pivots",
    "PIE_uvcontext",
    "PIE_uvmode",
    "PIE_uvpivots",

    "SUBPIE_proportional_menu",
    "SUBPIE_snap_menu",
    "SUBPIE_MeshAlign",
    "SUBPIE_set_origin",
)

'''if not "bl_ext.blender_org.copy_attributes_menu" in bpy.context.preferences.addons:
    module_names.append("CopyOps")
'''

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

def delayed_register(_scene=None):
    # Register whole add-on with a slight delay,
    # to make sure Keymap data we need already exists on Blender launch.
    # Otherwise, keyconfigs.user.keymaps is an empty list, we can't find fallback ops.
    register_unregister_modules(modules, True)

def register():
    # NOTE: persistent=True must be set, otherwise this doesn't work when opening a .blend file directly from a file browser.
    bpy.app.timers.register(delayed_register, first_interval=0.5, persistent=True)

def unregister():
    # save add-on prefs to file before unregistering.
    from .blender_studio_utils.prefs import get_addon_prefs, update_prefs_on_file
    addon_prefs = get_addon_prefs()
    if addon_prefs:
        if bpy.context.preferences.use_preferences_save:
            update_prefs_on_file()
        register_unregister_modules(reversed(modules), False)
