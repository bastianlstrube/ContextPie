# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _brush_path(context):
    """Return ('tool_settings.sculpt' | 'tool_settings.image_paint', brush) for the active paint mode."""
    if context.mode == 'SCULPT':
        return 'tool_settings.sculpt', context.tool_settings.sculpt.brush
    if context.mode == 'PAINT_TEXTURE':
        return 'tool_settings.image_paint', context.tool_settings.image_paint.brush
    return None, None


def _radial(layout, text, primary, *, secondary=None, use_secondary=None,
            rotation=None, image_id=None, icon='NONE'):
    """Drop into Blender's drag-to-set modal (wm.radial_control)."""
    op = layout.operator("wm.radial_control", text=text, icon=icon)
    op.data_path_primary = primary
    if secondary:
        op.data_path_secondary = secondary
    if use_secondary:
        op.use_secondary = use_secondary
    if rotation:
        op.rotation_path = rotation
    if image_id:
        op.image_id = image_id
    return op


# ----------------------------------------------------------------------------
# Sub pies — shared between Sculpt and Texture Paint
# ----------------------------------------------------------------------------

class SUBPIE_MT_brush_falloff(Menu):
    bl_idname = "SUBPIE_MT_brush_falloff"
    bl_label = "Falloff"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        ts_path, brush = _brush_path(context)
        if brush is None:
            return

        # Cluster around WEST (parent slot)
        # WEST
        pie.prop_enum(brush, "curve_distance_falloff_preset", value='SMOOTH')
        # EAST
        pie.separator()
        # SOUTH
        pie.prop_enum(brush, "curve_distance_falloff_preset", value='SHARP')
        # NORTH
        pie.prop_enum(brush, "curve_distance_falloff_preset", value='ROOT')
        # NORTH-WEST
        pie.prop_enum(brush, "curve_distance_falloff_preset", value='SPHERE')
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.prop_enum(brush, "curve_distance_falloff_preset", value='POW4')
        # SOUTH-EAST
        pie.prop_enum(brush, "curve_distance_falloff_preset", value='CONSTANT')


class SUBPIE_MT_brush_stroke(Menu):
    bl_idname = "SUBPIE_MT_brush_stroke"
    bl_label = "Stroke"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        _, brush = _brush_path(context)
        if brush is None:
            return

        # Cluster around EAST (parent slot)
        # WEST
        pie.separator()
        # EAST
        pie.prop_enum(brush, "stroke_method", value='SPACE')
        # SOUTH
        pie.prop_enum(brush, "stroke_method", value='AIRBRUSH')
        # NORTH
        pie.prop_enum(brush, "stroke_method", value='DOTS')
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.prop_enum(brush, "stroke_method", value='DRAG_DOT')
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.prop_enum(brush, "stroke_method", value='ANCHORED')


class SUBPIE_MT_brush_symmetry(Menu):
    bl_idname = "SUBPIE_MT_brush_symmetry"
    bl_label = "Symmetry"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # The Paint base struct holds use_symmetry_x/y/z for both sculpt & image_paint
        paint = (context.tool_settings.sculpt if context.mode == 'SCULPT'
                 else context.tool_settings.image_paint)

        # WEST
        pie.prop(paint, "use_symmetry_x", text="X Mirror", toggle=True)
        # EAST
        pie.prop(paint, "use_symmetry_z", text="Z Mirror", toggle=True)
        # SOUTH
        pie.prop(paint, "use_symmetry_y", text="Y Mirror", toggle=True)
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_sculpt_remesh(Menu):
    bl_idname = "SUBPIE_MT_sculpt_remesh"
    bl_label = "Remesh / Dyntopo"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("sculpt.dynamic_topology_toggle", text="Toggle Dyntopo", icon='MOD_REMESH')
        # EAST
        pie.operator("object.voxel_remesh", text="Voxel Remesh", icon='MOD_REMESH')
        # SOUTH
        pie.operator("sculpt.symmetrize", text="Symmetrize")
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("object.quadriflow_remesh", text="QuadriFlow")
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_sculpt_automasking(Menu):
    bl_idname = "SUBPIE_MT_sculpt_automasking"
    bl_label = "Auto-Mask"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        sculpt = context.tool_settings.sculpt

        # WEST
        pie.prop(sculpt, "use_automasking_topology", text="Topology", toggle=True)
        # EAST
        pie.prop(sculpt, "use_automasking_face_sets", text="Face Sets", toggle=True)
        # SOUTH
        pie.prop(sculpt, "use_automasking_boundary_edges", text="Mesh Boundary", toggle=True)
        # NORTH
        pie.prop(sculpt, "use_automasking_cavity", text="Cavity", toggle=True)
        # NORTH-WEST
        pie.prop(sculpt, "use_automasking_start_normal", text="Area Normal", toggle=True)
        # NORTH-EAST
        pie.prop(sculpt, "use_automasking_view_normal", text="View Normal", toggle=True)
        # SOUTH-WEST
        pie.prop(sculpt, "use_automasking_boundary_face_sets", text="Face Set Boundary", toggle=True)
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_texture_paint_blend(Menu):
    bl_idname = "SUBPIE_MT_texture_paint_blend"
    bl_label = "Blend"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        _, brush = _brush_path(context)
        if brush is None:
            return

        # WEST
        pie.prop_enum(brush, "blend", value='MIX')
        # EAST
        pie.prop_enum(brush, "blend", value='ERASE_ALPHA')
        # SOUTH
        pie.prop_enum(brush, "blend", value='MUL')
        # NORTH
        pie.prop_enum(brush, "blend", value='ADD')
        # NORTH-WEST
        pie.prop_enum(brush, "blend", value='LIGHTEN')
        # NORTH-EAST
        pie.prop_enum(brush, "blend", value='DARKEN')
        # SOUTH-WEST
        pie.prop_enum(brush, "blend", value='SUB')
        # SOUTH-EAST
        pie.prop_enum(brush, "blend", value='OVERLAY')


