import bpy, json
from bpy.props import BoolProperty
from pathlib import Path
from . import __package__ as base_package
from . import get_addon_prefs

class PrefsFileSaveLoadMixin:
    """Mix-in class that can be used by any add-on to store their preferences in a file,
    so that they don't get lost when the add-on is disabled.
    To use it, copy this file to your add-on, and do this in your code:

    ```
    import bpy
    from .prefs_save_load import PrefsFileSaveLoadMixin, update_prefs_on_file

    class MyAddonPrefs(PrefsFileSaveLoadMixin, bpy.types.AddonPreferences):
        some_prop: bpy.props.IntProperty(update=update_prefs_on_file)

    def register():
        bpy.utils.register_class(MyAddonPrefs)
        MyAddonPrefs.register_autoload_from_file()

    def unregister():
        update_prefs_on_file()
    ```

    """

    use_auto_save: BoolProperty(
        name="Auto-Save Hotkeys",
        default=True,
        description="Whether hotkey settings for this add-on should be saved to disk automatically when the add-on is disabled or Blender shuts down (without crashing). Disable for troubleshooting issues with the hotkeys",
    )

    # List of property names to not write to disk.
    omit_from_disk: list[str] = []

    loading = False

    @staticmethod
    def register_autoload_from_file(delay=2.0):
        def timer_func(_scene=None):
            try:
                prefs = get_addon_prefs()
            except KeyError:
                # Add-on got un-registered in the meantime.
                return
            if prefs:
                prefs.load_and_apply_prefs_from_file()
            else:
                return 1.0
        bpy.app.timers.register(timer_func, first_interval=delay)

    def apply_prefs_from_dict_recursive(self, propgroup, data):
        for key, value in data.items():
            if not hasattr(propgroup, key):
                # Property got removed or renamed in the implementation.
                continue
            if type(value) == list:
                for elem in value:
                    collprop = getattr(propgroup, key)
                    entry = collprop.get(elem['name'])
                    if not entry:
                        entry = collprop.add()
                    self.apply_prefs_from_dict_recursive(entry, elem)
            elif type(value) == dict:
                self.apply_prefs_from_dict_recursive(getattr(propgroup, key), value)
            else:
                setattr(propgroup, key, value)

    def to_dict(self):
        return props_to_dict_recursive(self, skip=type(self).omit_from_disk)

    def save_prefs_to_file(self, _context=None):
        filepath = get_prefs_filepath()

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_and_apply_prefs_from_file(self):
        type(self).loading = True
        addon_data = load_prefs_from_file()
        self.apply_prefs_from_dict_recursive(self, addon_data)
        type(self).loading = False


def load_prefs_from_file() -> dict:
    filepath = get_prefs_filepath()
    if not filepath.exists():
        return {}

    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            print(f"Failed to load add-on preferences from file: {base_package}")


def get_prefs_filepath() -> Path:
    if "." in base_package:
        addon_name = base_package.split(".")[-1]
    else:
        addon_name = base_package
    return Path(bpy.utils.user_resource('CONFIG')) / Path(addon_name + ".json")


def update_prefs_on_file(self=None, context=None):
    prefs = get_addon_prefs(context)
    if prefs:
        if not type(prefs).loading:
            prefs.save_prefs_to_file()
    else:
        print("Couldn't save preferences because the class was already unregistered.")


def props_to_dict_recursive(propgroup: 'IDPropertyGroup', skip=[]) -> dict:
    """Recursively convert a PropertyGroup or AddonPreferences to a dictionary.
    Note that AddonPreferences don't support PointerProperties,
    so this function doesn't either."""
    from rna_prop_ui import IDPropertyGroup

    ret = {}

    for key in propgroup.bl_rna.properties.keys():
        if key in skip or key in ['rna_type', 'bl_idname']:
            continue
        value = getattr(propgroup, key)
        if isinstance(value, bpy.types.bpy_prop_collection):
            ret[key] = [props_to_dict_recursive(elem) for elem in value]
        elif type(value) == IDPropertyGroup or isinstance(value, bpy.types.PropertyGroup):
            ret[key] = props_to_dict_recursive(value)
        else:
            if hasattr(propgroup.bl_rna.properties[key], 'enum_items'):
                # Save enum values as string, not int.
                ret[key] = propgroup.bl_rna.properties[key].enum_items[value].identifier
            else:
                ret[key] = value
    return ret
