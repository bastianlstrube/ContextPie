# SPDX-FileCopyrightText: 2016-2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import json


class WM_OT_call_menu_pie_drag_only(Operator):
    bl_idname = "wm.call_menu_pie_drag_only_cpie"
    bl_label = "Pie Menu on Drag"
    bl_description = (
        "Summon a pie menu only on mouse drag, otherwise pass the hotkey through"
    )
    bl_options = {'REGISTER', 'INTERNAL'}

    name: StringProperty(options={'SKIP_SAVE'})
    fallback_operator: StringProperty(options={'SKIP_SAVE'})
    op_kwargs: StringProperty(default="{}", options={'SKIP_SAVE'})

    def invoke(self, context, event):
        self.init_mouse_x = event.mouse_x
        self.init_mouse_y = event.mouse_y
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.value == 'RELEASE':
            parts = self.fallback_operator.split(".")
            op = bpy.ops
            for part in parts:
                op = getattr(op, part)
            kwargs = json.loads(self.op_kwargs)
            op('INVOKE_DEFAULT', **kwargs)
            return {'CANCELLED'}
        threshold = context.preferences.inputs.drag_threshold
        delta_x = abs(event.mouse_x - self.init_mouse_x)
        delta_y = abs(event.mouse_y - self.init_mouse_y)
        if delta_x > threshold or delta_y > threshold:
            return self.execute(context)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name=self.name)
        return {'FINISHED'}


registry = [WM_OT_call_menu_pie_drag_only]