class SUBPIE_MT_texture_paint_options(Menu):
    bl_idname = "SUBPIE_MT_texture_paint_options"
    bl_label = "Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        ip = context.tool_settings.image_paint

        # WEST
        pie.prop(ip, "use_occlude", text="Occlude", toggle=True)
        # EAST
        pie.prop(ip, "use_backface_culling", text="Backface Culling", toggle=True)
        # SOUTH
        pie.prop(ip, "use_normal_falloff", text="Normal Falloff", toggle=True)
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


# ----------------------------------------------------------------------------
# Main pivots / tool-settings pie
# ----------------------------------------------------------------------------

class VIEW3D_PIE_MT_pivots(Menu):
    bl_idname = "PIE_MT_context_pivots"
    bl_label = "Pivots Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        if context.mode == 'SCULPT':
            self.draw_sculpt(pie, context)
        elif context.mode == 'PAINT_TEXTURE':
            self.draw_texture_paint(pie, context)
        elif context.mode in ('EDIT_MESH', 'EDIT_CURVE', 'EDIT_LATTICE', 'EDIT_ARMATURE'):
            self.draw_edit(pie, context)
        elif context.mode in ('OBJECT', 'POSE'):
            self.draw_object(pie, context)

    # --- mesh / armature / curve / lattice edit modes ---
    def draw_edit(self, pie, context):
        # WEST
        pie.operator("wm.call_menu_pie", text='Orientation...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_orientations_pie"
        # EAST
        pie.operator("wm.call_menu_pie", text='Pivot...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_pivot_pie"
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Snap...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_snap"
        # NORTH
        pie.operator("wm.call_menu_pie", text='Proportional...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_proportional_edt"
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Set Origin...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_set_origin"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Align...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_mesh_align"
        # SOUTH-EAST
        pie.separator()

    def draw_object(self, pie, context):
        # WEST
        pie.operator("wm.call_menu_pie", text='Orientation...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_orientations_pie"
        # EAST
        pie.operator("wm.call_menu_pie", text='Pivot...', icon='RIGHTARROW_THIN').name = "VIEW3D_MT_pivot_pie"
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Snap...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_snap"
        # NORTH
        pie.operator("wm.call_menu_pie", text='Proportional...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_proportional_obj"
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Set Origin...', icon='RIGHTARROW_THIN').name = "SUBPIE_MT_set_origin"
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()

    # --- sculpt mode tool settings ---
    def draw_sculpt(self, pie, context):
        brush_path = 'tool_settings.sculpt.brush'

        # WEST
        pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = SUBPIE_MT_brush_falloff.bl_idname
        # EAST
        pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = SUBPIE_MT_brush_stroke.bl_idname
        # SOUTH
        pie.separator()
        # NORTH — drag to rotate texture
        _radial(pie, "Texture Angle",
                primary=f'{brush_path}.texture_slot.angle',
                image_id=brush_path, icon='DRIVER_ROTATIONAL_DIFFERENCE')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = SUBPIE_MT_brush_symmetry.bl_idname
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Auto-Mask...', icon='MOD_MASK').name = SUBPIE_MT_sculpt_automasking.bl_idname
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Remesh...', icon='MOD_REMESH').name = SUBPIE_MT_sculpt_remesh.bl_idname
        # SOUTH-EAST
        pie.separator()

    # --- texture paint mode tool settings ---
    def draw_texture_paint(self, pie, context):
        brush_path = 'tool_settings.image_paint.brush'

        # WEST
        pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = SUBPIE_MT_brush_falloff.bl_idname
        # EAST
        pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = SUBPIE_MT_brush_stroke.bl_idname
        # SOUTH
        pie.separator()
        # NORTH — drag to rotate texture
        _radial(pie, "Texture Angle",
                primary=f'{brush_path}.texture_slot.angle',
                image_id=brush_path, icon='DRIVER_ROTATIONAL_DIFFERENCE')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = SUBPIE_MT_brush_symmetry.bl_idname
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Options...', icon='PREFERENCES').name = SUBPIE_MT_texture_paint_options.bl_idname
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Blend...', icon='IMAGE_RGB_ALPHA').name = SUBPIE_MT_texture_paint_blend.bl_idname
        # SOUTH-EAST
        pie.separator()


registry = [
    SUBPIE_MT_brush_falloff,
    SUBPIE_MT_brush_stroke,
    SUBPIE_MT_brush_symmetry,
    SUBPIE_MT_sculpt_remesh,
    SUBPIE_MT_sculpt_automasking,
    SUBPIE_MT_texture_paint_blend,
    SUBPIE_MT_texture_paint_options,
    VIEW3D_PIE_MT_pivots,
]


def register():
    for keymap_name in ("3D View", "Sculpt", "Image Paint"):
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=VIEW3D_PIE_MT_pivots.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
            keymap_name=keymap_name,
        )
