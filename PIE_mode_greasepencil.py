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


class CPIE_MT_mode_gp_paint(Menu):
    bl_idname = "CPIE_MT_mode_gp_paint"
    bl_label = "Grease Pencil Draw Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        brush = None
        size_path = 'tool_settings.gpencil_paint.brush.size'
        strength_path = 'tool_settings.gpencil_paint.brush.strength'
        image_id = 'tool_settings.gpencil_paint.brush'

        if hasattr(context.tool_settings, "gpencil_paint"):
            paint_settings = context.tool_settings.gpencil_paint
            if paint_settings and paint_settings.brush:
                brush = paint_settings.brush
                if hasattr(brush, "gpencil_settings") and hasattr(brush.gpencil_settings, "pen_strength"):
                    strength_path = 'tool_settings.gpencil_paint.brush.gpencil_settings.pen_strength'

        # WEST
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE").mode = 'OBJECT'
        
        # EAST — Inline the full material/color panel directly into the pie menu
        panel_cls = getattr(bpy.types, "MAT_PT_TexPaintRMBMenu", None)
        if panel_cls:
            box = pie.box()
            panel_proxy = type("PanelProxy", (), {"layout": box})()
            panel_cls.draw(panel_proxy, context)
        else:
            pie.separator()
        
        # SOUTH
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = size_path
        op.image_id = image_id
        
        # NORTH
        op = pie.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
        op.data_path_primary = strength_path
        op.image_id = image_id


class CPIE_MT_mode_gp_sculpt(Menu):
    bl_idname = "CPIE_MT_mode_gp_sculpt"
    bl_label = "Grease Pencil Sculpt Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        brush = None
        size_path = 'tool_settings.gpencil_sculpt_paint.brush.size'
        strength_path = 'tool_settings.gpencil_sculpt_paint.brush.strength'
        image_id = 'tool_settings.gpencil_sculpt_paint.brush'

        # 1. Modern Blender (GPv3 architecture)
        if hasattr(context.tool_settings, "gpencil_sculpt_paint"):
            paint_settings = context.tool_settings.gpencil_sculpt_paint
            if paint_settings and paint_settings.brush:
                brush = paint_settings.brush
                if hasattr(brush, "gpencil_settings") and hasattr(brush.gpencil_settings, "pen_strength"):
                    strength_path = 'tool_settings.gpencil_sculpt_paint.brush.gpencil_settings.pen_strength'

        # 2. Legacy Blender fallback
        if not brush and hasattr(context.tool_settings, "gpencil_sculpt"):
            sculpt_settings = context.tool_settings.gpencil_sculpt
            if sculpt_settings and hasattr(sculpt_settings, 'brush'):
                brush = sculpt_settings.brush
                size_path = 'tool_settings.gpencil_sculpt.brush.size'
                strength_path = 'tool_settings.gpencil_sculpt.brush.strength'
                image_id = 'tool_settings.gpencil_sculpt.brush'

        # WEST
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE").mode = 'OBJECT'

        # EAST
        pie.separator()

        # SOUTH
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = size_path
        op.image_id = image_id

        # NORTH
        op = pie.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
        op.data_path_primary = strength_path
        op.image_id = image_id


class CPIE_MT_mode_gp_edit(Menu):
    bl_idname = "CPIE_MT_mode_gp_edit"
    bl_label = "Grease Pencil Edit Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE").mode = 'OBJECT'
        
        # EAST
        pie.operator("grease_pencil.set_selection_mode", text="Point Mode", icon="VERTEXSEL").mode = 'POINT'
        
        # SOUTH
        pie.operator("grease_pencil.set_selection_mode", text="Stroke Mode", icon="FACESEL").mode = 'STROKE'

        # NORTH
        pie.operator("grease_pencil.set_selection_mode", text="Segment Mode", icon="EDGESEL").mode = 'SEGMENT'
        
        # NORTH-WEST
        pie.separator()
        
        # NORTH-EAST
        pie.separator()
        
        # SOUTH-WEST
        pie.separator()
        
        # SOUTH-EAST
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_gp_select"


registry = [
    SUBPIE_MT_gp_select,
    CPIE_MT_mode_gp_paint,
    CPIE_MT_mode_gp_sculpt,
    CPIE_MT_mode_gp_edit,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    
    keymap_bindings = (
        (CPIE_MT_mode_gp_paint, "Grease Pencil Paint Mode"),
        (CPIE_MT_mode_gp_paint, "Grease Pencil Draw Mode"),
        (CPIE_MT_mode_gp_paint, "Grease Pencil Stroke Paint Mode"),
        (CPIE_MT_mode_gp_sculpt, "Grease Pencil Sculpt Mode"),
        (CPIE_MT_mode_gp_sculpt, "Grease Pencil Stroke Sculpt Mode"),
        (CPIE_MT_mode_gp_edit, "Grease Pencil Edit Mode"),
        (CPIE_MT_mode_gp_edit, "Grease Pencil Stroke Edit Mode"),
    )
    
    for menu, keymap_name in keymap_bindings:
        if keymap_name not in default_keymaps:
            continue
        try:
            WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
                pie_name=menu.bl_idname,
                hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
                keymap_name=keymap_name,
                on_drag=True,
            )
        except Exception as e:
            print(f"Failed to register hotkey for {keymap_name}: {e}")