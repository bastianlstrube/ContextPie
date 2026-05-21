# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

class SUBPIE_MT_gp_select(Menu):
    bl_idname = "SUBPIE_MT_gp_select"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("grease_pencil.select_ends", text='Ends')
        # EAST
        pie.operator("grease_pencil.select_more", text='Grow Selection')
        # SOUTH
        pie.operator("grease_pencil.select_less", text='Shrink Selection')
        # NORTH
        pie.operator("grease_pencil.select_alternate", text='Alternate Points')
        # NORTH-WEST
        pie.operator("grease_pencil.select_all", text='Invert Selection').action = 'INVERT'
        # NORTH-EAST
        pie.operator("grease_pencil.select_random", text='Random Selection')
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.operator("grease_pencil.select_linked", text='Linked')


class CPIE_MT_mode_greasepencil(Menu):
    bl_idname = "CPIE_MT_mode_greasepencil"
    bl_label = "Grease Pencil Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        obj = context.object
        is_v3 = obj and obj.type == 'GREASEPENCIL'
        active_mode = context.mode

        # WEST - Object Mode
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE").mode = 'OBJECT'

        # EAST - Edit Mode
        op = pie.operator("object.mode_set", text="Edit Mode", icon="EDITMODE_HLT")
        op.mode = 'EDIT' if is_v3 else 'EDIT_GPENCIL'

        # SOUTH - Active Brush Quick Settings Panel
        if "PAINT" in active_mode or "SCULPT" in active_mode:
            paint_attr = 'gpencil_sculpt' if "SCULPT" in active_mode else 'gpencil_paint'
            paint = getattr(context.tool_settings, paint_attr, None)
            brush = getattr(paint, 'brush', None) if paint else None
            if brush:
                box = pie.box().column()
                op = box.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
                op.data_path_primary = f'tool_settings.{paint_attr}.brush.size'
                
                op = box.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
                if hasattr(brush, "gpencil_settings") and hasattr(brush.gpencil_settings, "pen_strength"):
                    op.data_path_primary = f'tool_settings.{paint_attr}.brush.gpencil_settings.pen_strength'
                else:
                    op.data_path_primary = f'tool_settings.{paint_attr}.brush.strength'
            else:
                pie.separator()
        else:
            pie.separator()

        # NORTH - Sculpt Mode
        op = pie.operator("object.mode_set", text="Sculpt Mode", icon="SCULPTMODE_HLT")
        op.mode = 'SCULPT_GREASE_PENCIL' if is_v3 else 'SCULPT_GPENCIL'

        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()

        # SOUTH-WEST - Draw/Paint Mode
        op = pie.operator("object.mode_set", text="Draw Mode", icon="GREASEPENCIL")
        op.mode = 'PAINT_GREASE_PENCIL' if is_v3 else 'PAINT_GPENCIL'

        # SOUTH-EAST
        if "EDIT" in active_mode:
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_gp_select"
        else:
            pie.separator()


registry = [
    SUBPIE_MT_gp_select,
    CPIE_MT_mode_greasepencil,
]

def register():
    keymaps = [
        "Grease Pencil Edit Mode", "Grease Pencil Sculpt Mode", "Grease Pencil Draw Mode",
        "Grease Pencil Stroke Edit Mode", "Grease Pencil Stroke Sculpt Mode", "Grease Pencil Stroke Paint Mode"
    ]
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    for km in keymaps:
        if km not in default_keymaps:
            continue
        try:
            WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
                pie_name=CPIE_MT_mode_greasepencil.bl_idname,
                hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
                keymap_name=km,
                on_drag=True,
            )
        except Exception:
            pass