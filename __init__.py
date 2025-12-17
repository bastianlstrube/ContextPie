import bpy
from bpy.utils import register_class, unregister_class
import importlib

_VPM_AGENT_IMMEDIATE_REGISTER_DONE = locals().get("_VPM_AGENT_IMMEDIATE_REGISTER_DONE", False)

bl_info = {
    "name": "ContextPie",
    "version": (0, 9, 21),
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
                except (AttributeError, RuntimeError, TypeError, ValueError) as e:
                    print(f"Warning: Pie Menus failed to {un}register class: {c.__name__}")
                    print(e)

        if hasattr(m, 'modules'):
            register_unregister_modules(m.modules, register)

        if register and hasattr(m, 'register'):
            m.register()
        elif hasattr(m, 'unregister'):
            m.unregister()

def delayed_register():
    register_unregister_modules(modules, True)


def register():
    """
    We prefer an *immediate* register during startup, because other add-ons may touch
    keyconfig initialization very early, and Blender's keymap diff application appears
    sensitive to timing.
    If immediate registration fails (e.g. missing WM in edge cases), fall back to the
    legacy timer-based delayed registration.
    """
    global _VPM_AGENT_IMMEDIATE_REGISTER_DONE
    if not _VPM_AGENT_IMMEDIATE_REGISTER_DONE:
        try:
            register_unregister_modules(modules, True)
            _VPM_AGENT_IMMEDIATE_REGISTER_DONE = True
            return
        except Exception as e:
            # Keep behavior unchanged (fallback to timer), but avoid raising during registration.
            pass
    # NOTE: persistent=True must be set, otherwise this doesn't work when opening
    # a .blend file directly from a file browser.
    bpy.app.timers.register(delayed_register, first_interval=0.0, persistent=True)

def unregister():
    register_unregister_modules(reversed(modules), False)
