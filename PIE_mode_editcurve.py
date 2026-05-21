# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class SUBPIE_MT_curveSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("curve.select_previous", text='Previous')
        # EAST
        pie.operator("curve.select_next", text='Next')
        # SOUTH
        pie.operator("curve.select_similar", text='Similar Direction').type = 'DIRECTION'
        # NORTH
        pie.operator("curve.select_nth", text='Checker Deselect')
        # NORTH-WEST
        pie.operator("curve.select_all", text='Invert').action = 'INVERT'
        # NORTH-EAST
        pie.operator("curve.select_random", text='Random')
        # SOUTH-WEST
        pie.operator("curve.select_similar", text='Similar Radius').type = 'RADIUS'
        # SOUTH-EAST
        pie.operator("curve.select_linked", text='Linked')


class SUBPIE_MT_curveTypeHandles(Menu):
    bl_label = "Set Curve/Handle Type"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("curve.handle_type_set", text='Automatic Handles').type = 'AUTOMATIC'
        # EAST
        pie.operator("curve.handle_type_set", text='Toggle Free/Align Handles').type = 'TOGGLE_FREE_ALIGN'
        # SOUTH
        pie.operator("curve.spline_type_set", text='Bezier Curve').type = 'BEZIER'
        # NORTH
        pie.operator("curve.handle_type_set", text='Free Handles').type = 'FREE_ALIGN'
        # NORTH-WEST
        pie.operator("curve.handle_type_set", text='Vector Handles').type = 'VECTOR'
        # NORTH-EAST
        pie.operator("curve.handle_type_set", text='Aligned Handles').type = 'ALIGNED'
        # SOUTH-WEST
        pie.operator("curve.spline_type_set", text='Poly Curve').type = 'POLY'
        # SOUTH-EAST
        pie.operator("curve.spline_type_set", text='NURBS Curve').type = 'NURBS'


class CPIE_MT_mode_editcurve(Menu):
    bl_idname = "CPIE_MT_mode_editcurve"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator("curve.switch_direction")
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Curve/Handle Type...').name = "SUBPIE_MT_curveTypeHandles"
        # NORTH
        pie.operator("curve.cyclic_toggle")
        # NORTH WEST
        pie.operator("wm.tool_set_by_id", text="Pen Tool", icon='CURVE_BEZCURVE').name = "builtin.pen"
        # NORTH EAST
        pie.operator("wm.tool_set_by_id", text="Curve Draw Tool", icon='GREASEPENCIL').name = "builtin.draw"
        # SOUTH WEST
        pie.menu("VIEW3D_MT_edit_curve_context_menu", text="Context Menu", icon="COLLAPSEMENU")
        # SOUTH EAST
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_curveSelect"


registry = [
    SUBPIE_MT_curveSelect,
    SUBPIE_MT_curveTypeHandles,
    CPIE_MT_mode_editcurve,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    if "Curve" not in default_keymaps:
        return
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=CPIE_MT_mode_editcurve.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        keymap_name="Curve",
        on_drag=True,
    )
