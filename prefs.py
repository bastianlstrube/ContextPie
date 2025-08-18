# SPDX-FileCopyrightText: 2016-2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

import io, platform, struct, urllib

import bpy
from bpy.types import AddonPreferences, Operator
from bpy.props import BoolProperty
from bl_ui.space_userpref import USERPREF_PT_interface_menus_pie
from .prefs_save_load import PrefsFileSaveLoadMixin, props_to_dict_recursive, update_prefs_on_file
from . import get_addon_prefs

from .hotkeys import (
    draw_hotkey_list,
    get_user_kmis_of_addon,
    get_user_kmi_of_addon,
)
from . import bl_info_copy

class ContextPie_AddonPrefs(
    PrefsFileSaveLoadMixin,
    AddonPreferences,
    USERPREF_PT_interface_menus_pie, # We use this class's `draw_centered` function to draw built-in pie settings.
):
    bl_idname = __package__

    debug: BoolProperty(
        name="Debug Mode",
        default=False,
        description="Enable some (ugly) debugging UI",
    )

    persistent_tools: BoolProperty(
        name="Persistent 'Knife' and 'Edge Loop' tools",
        default=False,
        description="Keeps 'Knife' and 'Insert Edge Loop' as the active tools after operation"
    )

    def draw(self, context):
        draw_prefs(self.layout, context, compact=False)

    def to_dict(self) -> dict:
        ret = props_to_dict_recursive(self)

        all_keymap_data = []
        for user_km, user_kmi in get_user_kmis_of_addon(bpy.context):
            data = {}
            data['keymap'] = user_km.name
            data['operator'] = user_kmi.idname

            NO_SAVE_OP_KWARGS = ('fallback_operator', 'fallback_op_kwargs')

            op_kwargs = {}
            if user_kmi.properties:
                op_kwargs = {
                    key: getattr(user_kmi.properties, key)
                    for key in user_kmi.properties.keys()
                    if hasattr(user_kmi.properties, key) and key not in NO_SAVE_OP_KWARGS
                }

            data['op_kwargs'] = op_kwargs

            data['key_kwargs'] = {
                'type' : user_kmi.type,
                'value' : user_kmi.value,
                'ctrl' : bool(user_kmi.ctrl),
                'shift' : bool(user_kmi.shift),
                'alt' : bool(user_kmi.alt),
                'any' : bool(user_kmi.any),
                'oskey' : bool(user_kmi.oskey),
                'key_modifier' : user_kmi.key_modifier,
                'active' : user_kmi.active
            }

            all_keymap_data.append(data)

        ret["hotkeys"] = all_keymap_data

        return ret

    def apply_prefs_from_dict_recursive(self, propgroup, data):
        success = True
        if 'hotkeys' in data:
            hotkeys = data.pop("hotkeys")
            if type(hotkeys) == dict:
                # Pre-1.6.8 code, with the keymap hash system.
                if not(self.apply_hotkeys_pre_v168(hotkeys)):
                    success = False
            else:
                # v1.6.8 and beyond.
                for hotkey in hotkeys:
                    op_kwargs = {}
                    if 'name' in hotkey['op_kwargs']:
                        op_kwargs['name'] = hotkey['op_kwargs']['name']
                    _user_km, user_kmi = get_user_kmi_of_addon(bpy.context, hotkey['keymap'], hotkey['operator'], op_kwargs)
                    if not user_kmi:
                        print("Failed to apply Keymap: ", hotkey['keymap'], hotkey['operator'], op_kwargs)
                        success = False
                        continue
                    op_kwargs = hotkey.pop('op_kwargs')
                    for key, value in op_kwargs.items():
                        setattr(user_kmi.properties, key, value)
                    for key, value in hotkey['key_kwargs'].items():
                        if key == "any" and not value:
                            continue
                        setattr(user_kmi, key, value)
        super().apply_prefs_from_dict_recursive(propgroup, data)
        return success

    def apply_hotkeys_pre_v168(self, hotkeys):
        """Best effort to read the old, hash-based keymap storage format. 
        This caused issues so it had to be re-worked, and versioned."""

        context = bpy.context

        complete_success = True

        for _kmi_hash, kmi_props in hotkeys.items():
            if 'key_cat' in kmi_props:
                keymap_name = kmi_props.pop('key_cat')

            op_kwargs = {}
            if 'name' in kmi_props['properties']:
                op_kwargs['name'] = kmi_props['properties']['name']

            idname = kmi_props['idname']
            if idname in ('wm.call_menu_pie', 'wm.call_menu_pie_wrapper'):
                idname = 'wm.call_menu_pie_drag_only_cpie'

            _user_km, user_kmi = get_user_kmi_of_addon(context, keymap_name, idname, op_kwargs)
            if not user_kmi:
                complete_success = False
                # print("No such user KeymapItem: ", keymap_name, idname, op_kwargs)
                continue

            if "properties" in kmi_props:
                op_kwargs = kmi_props.pop("properties")
                for key, value in op_kwargs.items():
                    if hasattr(user_kmi.properties, key):
                        setattr(user_kmi.properties, key, value)

            for key, value in kmi_props.items():
                if key == "any" and not value:
                    continue
                if key == "name":
                    continue
                if key == "idname":
                    continue
                try:
                    setattr(user_kmi, key, value)
                except:
                    # print("Failed to load keymap item:")
                    # print_kmi(user_kmi)
                    pass

        return complete_success


