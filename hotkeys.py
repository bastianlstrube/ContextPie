# SPDX-FileCopyrightText: 2016-2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import json
from . import __package__ as base_package

pie_addon_keymaps = []

def register_hotkey(
    bl_idname, hotkey_kwargs, *, key_cat='Window', op_kwargs={}
):
    """This function inserts a 'hash' into the created KeyMapItems' properties,
    so they can be compared to each other, and duplicates can be avoided."""

    wm = bpy.context.window_manager

    space_type = wm.keyconfigs.default.keymaps[key_cat].space_type

    addon_keyconfig = wm.keyconfigs.addon
    if not addon_keyconfig:
        # This happens when running Blender in background mode.
        return

    addon_keymaps = addon_keyconfig.keymaps
    addon_km = addon_keymaps.get(key_cat)
    if not addon_km:
        addon_km = addon_keymaps.new(name=key_cat, space_type=space_type)

    addon_kmi = addon_km.keymap_items.new(bl_idname, **hotkey_kwargs)
    for key in op_kwargs:
        value = op_kwargs[key]
        setattr(addon_kmi.properties, key, value)

    pie_addon_keymaps.append((addon_km, addon_kmi))


def draw_hotkey_list(layout, context):
    user_kc = context.window_manager.keyconfigs.user

    keymap_data = sorted(pie_addon_keymaps, key=lambda tup: tup[1].properties.name)

    prev_kmi = None
    for addon_km, addon_kmi in keymap_data:

        user_km = user_kc.keymaps.get(addon_km.name)
        if not user_km:
            # This really shouldn't happen.
            continue
        user_kmi = find_kmi_in_km_by_pie_name(user_km, addon_kmi.properties.name)

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

def find_kmi_in_km_by_pie_name(keymap, pie_name):
    """For pie menu hotkeys specifically, we can use the pie menu name as an identifier,
    allowing us to find and draw the user keyconfig items in the preferences.
    
    I tried inserting a 'hash' custom property to the keymap entries instead, but
    this caused a bug where changes to the keymap entries fail to save to or load from user preferences.
    https://projects.blender.org/extensions/space_view3d_pie_menus/issues/2
    """
    for kmi in keymap.keymap_items:
        if kmi.idname in {'wm.call_menu_pie', 'wm.call_menu_pie_drag_only'} and kmi.properties.name == pie_name:
            return kmi

def unregister():
    for km, kmi in pie_addon_keymaps:
        km.keymap_items.remove(kmi)