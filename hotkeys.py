# SPDX-FileCopyrightText: 2016-2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy, json, hashlib
from . import __package__ as base_package

PIE_ADDON_KEYMAPS = {}

def register_hotkey(
    bl_idname, hotkey_kwargs, *, key_cat='Window', op_kwargs={}
):
    """This function inserts a 'hash' into the created KeyMapItems' properties,
    so they can be compared to each other, and duplicates can be avoided."""

    global PIE_ADDON_KEYMAPS
    wm = bpy.context.window_manager

    space_type = wm.keyconfigs.default.keymaps[key_cat].space_type

    addon_keyconfig = wm.keyconfigs.addon
    if not addon_keyconfig:
        # This happens when running Blender in background mode.
        return

    # We limit the hash to a few digits, otherwise it errors when trying to store it.
    kmi_string = json.dumps([bl_idname, hotkey_kwargs, key_cat, space_type, op_kwargs], sort_keys=True).encode("utf-8")
    kmi_hash = hashlib.md5(kmi_string).hexdigest()

    # If it already exists, don't create it again.
    for existing_kmi_hash, existing_kmi_tup in PIE_ADDON_KEYMAPS.items():
        existing_addon_kc, existing_addon_km, existing_kmi = existing_kmi_tup
        if kmi_hash == existing_kmi_hash:
            # The hash we just calculated matches one that is in storage.
            user_kc = wm.keyconfigs.user
            user_km = user_kc.keymaps.get(existing_addon_km.name)
            # NOTE: It's possible on Reload Scripts that some KeyMapItems remain in storage,
            # but are unregistered by Blender for no reason.
            # I noticed this particularly in the Weight Paint keymap.
            # So it's not enough to check if a KMI with a hash is in storage, we also need to check if a corresponding user KMI exists.
            user_kmi = find_kmi_in_km_by_hash(user_km, kmi_hash)
            if user_kmi:
                # print("Hotkey already exists, skipping: ", existing_kmi.name, existing_kmi.to_string(), kmi_hash)
                return

    addon_keymaps = addon_keyconfig.keymaps
    addon_km = addon_keymaps.get(key_cat)
    if not addon_km:
        addon_km = addon_keymaps.new(name=key_cat, space_type=space_type)

    addon_kmi = addon_km.keymap_items.new(bl_idname, **hotkey_kwargs)
    for key in op_kwargs:
        value = op_kwargs[key]
        setattr(addon_kmi.properties, key, value)

    addon_kmi.properties['hash'] = kmi_hash

    PIE_ADDON_KEYMAPS[kmi_hash] = (
        addon_keyconfig,
        addon_km,
        addon_kmi,
    )


def draw_hotkey_list(layout, context):
    user_kc = context.window_manager.keyconfigs.user

    keymap_data = list(PIE_ADDON_KEYMAPS.items())
    keymap_data = sorted(keymap_data, key=lambda tup: tup[1][2].name)

    prev_kmi = None
    for kmi_hash, kmi_tup in keymap_data:
        addon_kc, addon_km, addon_kmi = kmi_tup

        user_km = user_kc.keymaps.get(addon_km.name)
        if not user_km:
            # This really shouldn't happen.
            continue
        user_kmi = find_kmi_in_km_by_hash(user_km, kmi_hash)

        col = layout.column()
        col.context_pointer_set("keymap", user_km)
        if user_kmi and prev_kmi and prev_kmi.properties.name != user_kmi.properties.name:
            col.separator()
        user_row = col.row()

        if False:
            # Debug code: Draw add-on and user KeyMapItems side-by-side.
            split = user_row.split(factor=0.5)
            addon_row = split.row()
            user_row = split.row()
            draw_kmi(addon_km, addon_kmi, addon_row)
        if not user_kmi:
            # This should only happen for one frame during Reload Scripts.
            print(
                base_package + "Can't find this hotkey to draw: ",
                addon_kmi.name,
                addon_kmi.to_string(),
            )
            continue

        draw_kmi(user_km, user_kmi, user_row)
        prev_kmi = user_kmi

def draw_kmi(km, kmi, layout):
    """A simplified version of draw_kmi from rna_keymap_ui.py."""

    col = layout.column()

    split = col.split(factor=0.7)

    # header bar
    row = split.row(align=True)
    row.prop(kmi, "active", text="", emboss=False)
    km_name = km.name
    if km_name == 'Armature':
        km_name = 'Armature Edit'
    bpy_type = getattr(bpy.types, kmi.properties.name)
    row.label(text=f'{km_name} - {bpy_type.bl_label}')

    row = split.row(align=True)
    sub = row.row(align=True)
    sub.enabled = kmi.active
    sub.prop(kmi, "type", text="", full_event=True)

    if kmi.is_user_modified:
        row.operator(
            "preferences.keyitem_restore", text="", icon='LOOP_BACK'
        ).item_id = kmi.id

def print_kmi(kmi):
    idname = kmi.idname
    keys = kmi.to_string()
    props = str(list(kmi.properties.items()))
    print(idname, props, keys)

def find_kmi_in_km_by_hash(keymap, kmi_hash):
    """There's no solid way to match modified user keymap items to their
    add-on equivalent, which is necessary to draw them in the UI reliably.

    To remedy this, we store a hash in the KeyMapItem's properties.

    This function lets us find a KeyMapItem with a stored hash in a KeyMap.
    Eg., we can pass a User KeyMap and an Addon KeyMapItem's hash, to find the
    corresponding user keymap, even if it was modified.

    The hash value is unfortunately exposed to the users, so we just hope they don't touch that.
    """

    for kmi in keymap.keymap_items:
        if not kmi.properties:
            continue
        if 'hash' not in kmi.properties:
            continue

        if kmi.properties['hash'] == kmi_hash:
            return kmi

def unregister():
    global PIE_ADDON_KEYMAPS
    for kmi_hash, km_tuple in PIE_ADDON_KEYMAPS.items():
        kc, km, kmi = km_tuple
        km.keymap_items.remove(kmi)

    PIE_ADDON_KEYMAPS = {}