def draw_prefs(layout, context, compact=False):
    prefs = get_addon_prefs(context)


    layout.use_property_split = True
    layout.use_property_decorate = False

    if not compact:
        col = layout.column()
        row = col.row()
        row.operator('wm.url_open', text="Report Bug", icon='URL').url = (
            get_bug_report_url()
        )
        row.prop(prefs, 'debug', icon='BLANK1', text="", emboss=False)
        col.prop(prefs, 'use_auto_save')
        col.prop(prefs, 'persistent_tools') #, icon='TOOL_SETTINGS')

    header, builtins_panel = layout.panel(idname="Context Pie Builtin Prefs")
    header.label(text="Pie Preferences")
    if builtins_panel:
        prefs.draw_centered(context, layout)

    compact = context.area.width < 600
    header, hotkeys_panel = layout.panel(idname="Context Pie Hotkeys")
    header.label(text="Hotkeys")
    if hotkeys_panel:
        hotkeys_panel.operator('window.restore_deleted_hotkeys_v3pm', icon='KEY_RETURN')
        draw_hotkey_list(hotkeys_panel, context, prefs, compact=compact)


def get_bug_report_url(stack_trace=""):
    fh = io.StringIO()

    fh.write("**System Information**\n")
    fh.write(
        "Operating system: %s %d Bits\n"
        % (
            platform.platform(),
            struct.calcsize("P") * 8,
        )
    )
    fh.write("\n" "**Blender Version:** ")
    fh.write(
        "%s, branch: %s, commit: [%s](https://projects.blender.org/blender/blender/commit/%s)\n"
        % (
            bpy.app.version_string,
            bpy.app.build_branch.decode('utf-8', 'replace'),
            bpy.app.build_commit_date.decode('utf-8', 'replace'),
            bpy.app.build_hash.decode('ascii'),
        )
    )

    addon_version = bl_info_copy['version']
    fh.write(f"**Add-on Version**: {addon_version}\n")

    if stack_trace != "":
        fh.write("\nStack trace\n```\n" + stack_trace + "\n```\n")

    fh.write("\n" "---")

    fh.write("\n" "Description of the problem:\n" "\n")

    fh.seek(0)

    # Use the GitHub issue URL with the 'body' query parameter
    github_url = "https://github.com/bastianlstrube/ContextPie/issues/new"
    params = {'body': fh.read()}
    
    # Optional: You can also pre-fill the issue title and labels
    # params['title'] = 'New bug report from ContextPie'
    # params['labels'] = 'bug'

    return github_url + "?" + urllib.parse.urlencode(params)


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
