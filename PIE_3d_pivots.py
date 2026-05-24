# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu
from mathutils import Matrix

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

_PAINT_TS_PATH = {
    'SCULPT':        'tool_settings.sculpt',
    'PAINT_TEXTURE': 'tool_settings.image_paint',
    'PAINT_VERTEX':  'tool_settings.vertex_paint',
    'PAINT_WEIGHT':  'tool_settings.weight_paint',
}


def _brush_path(context):
    """Return (paint-settings path, brush) for the active paint mode, or (None, None)."""
    ts_path = _PAINT_TS_PATH.get(context.mode)
    if not ts_path:
        return None, None
    paint = getattr(context.tool_settings, ts_path.rsplit('.', 1)[-1], None)
    return ts_path, (paint.brush if paint else None)


def _active_paint(context):
    """Return the active Paint settings struct for paint modes, else None."""
    ts_path = _PAINT_TS_PATH.get(context.mode)
    if not ts_path:
        return None
    return getattr(context.tool_settings, ts_path.rsplit('.', 1)[-1], None)


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
#                               OPERATORS
# ----------------------------------------------------------------------------

class CPIE_OT_copy_gizmo_to_cursor(bpy.types.Operator):
    """Copy the current transform gizmo orientation to the 3D Cursor"""
    bl_idname = "view3d.copy_gizmo_to_cursor"
    bl_label = "Gizmo Orientation to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def execute(self, context):
        slot = context.scene.transform_orientation_slots[0]
        orient_type = slot.type
        mat_3x3 = Matrix.Identity(3)
        
        # 1. Evaluate Built-in Orientations
        if orient_type == 'GLOBAL':
            mat_3x3 = Matrix.Identity(3)
            
        elif orient_type == 'LOCAL':
            if context.active_object:
                mat_3x3 = context.active_object.matrix_world.to_3x3().normalized()
                
        elif orient_type == 'PARENT':
            if context.active_object and context.active_object.parent:
                mat_3x3 = context.active_object.parent.matrix_world.to_3x3().normalized()
                
        elif orient_type == 'VIEW':
            rv3d = context.region_data
            if rv3d:
                # Invert the view matrix to get world-space camera/view vectors
                mat_3x3 = rv3d.view_matrix.to_3x3().inverted().normalized()
                
        elif orient_type == 'CURSOR':
            self.report({'INFO'}, "Orientation is already set to Cursor.")
            return {'FINISHED'}
            
        elif orient_type in {'NORMAL', 'GIMBAL'}:
            # For dynamic selections like Normal/Gimbal, let Blender generate a 
            # temporary custom orientation from the active context to catch its matrix.
            try:
                old_type = slot.type
                bpy.ops.transform.create_orientation(name="TEMP_GIZMO_ORIENT", use=True, overwrite=True)
                mat_3x3 = slot.custom_orientation.matrix.copy()
                bpy.ops.transform.delete_orientation()
                slot.type = old_type
            except Exception as e:
                self.report({'WARNING'}, f"Could not determine selection orientation: {e}")
                if context.active_object:
                    mat_3x3 = context.active_object.matrix_world.to_3x3().normalized()
        
        else:
            # 2. Handle Existing Custom Orientations
            if slot.custom_orientation:
                mat_3x3 = slot.custom_orientation.matrix.copy()
            else:
                self.report({'WARNING'}, "Custom orientation matrix not found. Falling back to Global.")

        # 3. Apply the 3x3 Rotation Matrix to the 4x4 Cursor Matrix
        cursor = context.scene.cursor
        cursor_loc = cursor.location.copy()
        
        # Build 4x4 matrix from 3x3 rotation and re-insert the original location
        new_cursor_matrix = mat_3x3.to_4x4()
        new_cursor_matrix.translation = cursor_loc
        
        cursor.matrix = new_cursor_matrix
        
        self.report({'INFO'}, f"Copied '{orient_type}' orientation to 3D Cursor.")
        return {'FINISHED'}


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

        # All paint modes' base struct holds use_symmetry_x/y/z
        paint = _active_paint(context)
        if paint is None:
            return

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

        obj = context.object
        mesh = obj.data if obj and obj.type == 'MESH' else None

        # WEST
        pie.operator("sculpt.dynamic_topology_toggle", text="Toggle Dyntopo", icon='MOD_REMESH')
        # EAST
        pie.operator("object.voxel_remesh", text="Voxel Remesh", icon='MOD_REMESH')
        # SOUTH
        pie.operator("sculpt.symmetrize", text="Symmetrize")
        # NORTH — drag to set voxel size for next Voxel Remesh
        if mesh and hasattr(mesh, "remesh_voxel_size"):
            _radial(pie, "Voxel Size",
                    primary='object.data.remesh_voxel_size',
                    icon='MESH_GRID')
        else:
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
        brush = sculpt.brush

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
        # SOUTH-EAST — sibling constraint: brush only affects front faces
        if brush and hasattr(brush, "use_frontface"):
            pie.prop(brush, "use_frontface", text="Front Face Only", toggle=True)
        else:
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
        brush = ip.brush

        # WEST
        pie.prop(ip, "use_occlude", text="Occlude", toggle=True)
        # EAST
        pie.prop(ip, "use_backface_culling", text="Backface Culling", toggle=True)
        # SOUTH
        pie.prop(ip, "use_normal_falloff", text="Normal Falloff", toggle=True)
        # NORTH — accumulate (additive stroke building)
        if brush and hasattr(brush, "use_accumulate"):
            pie.prop(brush, "use_accumulate", text="Accumulate", toggle=True)
        else:
            pie.separator()
        # NORTH-WEST — only paint front faces
        if brush and hasattr(brush, "use_frontface"):
            pie.prop(brush, "use_frontface", text="Front Face Only", toggle=True)
        else:
            pie.separator()
        # NORTH-EAST
        if hasattr(ip, "tile_x"):
            pie.prop(ip, "tile_x", text="Tile X", toggle=True)
        else:
            pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        if hasattr(ip, "tile_y"):
            pie.prop(ip, "tile_y", text="Tile Y", toggle=True)
        else:
            pie.separator()


