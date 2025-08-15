# NOTE: Keep in sync with CloudRig/operators/restore_deleted_hotkeys

import bpy
from .hotkeys import find_matching_km_and_kmi

class WINDOW_OT_restore_deleted_hotkeys_v3pm(bpy.types.Operator):
    bl_idname = "window.restore_deleted_hotkeys_v3pm"
    bl_description = "Restore any missing built-in or add-on hotkeys.\n(These should be disabled instead of being deleted.)\nThis operation cannot be undone!"
    # Undo flag is omitted, because this operation cannot be un-done.
    bl_options = {'REGISTER'}
    bl_label = "Restore Deleted Hotkeys"

    def execute(self, context):
        if bpy.app.version < (4, 5, 0):
            self.report({'ERROR'}, "This functionality requires Blender 4.5 or newer.")
            return {'CANCELLED'}
        num_restored = restore_deleted_keymap_items_global(context)
        self.report({'INFO'}, f"Restored {num_restored} deleted keymaps.")
        return {'FINISHED'}

def restore_deleted_keymap_items_global(context) -> int:
    """Deleting built-in or add-on KeyMapItems should never be done by users, as there's no way to recover them.
    Changing the operator name also shouldn't be done, since that makes it impossible to track modifications.
    Blender shouldn't even allow either of these things. You can disable instead of delete, and you can disable and add new entry instead of modifying idname.
    This function tries to bring them back, by restoring all KeyMaps to their default state, then re-applying any modifications that were there before
    (Except these deletions.)
    """

    keyconfigs = context.window_manager.keyconfigs
    user_kc = keyconfigs.user
    total_restored = 0
    for user_km in user_kc.keymaps:
        total_restored += restore_deleted_keymap_items(context, user_km)
    return total_restored

def restore_deleted_keymap_items(context, user_km) -> int:
    keyconfigs = context.window_manager.keyconfigs
    user_kc = keyconfigs.user
    default_kc = keyconfigs.default
    addon_kc = keyconfigs.addon

    # Step 1: Store modified and added KeyMapItems in a temp keymap.
    temp_km = user_kc.keymaps.new("temp_"+user_km.name)
    try:
        kmis_user_modified = []
        kmis_user_defined = []
        for user_kmi in user_km.keymap_items:
            if user_kmi.is_user_defined:
                temp_kmi = temp_km.keymap_items.new_from_item(user_kmi)
                kmis_user_defined.append(temp_kmi)
                continue
            if user_kmi.is_user_modified:
                temp_kmi = temp_km.keymap_items.new_from_item(user_kmi)
                # Find the original keymap in either the Blender default or Addon KeyConfigs. 
                # Not sure if this works with presets like Industry Compatible keymap, 
                # but I assume they change the contents of the "default" keyconfig, so it would work.
                default_km, default_kmi = find_matching_km_and_kmi(context, default_kc, user_km, user_kmi)
                if not default_kmi:
                    default_km, default_kmi = find_matching_km_and_kmi(context, addon_kc, user_km, user_kmi)
                kmis_user_modified.append(((default_km, default_kmi), (temp_km, temp_kmi)))

        # Step 2: Restore User KeyMap to default.
        num_kmis = len(user_km.keymap_items)
        user_km.restore_to_default()

        # Step 3: Restore modified and added KeyMapItems.
        for temp_def_kmi in kmis_user_defined:
            user_km.keymap_items.new_from_item(temp_def_kmi)

        for (default_km, default_kmi), (temp_km, temp_kmi) in kmis_user_modified:
            user_km, user_kmi = find_matching_km_and_kmi(context, user_kc, default_km, default_kmi)
            for key in ('active', 'alt', 'any', 'ctrl', 'hyper', 'key_modifier', 'map_type', 'oskey', 'shift', 'repeat', 'type', 'value'):
                setattr(user_kmi, key, getattr(temp_kmi, key))
            if temp_kmi.properties:
                for key in temp_kmi.properties.keys():
                    temp_value = getattr(temp_kmi.properties, key)
                    if hasattr(temp_value, 'keys'):
                        # Operator properties can be PropertyGroups, and this is the case for some node wrangler ops.
                        temp_propgroup = temp_value
                        real_propgroup = getattr(user_kmi.properties, key)
                        for pg_key in temp_propgroup.keys():
                            pg_val = getattr(temp_propgroup, pg_key)
                            real_propgroup[pg_key] = pg_val
                        continue
                    setattr(user_kmi.properties, key, temp_value)
    finally:
        # Nuke the temp keymap.
        user_kc.keymaps.remove(temp_km)

    return len(user_km.keymap_items) - num_kmis


if "bl_ext.blender_org.viewport_pie_menus" not in bpy.context.preferences.addons:
    registry = [WINDOW_OT_restore_deleted_hotkeys_v3pm]
else:
    registry = []