# SPDX-FileCopyrightText: 2016-2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

import io, platform, struct, urllib

import bpy
import addon_utils
from bpy.types import AddonPreferences, Operator, KeyMap, KeyMapItem
from bpy.props import BoolProperty
from bl_ui.space_userpref import USERPREF_PT_interface_menus_pie

from .blender_studio_utils.prefs import PrefsFileSaveLoadMixin, update_prefs_on_file, get_addon_prefs
from .blender_studio_utils.hotkeys import draw_hotkey_list

class ContextPie_AddonPrefs(
    PrefsFileSaveLoadMixin,
    AddonPreferences,
    USERPREF_PT_interface_menus_pie, # We use this class's `draw_centered` function to draw built-in pie settings.
):
    bl_idname = __package__

    persistent_tools: BoolProperty(
        name="Persistent 'Knife' and 'Edge Loop' tools",
        default=False,
        description="Keeps 'Knife' and 'Insert Edge Loop' as the active tools after operation"
    )

    def draw(self, context):
        draw_prefs(self.layout, context, compact=False)


def draw_prefs(layout, context, compact=False):
    prefs = get_addon_prefs(context)

    layout.use_property_split = True
    layout.use_property_decorate = False

    if not compact:
        col = layout.column()
        row = col.row()
        row.prop(prefs, 'debug', icon='BLANK1', text="", emboss=False)
        col.prop(prefs, 'persistent_tools') #, icon='TOOL_SETTINGS')

    header, builtins_panel = layout.panel(idname="Context Pie Builtin Prefs")
    header.label(text="Pie Preferences")
    if builtins_panel:
        prefs.draw_centered(context, layout)

    compact = context.area.width < 600
    header, hotkeys_panel = layout.panel(idname="Context Pie Hotkeys")
    header.label(text="Hotkeys")
    if hotkeys_panel:
        hotkeys_panel.operator('window.restore_deleted_hotkeys', icon='KEY_RETURN')
        draw_hotkey_list(context, hotkeys_panel, sort_mode='BY_OPERATOR', compact=compact, button_draw_func=button_draw_func)

def button_draw_func(layout, km: KeyMap, kmi: KeyMapItem, compact=False):
    """This function is passed as a callback to draw_hotkey_list, which will in turn call it
    with these parameters to draw the key combo UI, where we want to insert a "Drag" button."""
    split = layout.split(factor=0.65, align=True)
    split.prop(kmi, "type", text="", full_event=True)

    if kmi.idname != 'wm.call_menu_pie_drag_only':
        return
    if not kmi.properties:
        sub.label(text="Missing properties. This should never happen!")
        return
    text = "" if compact else "Drag"

    sub = split.row(align=True)
    sub.enabled = kmi.active
    op = sub.operator(
        'wm.toggle_keymap_item_property',
        text=text,
        icon='MOUSE_MOVE',
        depress=kmi.properties.on_drag,
    )
    op.km_name = km.name
    op.kmi_idname = kmi.idname
    op.pie_name = kmi.properties.name
    op.prop_name = 'on_drag'


class WINDOW_OT_context_pie_prefs_save(Operator):
    """Save Context Pie add-on preferences"""

    bl_idname = "window.context_pie_prefs_save"
    bl_label = "Save Pie Hotkeys"
    bl_options = {'REGISTER'}

    def execute(self, context):
        filepath, data = update_prefs_on_file(context)
        self.report({'INFO'}, f"Saved Pie Prefs to {filepath}.")
        return {'FINISHED'}


class WINDOW_OT_context_pie_prefs_load(Operator):
    """Load Context Pie add-on preferences"""

    bl_idname = "window.context_pie_prefs_load"
    bl_label = "Load Pie Hotkeys"
    bl_options = {'REGISTER'}

    def execute(self, context):
        prefs = get_addon_prefs(context)
        filepath = prefs.get_prefs_filepath()
        success = prefs.load_and_apply_prefs_from_file()

        if success:
            self.report({'INFO'}, f"Loaded pie preferences from {filepath}.")
        else:
            self.report({'ERROR'}, "Failed to load Pie preferences.")

        return {'FINISHED'}


registry = [
    ContextPie_AddonPrefs,
    WINDOW_OT_context_pie_prefs_save,
    WINDOW_OT_context_pie_prefs_load,
]


def register():
    ContextPie_AddonPrefs.register_autoload_from_file()
