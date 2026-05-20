# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

class SUBPIE_MT_gp_select(Menu):
    bl_label = "Select"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST / EAST
        pie.operator("grease_pencil.select_ends", text='Ends')
        pie.operator("grease_pencil.select_more", text='Grow Selection')
        # SOUTH / NORTH
        pie.operator("grease_pencil.select_less", text='Shrink Selection')
        pie.operator("grease_pencil.select_alternate", text='Alternate Points')
        # NORTH-WEST / NORTH-EAST
        pie.operator("grease_pencil.select_all", text='Invert Selection').action = 'INVERT'
        pie.operator("grease_pencil.select_random", text='Random Selection')
        # SOUTH-WEST / SOUTH-EAST
        pie.separator()
        pie.operator("grease_pencil.select_linked", text='Linked')

class VIEW3D_PIE_MT_gp_mode(Menu):
    bl_idname = "PIE_MT_gp_mode"
    bl_label = "Grease Pencil Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        obj = context.object
        is_v3 = obj and obj.type == 'GREASEPENCIL'

        # WEST - Object Mode
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE").mode = 'OBJECT'
        
        # EAST - Edit Mode
        op = pie.operator("object.mode_set", text="Edit Mode", icon="EDITMODE_HLT")
        op.mode = 'EDIT' if is_v3 else 'EDIT_GPENCIL'

        # SOUTH - Active Brush Quick Settings Panel
        box = pie.box().column()
        active_mode = context.mode
        paint_path = 'tool_settings.gpencil_sculpt' if "SCULPT" in active_mode else 'tool_settings.gpencil_paint'
        brush = getattr(getattr(context.tool_settings, paint_path.split('.')[-1], None), "brush", None)

        if brush:
            op_sz = box.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
            op_sz.data_path_primary = f'{paint_path}.brush.size'
            
            op_st = box.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
            if hasattr(brush, "gpencil_settings") and hasattr(brush.gpencil_settings, "pen_strength"):
                op_st.data_path_primary = f'{paint_path}.brush.gpencil_settings.pen_strength'
            else:
                op_st.data_path_primary = f'{paint_path}.brush.strength'
        else:
            box.label(text="No Brush Context")

        # NORTH - Sculpt Mode
        op = pie.operator("object.mode_set", text="Sculpt Mode", icon="SCULPTMODE_HLT")
        op.mode = 'SCULPT_GREASE_PENCIL' if is_v3 else 'SCULPT_GPENCIL'

        # NORTH-WEST / NORTH-EAST
        pie.separator()
        pie.separator()

        # SOUTH-WEST
        op = pie.operator("object.mode_set", text="Draw Mode", icon="GREASEPENCIL")
        op.mode = 'PAINT_GREASE_PENCIL' if is_v3 else 'PAINT_GPENCIL'

        # SOUTH-EAST
        if "EDIT" in active_mode:
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_gp_select"
        else:
            pie.separator()

registry = [
    SUBPIE_MT_gp_select,
    VIEW3D_PIE_MT_gp_mode,
]

def register():
    keymaps = [
        "Grease Pencil Edit Mode", "Grease Pencil Sculpt Mode", "Grease Pencil Paint Mode",
        "Grease Pencil Stroke Edit Mode", "Grease Pencil Stroke Sculpt Mode", "Grease Pencil Stroke Paint Mode"
    ]
    for km in keymaps:
        try:
            WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
                pie_name=VIEW3D_PIE_MT_gp_mode.bl_idname,
                hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
                keymap_name=km,
                on_drag=True,
            )
        except Exception:
            pass