# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import Menu, Operator
from bpy.props import EnumProperty, StringProperty
from bl_ui.properties_paint_common import UnifiedPaintPanel
from mathutils import Color

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


_SQRT2_INV = 1.0 / (2.0 ** 0.5)
# Unit vector pointing from the slot's cursor position back to the pie center.
# Pie auto-confirms at the slot position so event.mouse_* at invoke is on the slot,
# not the center. We translate back along the opposite of the slot direction.
_PIE_CENTER_OFFSET = {
    'H': ( _SQRT2_INV, -_SQRT2_INV),  # NW slot -> center is to the lower-right
    'S': (-_SQRT2_INV, -_SQRT2_INV),  # NE slot -> center is to the lower-left
    'V': (-_SQRT2_INV,  _SQRT2_INV),  # SE slot -> center is to the upper-left
}


def _get_pie_radius(context):
    prefs = context.preferences
    for path in ('system.pie_menu_radius', 'view.pie_menu_radius', 'inputs.pie_menu_radius'):
        obj = prefs
        for part in path.split('.'):
            obj = getattr(obj, part, None)
            if obj is None:
                break
        if isinstance(obj, (int, float)):
            return float(obj)
    return 100.0


def _disc_verts(cx, cy, radius, segments=48):
    verts = [(cx, cy)]
    for i in range(segments + 1):
        a = (i / segments) * 2.0 * math.pi
        verts.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))
    return verts


def _draw_color_indicator(op, context):
    region = context.region
    if region is None or not hasattr(op, '_anchor_x'):
        return
    cx = op._anchor_x
    cy = op._anchor_y
    radius = 42

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')

    # Dark outer ring for contrast
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": _disc_verts(cx, cy, radius + 4)})
    shader.bind()
    shader.uniform_float("color", (0.0, 0.0, 0.0, 0.75))
    batch.draw(shader)

    # Color fill
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": _disc_verts(cx, cy, radius)})
    shader.uniform_float("color", (*op._brush.color[:3], 1.0))
    batch.draw(shader)

    gpu.state.blend_set('NONE')


def _resolve_path(context, path):
    obj = context
    for part in path.split('.'):
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


