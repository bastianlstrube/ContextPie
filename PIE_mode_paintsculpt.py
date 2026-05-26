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


# --- Persistent GPU Cache ---
_shader = None
_unit_disk_batch = None

def _get_unit_disk_batch():
    global _shader, _unit_disk_batch
    if _shader is None:
        _shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    if _unit_disk_batch is None:
        verts = [(0.0, 0.0, 0.0)]
        segments = 48
        for i in range(segments + 1):
            a = (i / segments) * 2.0 * math.pi
            verts.append((math.cos(a), math.sin(a), 0.0))
        _unit_disk_batch = batch_for_shader(_shader, 'TRI_FAN', {"pos": verts})
    return _shader, _unit_disk_batch


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


def _draw_color_indicator(op, context):
    if not hasattr(op, '_anchor_x') or not getattr(op, '_brush', None):
        return

    try:
        shader, batch = _get_unit_disk_batch()
    except Exception as e:
        print(f"[CPIE] Drawing error: {e}")
        return

    cx = op._anchor_x
    cy = op._anchor_y
    radius = 42

    gpu.state.blend_set('ALPHA')
    shader.bind()

    with gpu.matrix.push_pop():
        gpu.matrix.translate((cx, cy, 0.0))
        
        # 1. Dark outer ring for contrast
        with gpu.matrix.push_pop():
            gpu.matrix.scale((radius + 2, radius + 2, 1.0))
            shader.uniform_float("color", (0.0, 0.0, 0.0, 0.75))
            batch.draw(shader)

        # 2. Color fill
        with gpu.matrix.push_pop():
            gpu.matrix.scale((radius, radius, 1.0))
            target_obj = getattr(op, '_target_obj', op._brush)
            color = getattr(target_obj, "color", (1.0, 1.0, 1.0))
            shader.uniform_float("color", (*color[:3], 1.0))
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
    """Modal drag to adjust the brush color in HSV space"""
    bl_idname = "cpie.brush_color_hsv"
    bl_label = "Brush Color HSV"
    bl_options = {'REGISTER', 'UNDO'}

    component: EnumProperty(
        name="Component",
        items=[
            ('U', "Hue + Saturation", "Adjust hue (X drag) and saturation (Y drag) together"),
            ('S', "Saturation", "Adjust saturation"),
            ('V', "Value", "Adjust value"),
            ('H', "Hue", "Adjust hue only (X drag)"),
            ('X', "Value + Saturation", "Adjust value (X drag) and saturation (Y drag) together"),
        ],
        default='U',
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
        
        ups_path = self.brush_path.rsplit('.', 1)[0] + '.unified_paint_settings'
        self._ups = _resolve_path(context, ups_path)
        
        if self._ups and getattr(self._ups, "use_unified_color", False):
            self._target_obj = self._ups
        else:
            self._target_obj = brush
            
        self._init_color = tuple(self._target_obj.color[:3])
        self._init_hsv = list(Color(self._init_color).hsv)
        self._init_x = event.mouse_x
        self._init_y = event.mouse_y
        
        self._anchor_x = event.mouse_region_x
        self._anchor_y = event.mouse_region_y
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
            
        cursor = 'SCROLL_XY' if self.component in {'H', 'X'} else 'SCROLL_X'
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
        rgb = (c.r, c.g, c.b)
        
        self._brush.color = rgb
        if self._ups:
            self._ups.color = rgb
            
        return hsv[idx]

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            scale = 2000.0 if event.shift else 500.0
            dx = (event.mouse_x - self._init_x) / scale
            
            if self.component == 'H':
                dy = (event.mouse_y - self._init_y) / scale
                h = (self._init_hsv[0] + dx) % 1.0
                s = max(0.0, min(1.0, self._init_hsv[1] + dy))
                c = Color()
                c.hsv = (h, s, self._init_hsv[2])
                rgb = (c.r, c.g, c.b)
                self._brush.color = rgb
                if self._ups: self._ups.color = rgb
                if context.area:
                    context.area.header_text_set(f"Hue: {h:.3f}   Sat: {s:.3f}")
                    
            elif self.component == 'X':
                dy = (event.mouse_y - self._init_y) / scale
                v = max(0.0, min(1.0, self._init_hsv[2] + dx))
                s = max(0.0, min(1.0, self._init_hsv[1] + dy))
                c = Color()
                c.hsv = (self._init_hsv[0], s, v)
                rgb = (c.r, c.g, c.b)
                self._brush.color = rgb
                if self._ups: self._ups.color = rgb
                if context.area:
                    context.area.header_text_set(f"Value: {v:.3f}   Sat: {s:.3f}")
                    
            elif self.component == 'U':
                h = (self._init_hsv[0] + dx) % 1.0
                c = Color()
                c.hsv = (h, self._init_hsv[1], self._init_hsv[2])
                rgb = (c.r, c.g, c.b)
                self._brush.color = rgb
                if self._ups: self._ups.color = rgb
                if context.area:
                    context.area.header_text_set(f"Hue: {h:.3f}")
                    
            else:
                idx = 'HSV'.index(self.component)
                applied = self._apply(self._init_hsv[idx] + dx)
                comp_name = {'S': 'Saturation', 'V': 'Value'}[self.component]
                if context.area:
                    context.area.header_text_set(f"{comp_name}: {applied:.3f}")
            
            if context.screen:
                for area in context.screen.areas:
                    area.tag_redraw()
            return {'RUNNING_MODAL'}
            
        elif event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE'} and event.value == 'PRESS':
            self._cleanup(context)
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._brush.color = self._init_color
            if self._ups:
                self._ups.color = self._init_color
            self._cleanup(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _cleanup(self, context):
        context.window.cursor_modal_restore()
        if context.area:
            context.area.header_text_set(None)
        if context.screen:
            for area in context.screen.areas:
                area.tag_redraw()
        if self._draw_handle is not None:
            self._draw_space.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None


class CPIE_OT_brush_color_picker(Operator):
    """Open a persistent color-wheel dialog for the brush color"""
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
        return context.window_manager.invoke_props_dialog(self, width=330)

    def execute(self, context):
        if context.screen:
            for area in context.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}

    def draw(self, context):
        brush = _resolve_path(context, self.brush_path)
        if not brush:
            return
            
        ups_path = self.brush_path.rsplit('.', 1)[0] + '.unified_paint_settings'
        ups = _resolve_path(context, ups_path)
        
        layout = self.layout
        wheel_col = layout.column(align=True)
        wheel_col.scale_y = 2.4
        
        if ups and getattr(ups, "use_unified_color", False):
            wheel_col.template_color_picker(ups, "color", value_slider=True)
            layout.prop(ups, "color", text="")
        else:
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
    if size_owner and getattr(size_owner, "use_locked_size", 'VIEW') == 'SCENE':
        size_prop = "unprojected_radius"

    if brush:
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

    if brush and capabilities:
        for prop, text in sculpt_properties.items():
            if hasattr(capabilities, f"has_{prop}") and getattr(capabilities, f"has_{prop}"):
                if isinstance(text, tuple):
                    text = text[1] if getattr(brush, "sculpt_brush_type", "") in {'BLOB', 'SNAKE_HOOK'} else text[0]
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
        
        brush = getattr(context.tool_settings.sculpt, "brush", None)
        ups = context.tool_settings.sculpt.unified_paint_settings
        
        use_scene_size = False
        if ups.use_unified_size:
            use_scene_size = (getattr(ups, "use_locked_size", 'VIEW') == 'SCENE')
        elif brush:
            use_scene_size = (getattr(brush, "use_locked_size", 'VIEW') == 'SCENE')
            
        size_attr = 'unprojected_size' if use_scene_size else 'size'

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle")
        # SOUTH
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = f'{brush_path}.{size_attr}'
        op.data_path_secondary = f'{ups_path}.{size_attr}'
        op.use_secondary = f'{ups_path}.use_unified_size'
        op.image_id = brush_path
        # NORTH
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
        # EAST
        pie.operator("cpie.brush_color_picker", text="Color Picker", icon='COLOR').brush_path = brush_path
        # SOUTH
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = f'{brush_path}.size'
        op.data_path_secondary = f'{ups_path}.size'
        op.use_secondary = f'{ups_path}.use_unified_size'
        op.image_id = brush_path
        # NORTH
        op = pie.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
        op.data_path_primary = f'{brush_path}.strength'
        op.data_path_secondary = f'{ups_path}.strength'
        op.use_secondary = f'{ups_path}.use_unified_strength'
        op.image_id = brush_path
        
        # NORTH WEST (NW)
        op = pie.operator("cpie.brush_color_hsv", text="Hue", icon='COLOR')
        op.component = 'H'
        op.brush_path = brush_path
        
        # NORTH EAST (NE)
        op = pie.operator("cpie.brush_color_hsv", text="Hue + Sat", icon='COLOR')
        op.component = 'U'
        op.brush_path = brush_path
        
        # SOUTH WEST (SW)
        op = pie.operator("cpie.brush_color_hsv", text="Value", icon='COLOR')
        op.component = 'V'
        op.brush_path = brush_path
        
        # SOUTH EAST (SE)
        op = pie.operator("cpie.brush_color_hsv", text="Value + Sat", icon='COLOR')
        op.component = 'X'
        op.brush_path = brush_path


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
        pie.operator("cpie.brush_color_picker", text="Color Picker", icon='COLOR').brush_path = brush_path
        # SOUTH
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = f'{brush_path}.size'
        op.data_path_secondary = f'{ups_path}.size'
        op.use_secondary = f'{ups_path}.use_unified_size'
        op.image_id = brush_path
        # NORTH
        op = pie.operator("wm.radial_control", text="Brush Strength", icon='SHARPCURVE')
        op.data_path_primary = f'{brush_path}.strength'
        op.data_path_secondary = f'{ups_path}.strength'
        op.use_secondary = f'{ups_path}.use_unified_strength'
        op.image_id = brush_path
        
        # NORTH WEST (NW)
        op = pie.operator("cpie.brush_color_hsv", text="Hue", icon='COLOR')
        op.component = 'H'
        op.brush_path = brush_path
        
        # NORTH EAST (NE)
        op = pie.operator("cpie.brush_color_hsv", text="Hue + Sat", icon='COLOR')
        op.component = 'U'
        op.brush_path = brush_path
        
        # SOUTH WEST (SW)
        op = pie.operator("cpie.brush_color_hsv", text="Value", icon='COLOR')
        op.component = 'V'
        op.brush_path = brush_path
        
        # SOUTH EAST (SE)
        op = pie.operator("cpie.brush_color_hsv", text="Value + Sat", icon='COLOR')
        op.component = 'X'
        op.brush_path = brush_path



class CPIE_MT_mode_weightpaint(Menu):
    bl_idname = "CPIE_MT_mode_weightpaint"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        paint_path = 'tool_settings.weight_paint'
        brush_path = f'{paint_path}.brush'
        ups_path = f'{paint_path}.unified_paint_settings'

        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        op = pie.operator("wm.radial_control", text="Brush Weight", icon='SHARPCURVE')
        op.data_path_primary = f'{brush_path}.weight'
        op.data_path_secondary = f'{ups_path}.weight'
        op.use_secondary = f'{ups_path}.use_unified_weight'
        op.image_id = brush_path
        # SOUTH
        op = pie.operator("wm.radial_control", text="Brush Size", icon='BRUSH_DATA')
        op.data_path_primary = f'{brush_path}.size'
        op.data_path_secondary = f'{ups_path}.size'
        op.use_secondary = f'{ups_path}.use_unified_size'
        op.image_id = brush_path
        # NORTH
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