class SUBPIE_MT_brush_mapping(Menu):
    bl_idname = "SUBPIE_MT_brush_mapping"
    bl_label = "Texture Mapping"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        _, brush = _brush_path(context)
        ts = getattr(brush, "texture_slot", None) if brush else None
        prop = ts.bl_rna.properties.get('map_mode') if ts else None
        if prop is None or prop.type != 'ENUM':
            # Render an inert placeholder pie so the menu doesn't blank out.
            for _i in range(8):
                pie.separator()
            return
        available = {e.identifier for e in prop.enum_items}

        def slot(value):
            if value in available:
                pie.prop_enum(ts, "map_mode", value=value)
            else:
                pie.separator()

        # Mode-agnostic layout; mild cluster toward the lower hemisphere
        # since the parent slot is S (sculpt) or SW (tex/vertex paint).
        # WEST
        slot('RANDOM')
        # EAST
        slot('STENCIL')
        # SOUTH — primary, most common
        slot('VIEW_PLANE')
        # NORTH
        slot('3D')
        # NORTH-WEST
        slot('AREA_PLANE')
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        slot('TILED')
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_vertex_paint_options(Menu):
    bl_idname = "SUBPIE_MT_vertex_paint_options"
    bl_label = "Vertex Paint Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        _, brush = _brush_path(context)

        # WEST
        if brush and hasattr(brush, "use_frontface"):
            pie.prop(brush, "use_frontface", text="Front Face Only", toggle=True)
        else:
            pie.separator()
        # EAST
        if brush and hasattr(brush, "use_accumulate"):
            pie.prop(brush, "use_accumulate", text="Accumulate", toggle=True)
        else:
            pie.separator()
        # SOUTH
        if brush and hasattr(brush, "use_alpha"):
            pie.prop(brush, "use_alpha", text="Affect Alpha", toggle=True)
        else:
            pie.separator()
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


