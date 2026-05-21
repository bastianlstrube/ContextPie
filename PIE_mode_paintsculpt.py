# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from bl_ui.properties_paint_common import UnifiedPaintPanel

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


def draw_brush_properties(box, context, brush, capabilities):

    def draw_property(box, context, brush, prop, text=None):
        unified_name = f"use_unified_{prop}"
        pressure_name = f"use_pressure_{prop}"
        try:
            UnifiedPaintPanel.prop_unified(
                box, context, brush, prop,
                unified_name=unified_name,
                pressure_name=pressure_name,
                text=text, slider=True,
            )
        except Exception as e:
            print(f"Error drawing property {prop}: {e}")

    if hasattr(capabilities, "has_color") and capabilities.has_color:
        split = box.split(factor=0.1)
        UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
        UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
        if hasattr(brush, "blend"):
            box.prop(brush, "blend", text="")

    ups = UnifiedPaintPanel.paint_settings(context).unified_paint_settings
    size_prop = "size"
    size_owner = ups if ups.use_unified_size else brush
    if size_owner.use_locked_size == 'SCENE':
        size_prop = "unprojected_radius"

    draw_property(box, context, brush, size_prop, text="Radius")
    draw_property(box, context, brush, "strength", text="Strength")

    sculpt_properties = {
        "auto_smooth_factor": "Auto Smooth",
        "normal_weight": "Normal Weight",
        "crease_pinch_factor": ("Pinch", "Magnify"),
        "rake_factor": "Rake Factor",
        "plane_offset": "Plane Offset",
        "plane_trim": "Distance",
        "height": "Height",
        "weight": "Weight"
    }

    for prop, text in sculpt_properties.items():
        if hasattr(capabilities, f"has_{prop}") and getattr(capabilities, f"has_{prop}"):
            if isinstance(text, tuple):
                text = text[1] if brush.sculpt_tool in {'BLOB', 'SNAKE_HOOK'} else text[0]
            draw_property(box, context, brush, prop, text=text)


class CPIE_MT_mode_sculpt(Menu):
    bl_idname = "CPIE_MT_mode_sculpt"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        paint_path = 'tool_settings.sculpt'
        brush_path = f'{paint_path}.brush'
        ups_path = f'{paint_path}.unified_paint_settings'
        # Sculpt brushes can be locked to view (pixels = .size) or scene (world = .unprojected_size).
        # Brush.use_locked_size is 'VIEW' | 'SCENE'; ups.use_locked_size mirrors it for unified.
        brush = context.tool_settings.sculpt.brush
        ups = context.tool_settings.sculpt.unified_paint_settings
        size_attr = 'unprojected_size' if (ups.use_unified_size and ups.use_locked_size == 'SCENE') \
                    or (not ups.use_unified_size and brush and brush.use_locked_size == 'SCENE') \
                    else 'size'

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle")
        # SOUTH — drag to set brush size (LMB confirm, RMB cancel)
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = f'{brush_path}.{size_attr}'
        op.data_path_secondary = f'{ups_path}.{size_attr}'
        op.use_secondary = f'{ups_path}.use_unified_size'
        op.image_id = brush_path
        # NORTH — drag to set brush strength
        op = pie.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
        op.data_path_primary = f'{brush_path}.strength'
        op.data_path_secondary = f'{ups_path}.strength'
        op.use_secondary = f'{ups_path}.use_unified_strength'
        op.image_id = brush_path


class CPIE_MT_mode_vertexpaint(Menu):
    bl_idname = "CPIE_MT_mode_vertexpaint"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.vertex_paint.brush
        capabilities = brush.vertex_paint_capabilities

        draw_brush_properties(box, context, brush, capabilities)


class CPIE_MT_mode_weightpaint(Menu):
    bl_idname = "CPIE_MT_mode_weightpaint"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.weight_paint.brush
        capabilities = brush.weight_paint_capabilities

        draw_brush_properties(box, context, brush, capabilities)


class CPIE_MT_mode_texpaint(Menu):
    bl_idname = "CPIE_MT_mode_texpaint"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        paint_path = 'tool_settings.image_paint'
        brush_path = f'{paint_path}.brush'
        ups_path = f'{paint_path}.unified_paint_settings'
        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        # SOUTH — drag to set brush size (LMB confirm, RMB cancel)
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = f'{brush_path}.size'
        op.data_path_secondary = f'{ups_path}.size'
        op.use_secondary = f'{ups_path}.use_unified_size'
        op.image_id = brush_path
        # NORTH — drag to set brush strength
        op = pie.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
        op.data_path_primary = f'{brush_path}.strength'
        op.data_path_secondary = f'{ups_path}.strength'
        op.use_secondary = f'{ups_path}.use_unified_strength'
        op.image_id = brush_path


registry = [
    CPIE_MT_mode_sculpt,
    CPIE_MT_mode_vertexpaint,
    CPIE_MT_mode_weightpaint,
    CPIE_MT_mode_texpaint,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    for menu, keymap_name in (
        (CPIE_MT_mode_sculpt, "Sculpt"),
        (CPIE_MT_mode_vertexpaint, "Vertex Paint"),
        (CPIE_MT_mode_weightpaint, "Weight Paint"),
        (CPIE_MT_mode_texpaint, "Image Paint"),
    ):
        if keymap_name not in default_keymaps:
            continue
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=menu.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
            keymap_name=keymap_name,
            on_drag=True,
        )
