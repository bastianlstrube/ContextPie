import bpy
from bpy.utils import register_class, unregister_class
import importlib

bl_info = {
    "name": "ContextPie",
    "version": (0, 9, 13),
    "blender": (5, 0, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}
bl_info_copy = bl_info.copy()

# --- Global State Flag ---
# We use this to track if the delayed registration actually finished.
_delayed_loaded = False

module_names = (
    "op_object_utils",
    "op_pie_wrappers",
    "blender_studio_utils",
    "hotkeys",
    "prefs",

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

modules = [
    __import__(__package__ + "." + submod, {}, {}, submod)
    for submod in module_names
]

# Import PieAppender separately
pie_appender_module = __import__(__package__ + ".PieAppender", {}, {}, "PieAppender")

def register_unregister_modules(modules: list, register: bool):
    """Recursively register or unregister modules."""
    register_func = register_class if register else unregister_class
    un = 'un' if not register else ''

    for m in modules:
        # Only reload during registration, NEVER during unregistration
        # (Reloading during unregister creates new class objects that don't match Blender's registry)
        if register:
            importlib.reload(m)

        if hasattr(m, 'registry'):
            for c in m.registry:
                try:
                    register_func(c)
                except Exception as e:
                    # Suppress errors if we are just trying to clean up
                    # and the class isn't there anyway.
                    if register:
                        print(f"Warning: Pie Menus failed to {un}register class: {c.__name__}")
                        print(e)

        if hasattr(m, 'modules'):
            register_unregister_modules(m.modules, register)

        if register and hasattr(m, 'register'):
            m.register()
        elif hasattr(m, 'unregister'):
            m.unregister()

def delayed_register():
    global _delayed_loaded

    # Safety Check: Is the addon still enabled?
    if __package__ not in bpy.context.preferences.addons:
        return

    # Register PieAppender
    try:
        register_unregister_modules([pie_appender_module], True)
        _delayed_loaded = True  # <--- Mark as success
    except Exception as e:
        print("ContextPie: Delayed registration failed:", e)


def register():
    # Reset flag on register
    global _delayed_loaded
    _delayed_loaded = False

    # Register standard modules
    register_unregister_modules(modules, True)

    bpy.app.timers.register(delayed_register, first_interval=0.5, persistent=True)

def unregister():
    global _delayed_loaded

    # 1. Kill the timer if it's still pending
    if bpy.app.timers.is_registered(delayed_register):
        bpy.app.timers.unregister(delayed_register)

    # 2. Only unregister PieAppender if we actually loaded it
    if _delayed_loaded:
        register_unregister_modules([pie_appender_module], False)
        _delayed_loaded = False

    # 3. Unregister the rest
    register_unregister_modules(reversed(modules), False)