class SUBPIE_MT_weight_paint_options(Menu):
    bl_idname = "SUBPIE_MT_weight_paint_options"
    bl_label = "Weight Paint Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        wp = context.tool_settings.weight_paint
        obj = context.object
        mesh = obj.data if obj and obj.type == 'MESH' else None

        # WEST
        pie.prop(wp, "use_multipaint", text="Multi-Paint", toggle=True)
        # EAST
        pie.prop(wp, "use_auto_normalize", text="Auto-Normalize", toggle=True)
        # SOUTH
        if mesh is not None and hasattr(mesh, "use_mirror_x"):
            pie.prop(mesh, "use_mirror_x", text="Vertex Group X-Mirror", toggle=True)
        else:
            pie.separator()
        # NORTH
        pie.prop(wp, "use_lock_relative", text="Lock Relative", toggle=True)
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        if hasattr(wp, "use_group_restrict"):
            pie.prop(wp, "use_group_restrict", text="Restrict to Group", toggle=True)
        else:
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

        _GP_MODES = frozenset({
            'EDIT_GPENCIL', 'EDIT_GREASE_PENCIL',
            'PAINT_GREASE_PENCIL', 'PAINT_GPENCIL',
            'SCULPT_GREASE_PENCIL', 'SCULPT_GPENCIL',
        })

        if context.mode in _GP_MODES:
            from .PIE_greasepencil_pivots import draw_gp_pivots_pie
            draw_gp_pivots_pie(pie, context)
        elif context.mode == 'SCULPT':
            self.draw_sculpt(pie, context)
        elif context.mode == 'PAINT_TEXTURE':
            self.draw_texture_paint(pie, context)
        elif context.mode == 'PAINT_VERTEX':
            self.draw_vertex_paint(pie, context)
        elif context.mode == 'PAINT_WEIGHT':
            self.draw_weight_paint(pie, context)
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
        pie.operator("view3d.copy_gizmo_to_cursor", text='Orient Cursor to Gizmo', icon='ORIENTATION_CURSOR')
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
        pie.operator("view3d.copy_gizmo_to_cursor", text='Orient Cursor to Gizmo', icon='ORIENTATION_CURSOR')
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
        # SOUTH — texture mapping mode sub-pie
        pie.operator("wm.call_menu_pie", text='Mapping...', icon='TEXTURE').name = SUBPIE_MT_brush_mapping.bl_idname
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
        # SOUTH-EAST — drag to set brush spacing
        _radial(pie, "Spacing",
                primary=f'{brush_path}.spacing',
                image_id=brush_path, icon='DRIVER_DISTANCE')

    # --- texture paint mode tool settings ---
    def draw_texture_paint(self, pie, context):
        brush_path = 'tool_settings.image_paint.brush'

        # WEST
        pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = SUBPIE_MT_brush_falloff.bl_idname
        # EAST
        pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = SUBPIE_MT_brush_stroke.bl_idname
        # SOUTH — brush-behavior cardinal (was at SW; promoted to S)
        pie.operator("wm.call_menu_pie", text='Blend...', icon='IMAGE_RGB_ALPHA').name = SUBPIE_MT_texture_paint_blend.bl_idname
        # NORTH — drag to rotate texture
        _radial(pie, "Texture Angle",
                primary=f'{brush_path}.texture_slot.angle',
                image_id=brush_path, icon='DRIVER_ROTATIONAL_DIFFERENCE')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = SUBPIE_MT_brush_symmetry.bl_idname
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Options...', icon='PREFERENCES').name = SUBPIE_MT_texture_paint_options.bl_idname
        # SOUTH-WEST — texture mapping mode sub-pie
        pie.operator("wm.call_menu_pie", text='Mapping...', icon='TEXTURE').name = SUBPIE_MT_brush_mapping.bl_idname
        # SOUTH-EAST — drag to set brush spacing
        _radial(pie, "Spacing",
                primary=f'{brush_path}.spacing',
                image_id=brush_path, icon='DRIVER_DISTANCE')

    # --- vertex paint mode tool settings ---
    def draw_vertex_paint(self, pie, context):
        brush_path = 'tool_settings.vertex_paint.brush'

        # WEST
        pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = SUBPIE_MT_brush_falloff.bl_idname
        # EAST
        pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = SUBPIE_MT_brush_stroke.bl_idname
        # SOUTH — brush-behavior cardinal
        pie.operator("wm.call_menu_pie", text='Blend...', icon='IMAGE_RGB_ALPHA').name = SUBPIE_MT_texture_paint_blend.bl_idname
        # NORTH — drag to rotate texture
        _radial(pie, "Texture Angle",
                primary=f'{brush_path}.texture_slot.angle',
                image_id=brush_path, icon='DRIVER_ROTATIONAL_DIFFERENCE')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = SUBPIE_MT_brush_symmetry.bl_idname
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Options...', icon='PREFERENCES').name = SUBPIE_MT_vertex_paint_options.bl_idname
        # SOUTH-WEST — texture mapping mode sub-pie
        pie.operator("wm.call_menu_pie", text='Mapping...', icon='TEXTURE').name = SUBPIE_MT_brush_mapping.bl_idname
        # SOUTH-EAST — drag to set brush spacing
        _radial(pie, "Spacing",
                primary=f'{brush_path}.spacing',
                image_id=brush_path, icon='DRIVER_DISTANCE')

    # --- weight paint mode tool settings ---
    def draw_weight_paint(self, pie, context):
        brush_path = 'tool_settings.weight_paint.brush'

        # WEST
        pie.operator("wm.call_menu_pie", text='Falloff...', icon='SMOOTHCURVE').name = SUBPIE_MT_brush_falloff.bl_idname
        # EAST
        pie.operator("wm.call_menu_pie", text='Stroke...', icon='IPO_LINEAR').name = SUBPIE_MT_brush_stroke.bl_idname
        # SOUTH — brush-behavior cardinal
        pie.operator("wm.call_menu_pie", text='Blend...', icon='IMAGE_RGB_ALPHA').name = SUBPIE_MT_texture_paint_blend.bl_idname
        # NORTH — drag to set brush spacing (weight brushes have no texture)
        _radial(pie, "Spacing",
                primary=f'{brush_path}.spacing',
                image_id=brush_path, icon='DRIVER_DISTANCE')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Symmetry...', icon='MOD_MIRROR').name = SUBPIE_MT_brush_symmetry.bl_idname
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Options...', icon='PREFERENCES').name = SUBPIE_MT_weight_paint_options.bl_idname
        # SOUTH-WEST — eyedropper-style sample of weight under cursor
        pie.operator("paint.weight_sample", text='Sample Weight', icon='EYEDROPPER')
        # SOUTH-EAST — smooth weights on the active vertex group
        pie.operator("object.vertex_group_smooth", text='Smooth Weights', icon='MOD_SMOOTH')


registry = [
    CPIE_OT_copy_gizmo_to_cursor,
    SUBPIE_MT_brush_falloff,
    SUBPIE_MT_brush_stroke,
    SUBPIE_MT_brush_symmetry,
    SUBPIE_MT_sculpt_remesh,
    SUBPIE_MT_sculpt_automasking,
    SUBPIE_MT_texture_paint_blend,
    SUBPIE_MT_texture_paint_options,
    SUBPIE_MT_weight_paint_options,
    SUBPIE_MT_brush_mapping,
    SUBPIE_MT_vertex_paint_options,
    VIEW3D_PIE_MT_pivots,
]


def register():
    for keymap_name in ("3D View",):
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=VIEW3D_PIE_MT_pivots.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
            keymap_name=keymap_name,
        )