class CPIE_OT_brush_color_hsv(Operator):
    """Drag horizontally to set the brush color's hue, saturation, or value"""
    bl_idname = "cpie.brush_color_hsv"
    bl_label = "Brush Color HSV"
    bl_options = {'REGISTER', 'UNDO'}

    component: EnumProperty(
        name="Component",
        items=[
            ('H', "Hue", "Adjust hue (wraps)"),
            ('S', "Saturation", "Adjust saturation"),
            ('V', "Value", "Adjust value"),
        ],
        default='H',
        options={'SKIP_SAVE'},
    )
    brush_path: StringProperty(
        name="Brush Path",
        description="Dotted path to brush, relative to context",
        default='tool_settings.vertex_paint.brush',
        options={'SKIP_SAVE'},
    )

    def invoke(self, context, event):
        brush = _resolve_path(context, self.brush_path)
        if brush is None or not hasattr(brush, 'color'):
            return {'CANCELLED'}
        self._brush = brush
        self._init_color = tuple(brush.color[:3])
        self._init_hsv = list(Color(self._init_color).hsv)
        self._init_x = event.mouse_x
        self._init_y = event.mouse_y
        off_x, off_y = _PIE_CENTER_OFFSET.get(self.component, (0.0, 0.0))
        radius = _get_pie_radius(context)
        self._anchor_x = event.mouse_region_x + off_x * radius
        self._anchor_y = event.mouse_region_y + off_y * radius
        self._draw_handle = None
        space_type = getattr(context.space_data, 'type', None)
        space_cls = {
            'VIEW_3D': bpy.types.SpaceView3D,
            'IMAGE_EDITOR': bpy.types.SpaceImageEditor,
        }.get(space_type)
        if space_cls is not None:
            self._draw_space = space_cls
            self._draw_handle = space_cls.draw_handler_add(
                _draw_color_indicator, (self, context), 'WINDOW', 'POST_PIXEL'
            )
        # Hue slot uses 2D drag (X=hue, Y=saturation); others stay on X only.
        cursor = 'SCROLL_XY' if self.component == 'H' else 'SCROLL_X'
        context.window.cursor_modal_set(cursor)
        if context.area:
            context.area.tag_redraw()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _apply(self, value):
        idx = 'HSV'.index(self.component)
        hsv = list(self._init_hsv)
        if idx == 0:
            hsv[idx] = value % 1.0
        else:
            hsv[idx] = max(0.0, min(1.0, value))
        c = Color()
        c.hsv = hsv
        self._brush.color = (c.r, c.g, c.b)
        return hsv[idx]

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            # 500px drag = full range; finer when shift held
            scale = 2000.0 if event.shift else 500.0
            dx = (event.mouse_x - self._init_x) / scale
            if self.component == 'H':
                # 2D: X = hue (wrap), Y = saturation (clamp)
                dy = (event.mouse_y - self._init_y) / scale
                h = (self._init_hsv[0] + dx) % 1.0
                s = max(0.0, min(1.0, self._init_hsv[1] + dy))
                c = Color()
                c.hsv = (h, s, self._init_hsv[2])
                self._brush.color = (c.r, c.g, c.b)
                if context.area:
                    context.area.header_text_set(f"Hue: {h:.3f}   Sat: {s:.3f}")
                    context.area.tag_redraw()
            else:
                idx = 'HSV'.index(self.component)
                applied = self._apply(self._init_hsv[idx] + dx)
                comp_name = {'S': 'Saturation', 'V': 'Value'}[self.component]
                if context.area:
                    context.area.header_text_set(f"{comp_name}: {applied:.3f}")
                    context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        elif event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE'} and event.value == 'PRESS':
            self._cleanup(context)
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._brush.color = self._init_color
            self._cleanup(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _cleanup(self, context):
        context.window.cursor_modal_restore()
        if context.area:
            context.area.header_text_set(None)
            context.area.tag_redraw()
        if self._draw_handle is not None:
            self._draw_space.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None


class CPIE_OT_brush_color_picker(Operator):
    """Open a color-wheel popup for the brush color"""
    bl_idname = "cpie.brush_color_picker"
    bl_label = "Brush Color"
    bl_options = {'REGISTER', 'UNDO'}

    brush_path: StringProperty(
        name="Brush Path",
        description="Dotted path to brush, relative to context",
        default='tool_settings.vertex_paint.brush',
        options={'SKIP_SAVE'},
    )

    def invoke(self, context, event):
        if _resolve_path(context, self.brush_path) is None:
            return {'CANCELLED'}
        return context.window_manager.invoke_popup(self, width=330)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        brush = _resolve_path(context, self.brush_path)
        if not brush:
            return
        # invoke_popup only accepts a width — the wheel's natural item height
        # is small, so we scale_y to force the wheel to match the wider width.
        layout = self.layout
        wheel_col = layout.column(align=True)
        wheel_col.scale_y = 2.4
        wheel_col.template_color_picker(brush, "color", value_slider=True)
        layout.prop(brush, "color", text="")


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

        paint_path = 'tool_settings.vertex_paint'
        brush_path = f'{paint_path}.brush'
        ups_path = f'{paint_path}.unified_paint_settings'

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST — open color wheel popup
        pie.operator("cpie.brush_color_picker", text="Color Wheel", icon='COLOR').brush_path = brush_path
        # SOUTH — drag to set brush size
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
        # NW — drag to set hue
        op = pie.operator("cpie.brush_color_hsv", text="Hue", icon='COLOR')
        op.component = 'H'
        op.brush_path = brush_path
        # NE — drag to set saturation
        op = pie.operator("cpie.brush_color_hsv", text="Saturation", icon='COLOR')
        op.component = 'S'
        op.brush_path = brush_path
        # SW
        pie.separator()
        # SE — drag to set value
        op = pie.operator("cpie.brush_color_hsv", text="Value", icon='COLOR')
        op.component = 'V'
        op.brush_path = brush_path


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
    CPIE_OT_brush_color_hsv,
    CPIE_OT_brush_color_picker,
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
