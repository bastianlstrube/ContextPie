# SPDX-FileCopyrightText: 2016-2026 Bastian L Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

class WM_OT_toggle_keymap_item_on_drag(bpy.types.Operator):
    "When Drag is enabled, this pie menu will only appear when the mouse is dragged while the assigned key combo is held down"
    bl_idname = "wm.toggle_keymap_item_property"
    bl_label = "Toggle On Drag"
    bl_options = {'REGISTER', 'INTERNAL'}

    km_name: bpy.props.StringProperty(options={'SKIP_SAVE'})
    kmi_idname: bpy.props.StringProperty(options={'SKIP_SAVE'})
    pie_name: bpy.props.StringProperty(options={'SKIP_SAVE'})
    prop_name: bpy.props.StringProperty(options={'SKIP_SAVE'})

    def execute(self, context):
        # Another sign of the fragility of Blender's keymap API.
        # The reason for the existence of this property wrapper operator is that
        # when we draw the `on_drag` property in the UI directly, Blender's keymap
        # system (for some reason??) doesn't realize that a keymap entry has changed,
        # and fails to refresh caches, which has disasterous results.
        # This operator fires a refreshing of internal keymap data via
        # `user_kmi.type = user_kmi.type`

        user_kc = context.window_manager.keyconfigs.user
        user_km = user_kc.keymaps.get(self.km_name)
        if not user_km:
            # This really shouldn't happen.
            self.report({'ERROR'}, f"Couldn't find KeyMap: {self.km_name}")
            return {'CANCELLED'}

        for user_kmi in user_km.keymap_items:
            if user_kmi.idname == self.kmi_idname and user_kmi.properties and user_kmi.properties.name == self.pie_name:
                if hasattr(user_kmi.properties, self.prop_name):
                    setattr(
                        user_kmi.properties,
                        self.prop_name,
                        not getattr(user_kmi.properties, self.prop_name),
                    )
                    # This is the magic line that causes internal keymap data to be kept up to date and not break.
                    user_kmi.type = user_kmi.type
                else:
                    self.report({'ERROR'}, "Property not in keymap: " + self.prop_name)
                    return {'CANCELLED'}

        return {'FINISHED'}

if "bl_ext.blender_org.viewport_pie_menus" not in bpy.context.preferences.addons:
    registry = [WM_OT_toggle_keymap_item_on_drag,]
else:
    registry = []
