# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path

import bpy
from bpy.types import Menu
from bl_ui.properties_paint_common import BrushAssetShelf

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# CUSTOM OPERATORS ######################################################################

class SetKnifeTool(bpy.types.Operator):
    bl_idname = "mesh.set_knife_tool"
    bl_label = "Knife Tool"
    bl_description = "Activate the Knife tool, for one operation or as active tool"

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        if addon_prefs.persistent_tools:
            bpy.ops.wm.tool_set_by_id(name="builtin.knife")
        else:
            bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
        return {'FINISHED'}

class SetLoopCutTool(bpy.types.Operator):
    bl_idname = "mesh.set_loopcut_tool"
    bl_label = "Loop Cut'n'Slide Tool"
    bl_description = "Activate the Loop Cut'n'Slide Tool, for one operation or as active tool"

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        if addon_prefs.persistent_tools:
            bpy.ops.wm.tool_set_by_id(name="builtin.loop_cut")
        else:
            bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')
        return {'FINISHED'}

class CURVE_OT_clear_radius(bpy.types.Operator):
    """Reset the radius of selected control points to 1.0"""
    bl_idname = "curve.clear_radius"
    bl_label = "Clear Radius"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.mode == 'EDIT_CURVE' and
                context.active_object.type == 'CURVE')

    def execute(self, context):
        selected_curves = [obj for obj in context.selected_editable_objects if obj.type == 'CURVE']
        points_changed = 0

        if not selected_curves:
            self.report({'WARNING'}, "No curve objects selected in Edit Mode.")
            return {'CANCELLED'}

        for obj in selected_curves:
            curve_data = obj.data
            if curve_data and hasattr(curve_data, 'splines'):
                for spline in curve_data.splines:
                    if spline.type == 'BEZIER':
                        for point in spline.bezier_points:
                            if point.select_control_point or point.select_left_handle or point.select_right_handle:
                                point.radius = 1.0
                                points_changed += 1
                    elif spline.type in ['NURBS', 'POLY']:
                        for point in spline.points:
                            if point.select:
                                point.radius = 1.0
                                points_changed += 1

        if points_changed > 0:
            self.report({'INFO'}, f"Reset radius for {points_changed} selected control point(s).")
        else:
            self.report({'INFO'}, "No control points were selected.")
        return {'FINISHED'}


# MESH SUB MENUS ######################################################################

class SUBPIE_MT_merge(Menu):
    bl_label = "Merge"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("mesh.merge", text='Cursor').type = 'CURSOR'
        pie.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'
        pie.separator()
        pie.operator("mesh.merge", text='Center').type = 'CENTER'
        pie.operator("mesh.unsubdivide")
        pie.operator("mesh.remove_doubles", text="By Distance")

        try:
            pie.operator("mesh.merge", text='First').type = 'FIRST'
            pie.operator("mesh.merge", text='Last').type = 'LAST'
        except TypeError:
            pie.separator()
            pie.separator()

class SUBPIE_MT_connect(Menu):
    bl_label = "Connect"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.separator()
        pie.operator("mesh.bridge_edge_loops", text="Bridge")
        pie.operator("mesh.fill_grid", text="Grid Fill Loop")
        pie.operator("mesh.vert_connect_path", text="Cut Vert Path")
        pie.operator("mesh.vert_connect", text="Cut Connect")
        pie.operator("mesh.edge_face_add", text="Add Edge/Face")
        pie.separator()
        pie.operator("mesh.fill", text="Fill Loop")

class SUBPIE_MT_edit_mesh_looptools(Menu):
    bl_label = "LoopTools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("mesh.looptools_gstretch")
        pie.operator("mesh.looptools_bridge", text="Bridge").loft = False
        pie.operator("mesh.looptools_circle")
        pie.operator("mesh.looptools_flatten")
        pie.operator("mesh.looptools_curve")
        pie.operator("mesh.looptools_bridge", text="Loft").loft = True
        pie.operator("mesh.looptools_relax")
        pie.operator("mesh.looptools_space")

class SUBPIE_MT_divide(Menu):
    bl_label = "Divide"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode

        if is_vert_mode:
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            pie.operator("mesh.subdivide", text='Subdivide')
            pie.operator("mesh.rip_move")
            pie.operator("mesh.poke")
            pie.separator()
            pie.operator("mesh.bevel", text='Bevel').affect = 'VERTICES'
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            pie.separator()
        elif is_edge_mode:
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            pie.operator("mesh.subdivide", text='Subdivide')
            pie.operator("mesh.rip_move")
            pie.operator("mesh.poke")
            pie.separator()
            pie.operator("mesh.bevel", text='Bevel').affect = 'EDGES'
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            pie.operator("mesh.edge_split")
        elif is_face_mode:
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            pie.operator("mesh.bevel", text='Bevel')
            pie.operator("mesh.rip_move")
            pie.operator("mesh.poke")
            pie.separator()
            pie.operator("mesh.subdivide", text='Subdivide')
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            pie.operator("mesh.split")

class SUBPIE_MT_extrudeFaces(Menu):
    bl_label = "Extrude Faces"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("mesh.inset", text="Inset").use_individual = False
        pie.operator("mesh.extrude_faces_move", text="Extrude Individual")
        pie.operator("view3d.edit_mesh_extrude_move_shrink_fatten", text="Extrude Along Normals")
        pie.operator("mesh.solidify")
        pie.operator("mesh.inset", text="Inset Individual").use_individual = True
        pie.operator("mesh.wireframe")
        pie.operator("wm.tool_set_by_id", text="Extrude To Cursor Tool").name = "builtin.extrude_to_cursor"
        pie.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude")

class SUBPIE_MT_PieDelete(Menu):
    bl_label = "Pie Delete"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        box = pie.split().column()
        box.operator("mesh.dissolve_limited", text="Limited Dissolve", icon='STICKY_UVS_LOC')
        box.operator("mesh.delete_edgeloop", text="Delete Edge Loops", icon='NONE')
        box.operator("mesh.edge_collapse", text="Edge Collapse", icon='UV_EDGESEL')

        box = pie.split().column()
        box.operator("mesh.remove_doubles", text="Merge By Distance", icon='NONE')
        box.operator("mesh.delete", text="Only Edge & Faces", icon='NONE').type = 'EDGE_FACE'
        box.operator("mesh.delete", text="Only Faces", icon='UV_FACESEL').type = 'ONLY_FACE'

        pie.operator("mesh.dissolve_edges", text="Dissolve Edges", icon='SNAP_EDGE')
        pie.operator("mesh.delete", text="Delete Edges", icon='EDGESEL').type = 'EDGE'
        pie.operator("mesh.delete", text="Delete Vertices", icon='VERTEXSEL').type = 'VERT'
        pie.operator("mesh.delete", text="Delete Faces", icon='FACESEL').type = 'FACE'
        pie.operator("mesh.dissolve_verts", text="Dissolve Vertices", icon='SNAP_VERTEX')
        pie.operator("mesh.dissolve_faces", text="Dissolve Faces", icon='SNAP_FACE')

class SUBPIE_MT_smoothCurve(Menu):
    bl_label = "Smooth"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("curve.normals_make_consistent")
        pie.operator("curve.smooth")
        pie.operator("curve.smooth_radius")
        pie.operator("curve.smooth_tilt")
        pie.operator("curve.smooth_weight")
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_curveDelete(Menu):
    bl_label = "Delete/Clear"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("curve.dissolve_verts")
        pie.separator()
        pie.operator("curve.delete", text="Delete Segment").type = 'SEGMENT'
        pie.operator("curve.tilt_clear")
        pie.separator()
        pie.operator("curve.clear_radius")
        pie.operator("curve.delete", text="Delete Vert").type = 'VERT'
        pie.separator()


# OBJECT MODE SUB MENUS ######################################################################

class SUBPIE_MT_parent(Menu):
    bl_label = "Parent"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator('object.make_links_data', text='Link Collections').type = 'GROUPS'
        pie.operator('object.make_links_data', text='Link Instance Collection').type = 'DUPLICOLLECTION'
        pie.operator('object.make_links_data', text='Link Material').type = 'MATERIAL'
        pie.separator()                         # NORTH
        pie.operator("object.parent_set")       # NE
        pie.operator("object.parent_clear")     # NW
        pie.operator('object.make_links_data', text='Link Animation Data').type = 'ANIMATION'
        pie.operator('object.make_links_data', text='Link Object Data').type = 'OBDATA'

class SUBPIE_MT_convert(Menu):
    bl_label = "Convert"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        pie.operator_enum("object.convert", "target")

class SUBPIE_MT_joinMeshes(Menu):
    bl_label = "Join/Boolean"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        has_bool_tool = any(name.endswith("bool_tool") for name in bpy.context.preferences.addons.keys())

        if has_bool_tool:
            pie.operator("object.boolean_brush_difference", text="Difference", icon='SELECT_SUBTRACT')
            pie.operator("object.boolean_brush_union", text="Union", icon='SELECT_EXTEND')
            pie.operator("object.boolean_brush_intersect", text="Intersect", icon='SELECT_INTERSECT')
            pie.operator("object.join")
            sub = pie.operator("object.join_modifier")
            sub.use_collections = False
            sub.name_source = 'ACTIVE_OBJECT'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            sub = pie.operator("object.join_modifier", text="Join Parent Collections")
            sub.use_collections = True
            sub.inherit_name = True
            sub.name_source = 'PARENT_COLLECTION'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            pie.operator("object.boolean_brush_slice", text="Slice", icon='SELECT_DIFFERENCE')
            pie.separator()
        else:
            pie.operator("object.add_pie_boolean", text="Difference", icon='SELECT_SUBTRACT').boolean_type = 'DIFFERENCE'
            pie.operator("object.add_pie_boolean", text="Union", icon='SELECT_EXTEND').boolean_type = 'UNION'
            pie.operator("object.add_pie_boolean", text="Intersect", icon='SELECT_INTERSECT').boolean_type = 'INTERSECT'
            pie.operator("object.join")
            sub = pie.operator("object.join_modifier")
            sub.use_collections = False
            sub.name_source = 'ACTIVE_OBJECT'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            sub = pie.operator("object.join_modifier", text="Join Parent Collections")
            sub.use_collections = True
            sub.inherit_name = True
            sub.name_source = 'PARENT_COLLECTION'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            pie.separator()
            pie.separator()

class SUBPIE_MT_addMeshInteractive(Menu):
    bl_label = "Add Mesh Interactively"

    def draw(self, context):
        pie = self.layout.menu_pie()

        pie.operator("wm.tool_set_by_id", text="Cube", icon='MESH_CUBE').name = "builtin.primitive_cube_add"
        pie.operator("wm.tool_set_by_id", text="Cone", icon='MESH_CONE').name = "builtin.primitive_cone_add"
        pie.operator("wm.tool_set_by_id", text="Cylinder", icon='MESH_CYLINDER').name = "builtin.primitive_cylinder_add"
        pie.operator("wm.tool_set_by_id", text="UV Sphere", icon='MESH_UVSPHERE').name = "builtin.primitive_uv_sphere_add"
        pie.operator("wm.tool_set_by_id", text="Ico Sphere", icon='MESH_ICOSPHERE').name = "builtin.primitive_ico_sphere_add"
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_applyTransform(Menu):
    bl_label = "Apply"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        op = pie.operator("object.transform_apply", text="Location")
        op.location, op.rotation, op.scale = True, False, False
        op = pie.operator("object.transform_apply", text="Scale")
        op.location, op.rotation, op.scale = False, False, True
        op = pie.operator("object.transform_apply", text="Rotation")
        op.location, op.rotation, op.scale = False, True, False
        op = pie.operator("object.transform_apply", text="All Transforms")
        op.location, op.rotation, op.scale = True, True, True
        pie.separator()
        pie.operator("object.convert", text="Visual Geo to Mesh").target = 'MESH'
        pie.separator()
        pie.separator()

class SUBPIE_MT_shadeObject(Menu):
    bl_label = "Shade/Display"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("object.shade_smooth")
        pie.operator("object.edit_display_type", text="Solid", icon='SHADING_SOLID').display_type = 'SOLID'
        pie.operator("object.edit_obj_color", text="Set Object Colour")
        pie.operator("object.edit_display_type", text="Bounding Box", icon='CUBE').display_type = 'BOUNDS'
        pie.operator("object.shade_auto_smooth")
        pie.operator("object.edit_display_type", text="Wireframe", icon='SHADING_WIRE').display_type = 'WIRE'
        pie.operator("object.shade_flat")
        pie.operator("object.edit_display_type", text="Textured", icon='SHADING_TEXTURE').display_type = 'TEXTURED'

class SUBPIE_MT_LinkTransfer(Menu):
    bl_label = "Link"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("wm.call_menu_pie", text='Copy/Transfer...').name = "SUBPIE_MT_CopyTransfer"
        pie.operator('object.make_links_data', text='Link Material').type = 'MATERIAL'
        pie.operator('object.make_links_data', text='Link Animation Data').type = 'ANIMATION'
        pie.operator('object.make_links_data', text='Link Collections').type = 'GROUPS'
        pie.operator('object.make_links_data', text='Link Instance Collection').type = 'DUPLICOLLECTION'
        pie.operator('object.make_links_data', text='Link Object Data').type = 'OBDATA'
        pie.separator()
        pie.separator()

class SUBPIE_MT_CopyTransfer(Menu):
    bl_label = "Copy/Transfer"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator('object.data_transfer')
        pie.operator('object.constraints_copy', text='Copy Constraints')
        pie.operator('object.join_uvs', text='Copy UV Maps')
        pie.separator()
        pie.operator('object.make_links_data', text='Copy Grease Pencil FX').type = 'EFFECTS'
        pie.operator('object.modifiers_copy_to_selected', text='Copy Modifiers')
        pie.operator('object.datalayout_transfer')
        pie.separator()


# POSE MODE SUB MENUS ######################################################################

class SUBPIE_MT_inbetweens(Menu):
    bl_label = "Inbetweens"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("pose.push_rest")
        pie.operator("pose.relax_rest")
        pie.operator("pose.blend_to_neighbor")
        pie.operator("pose.breakdown")
        pie.separator()
        pie.separator()
        pie.operator("pose.push")
        pie.operator("pose.relax")

class SUBPIE_MT_propagate(Menu):
    bl_label = "Propagate"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator("pose.propagate", text="Selected Markers").mode = 'SELECTED_MARKERS'
        pie.operator("pose.propagate", text="Selected Keys").mode = 'SELECTED_KEYS'
        pie.operator("pose.propagate", text="Last Key").mode = 'LAST_KEY'
        pie.operator("pose.propagate", text="Next Key").mode = 'NEXT_KEY'
        pie.operator("pose.propagate", text="Before Frame").mode = 'BEFORE_FRAME'
        pie.operator("pose.propagate", text="Before End").mode = 'BEFORE_END'
        pie.separator()
        pie.separator()

class SUBPIE_MT_constraints(Menu):
    bl_label = "Constraints"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.separator()
        pie.separator()
        pie.operator("pose.constraints_clear", text="Clear Constraints")
        pie.operator("pose.constraint_add_with_targets", text="Constraint with targets")
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_ik(Menu):
    bl_label = "IK"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.separator()
        pie.separator()
        pie.operator("pose.ik_clear", text="Clear IK")
        pie.operator("pose.ik_add", text="Add IK")
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_motionpaths(Menu):
    bl_label = "Motion Paths"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.separator()
        pie.separator()
        pie.operator("pose.paths_clear")
        calc = pie.operator("pose.paths_calculate")
        calc.start_frame = context.scene.frame_start
        calc.end_frame = context.scene.frame_end
        calc.bake_location = 'HEADS'
        pie.operator("pose.paths_update_visible")
        pie.operator("pose.paths_update")
        pie.separator()
        pie.separator()


# SCULPT BRUSH SUB MENUS ######################################################################

class SUBPIE_MT_sculpt_brush_select_contrast(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_contrast"
    bl_label = "Contrast Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Flatten/Contrast', 'flatten')
        draw_brush_operator(pie, 'Scrape/Fill', 'scrape')
        draw_brush_operator(pie, 'Fill/Deepen', 'fill')
        draw_brush_operator(pie, 'Scrape Multiplane', 'multiplane_scrape')
        pie.separator()
        pie.separator()
        draw_brush_operator(pie, 'Smooth', 'smooth')

class SUBPIE_MT_sculpt_brush_select_transform(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_transform"
    bl_label = "Transform Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Elastic Grab', 'elastic_deform')
        draw_brush_operator(pie, 'Nudge', 'nudge')
        draw_brush_operator(pie, 'Relax Slide', 'topology')
        draw_brush_operator(pie, 'Snake Hook', 'snake_hook')
        draw_brush_operator(pie, 'Twist', 'rotate')
        draw_brush_operator(pie, 'Pose', 'pose')
        draw_brush_operator(pie, 'Pinch/Magnify', 'pinch')
        draw_brush_operator(pie, 'Thumb', 'thumb')

class SUBPIE_MT_sculpt_brush_select_volume(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_volume"
    bl_label = "Volume Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Blob', 'blob')
        draw_brush_operator(pie, 'Clay', 'clay')
        draw_brush_operator(pie, 'Inflate/Deflate', 'inflate')
        draw_brush_operator(pie, 'Draw Sharp', 'draw_sharp')
        draw_brush_operator(pie, 'Clay Strips', 'clay_strips')
        draw_brush_operator(pie, 'Crease', 'crease')
        draw_brush_operator(pie, 'Clay Thumb', 'clay_thumb')
        draw_brush_operator(pie, 'Layer', 'layer')

class SUBPIE_MT_sculpt_brush_select_special(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_special"
    bl_label = "Special Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Cloth', 'cloth')
        draw_brush_operator(pie, 'Erase Multires Displacement', 'displacement_eraser')
        draw_brush_operator(pie, 'Density', 'simplify')
        draw_brush_operator(pie, 'Paint', 'paint')
        draw_brush_operator(pie, 'Smear', 'smear')
        draw_brush_operator(pie, 'Face Set Paint', 'draw_face_sets')
        draw_brush_operator(pie, 'Boundary', 'boundary')
        draw_brush_operator(pie, 'Smear Multires Displacement', 'displacement_smear')


# ADD OBJECT SUB MENUS ######################################################################

class SUBPIE_MT_add_mesh(Menu):
    bl_label = "Mesh"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("mesh.primitive_cube_add", text="Cube", icon='MESH_CUBE')
        pie.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE')
        pie.operator("mesh.primitive_uv_sphere_add", text="UV Sphere", icon='MESH_UVSPHERE')
        pie.operator("mesh.primitive_ico_sphere_add", text="Ico Sphere", icon='MESH_ICOSPHERE')
        pie.operator("mesh.primitive_cylinder_add", text="Cylinder", icon='MESH_CYLINDER')
        pie.operator("mesh.primitive_cone_add", text="Cone", icon='MESH_CONE')
        pie.operator("mesh.primitive_torus_add", text="Torus", icon='MESH_TORUS')
        pie.operator("mesh.primitive_grid_add", text="Grid", icon='MESH_GRID')

class SUBPIE_MT_add_curves_text(Menu):
    bl_label = "Curves & Text"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("curve.primitive_bezier_curve_add", text="Bezier", icon='CURVE_BEZCURVE')
        pie.operator("curve.primitive_bezier_circle_add", text="Circle", icon='CURVE_BEZCIRCLE')
        pie.operator("curve.primitive_nurbs_circle_add", text="NURBS Circle", icon='CURVE_NCIRCLE')
        pie.operator("curve.primitive_nurbs_curve_add", text="NURBS Curve", icon='CURVE_NCURVE')
        pie.operator("curve.primitive_nurbs_path_add", text="NURBS Path", icon='CURVE_PATH')
        pie.operator("object.text_add", text="Text", icon='FONT_DATA')

class SUBPIE_MT_add_empties(Menu):
    bl_label = "Empties"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("object.empty_add", "type")

class SUBPIE_MT_add_lights_probes(Menu):
    bl_label = "Lights & Probes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("object.light_add", "type")
        pie.operator_enum("object.lightprobe_add", "type")

class SUBPIE_MT_add_cameras_speakers(Menu):
    bl_label = "Camera, Images & Speakers"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("object.camera_add", text="Camera", icon='CAMERA_DATA')
        pie.operator("object.speaker_add", text="Speaker", icon='SPEAKER')
        pie.operator("object.empty_image_add", text="Reference", icon='IMAGE_REFERENCE').background = False
        pie.operator("object.empty_image_add", text="Background", icon='IMAGE_BACKGROUND').background = True
        pie.operator("image.import_as_mesh_planes", text="Image Mesh Plane", icon='IMAGE_PLANE')

class SUBPIE_MT_add_greasepencil(Menu):
    bl_label = "Grease Pencil"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("object.grease_pencil_add", "type")

class SUBPIE_MT_add_forcefield(Menu):
    bl_label = "Volumes & Force Fields"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("object.effector_add", "type")


# MAIN CONTEXT PIE MENU ######################################################################

class VIEW3D_PIE_MT_context(Menu):
    bl_idname = "PIE_MT_context_pie"
    bl_label = "Context Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        mode_actions = {
            'EDIT_MESH': self.draw_edit_mesh,
            'EDIT_CURVE': self.draw_edit_curve,
            'EDIT_ARMATURE': self.draw_edit_armature,
            'OBJECT': self.draw_object,
            'SCULPT': self.draw_sculpt,
            'POSE': self.draw_pose,
            'PAINT_VERTEX': self.draw_paint_vertex,
        }

        if context.mode in mode_actions:
            mode_actions[context.mode](pie, context)

    def draw_edit_mesh(self, pie, context):
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode

        if is_vert_mode:
            self.draw_edit_mesh_vert(pie, context)
        elif is_edge_mode:
            self.draw_edit_mesh_edge(pie, context)
        elif is_face_mode:
            self.draw_edit_mesh_face(pie, context)

    def draw_edit_mesh_vert(self, pie, context):
        # WEST
        pie.operator("mesh.set_knife_tool", text="Knife")
        # EAST
        pie.operator("wm.call_menu_pie", text='Connect...', icon="TRIA_RIGHT").name = "SUBPIE_MT_connect"
        # SOUTH
        pie.operator("mesh.extrude_vertices_move", text="Extrude Vertices")
        # NORTH
        pie.operator("wm.call_menu_pie", text='Merge...', icon="TRIA_UP").name = "SUBPIE_MT_merge"
        # NORTH-WEST
        pie.operator("mesh.set_loopcut_tool", text="Insert Loop")
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Divide...', icon="TRIA_RIGHT").name = "SUBPIE_MT_divide"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Delete...', icon="TRIA_DOWN").name = "SUBPIE_MT_PieDelete"
        # SOUTH-EAST
        pie.operator("transform.vert_slide", text="Slide Vertex")

        # Static dropdown menu
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        dropdown_menu.operator("mesh.bisect", text="Bisect")
        dropdown_menu.operator("wm.call_menu_pie", text='Separate...').name = "SUBPIE_MT_separate"

    def draw_edit_mesh_edge(self, pie, context):
        # WEST
        pie.operator("mesh.set_knife_tool", text="Knife")
        # EAST
        pie.operator("wm.call_menu_pie", text='Connect...', icon="TRIA_RIGHT").name = "SUBPIE_MT_connect"
        # SOUTH
        pie.operator("mesh.extrude_edges_move", text="Extrude Edges")
        # NORTH
        pie.operator("wm.call_menu_pie", text='Merge...', icon="TRIA_UP").name = "SUBPIE_MT_merge"
        # NORTH-WEST
        pie.operator("mesh.set_loopcut_tool", text="Insert Loop")
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Divide...', icon="TRIA_RIGHT").name = "SUBPIE_MT_divide"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Delete...', icon="TRIA_LEFT").name = "SUBPIE_MT_PieDelete"
        # SOUTH-EAST
        pie.operator("transform.edge_slide", text="Slide Edge")

        # Static dropdown menu
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        dropdown_menu.operator("mesh.mark_sharp", text="Mark Sharp").clear = False
        dropdown_menu.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
        dropdown_menu.operator("mesh.edge_rotate", text="Rotate CW").use_ccw = False
        dropdown_menu.operator("mesh.edge_rotate", text="Rotate CCW").use_ccw = True
        dropdown_menu.operator("mesh.mark_seam", text='Mark Seam').clear = False
        dropdown_menu.operator("mesh.mark_seam", text='Clear Seam').clear = True
        dropdown_menu.operator("transform.edge_crease")
        dropdown_menu.operator("transform.edge_bevelweight")
        dropdown_menu.operator("wm.call_menu_pie", text='Separate').name = "SUBPIE_MT_separate"

    def draw_edit_mesh_face(self, pie, context):
        # WEST
        pie.operator("mesh.set_knife_tool", text="Knife")
        # EAST
        if "bl_ext.blender_org.looptools" in bpy.context.preferences.addons:
            pie.operator("wm.call_menu_pie", text='LoopTools...', icon="TRIA_RIGHT").name = "SUBPIE_MT_edit_mesh_looptools"
        else:
            pie.operator("mesh.bridge_edge_loops", text="Bridge Faces")
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Extrude Faces...', icon="TRIA_DOWN").name = "SUBPIE_MT_extrudeFaces"
        # NORTH
        pie.operator("wm.call_menu_pie", text='Merge...', icon="TRIA_UP").name = "SUBPIE_MT_merge"
        # NORTH-WEST
        pie.operator("mesh.set_loopcut_tool", text="Insert Loop")
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Divide...', icon="TRIA_RIGHT").name = "SUBPIE_MT_divide"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Delete...', icon="TRIA_LEFT").name = "SUBPIE_MT_PieDelete"
        # SOUTH-EAST
        pie.operator("transform.shrink_fatten")

        # Static dropdown menu
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        dropdown_menu.operator("mesh.bisect")
        dropdown_menu.operator("mesh.flip_normals")

    def draw_edit_curve(self, pie, context):
        # WEST
        pie.operator("transform.transform", text='Radius').mode = 'CURVE_SHRINKFATTEN'
        # EAST
        pie.operator("wm.call_menu_pie", text='Smooth...').name = "SUBPIE_MT_smoothCurve"
        # SOUTH
        pie.operator("curve.extrude_move")
        # NORTH
        pie.operator("curve.make_segment")
        # NORTH-WEST
        pie.operator("transform.tilt")
        # NORTH-EAST
        pie.operator("curve.subdivide")
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Delete/Clear...').name = "SUBPIE_MT_curveDelete"
        # SOUTH-EAST
        pie.operator("curve.separate")

    def draw_edit_armature(self, pie, context):
        # WEST
        pie.operator("armature.parent_set", text="Make Parent")
        # EAST
        pie.operator("armature.parent_clear", text="Clear Parent")
        # SOUTH
        pie.operator("armature.extrude_move")
        # NORTH
        pie.operator("armature.fill")
        # NORTH-WEST
        pie.operator("armature.symmetrize")
        # NORTH-EAST
        pie.operator("armature.subdivide", text="Subdivide")
        # SOUTH-WEST
        pie.operator("armature.dissolve", text="Dissolve")
        # SOUTH-EAST
        pie.operator("armature.split")

    def draw_object(self, pie, context):
        obj = context.object
        sel = context.selected_objects

        if obj is not None and sel:
            self.draw_object_with_selection(pie, context, obj, sel)
        else:
            self.draw_object_add_menu(pie, context)

    def draw_object_with_selection(self, pie, context, obj, sel):
        # WEST & EAST
        if obj.type in {'MESH', 'CURVE', 'SURFACE'}:
            pie.operator("wm.call_menu_pie", text='Shade...').name = "SUBPIE_MT_shadeObject"
            #pie.operator("wm.call_menu_pie", text='Link/Transfer...').name = "SUBPIE_MT_LinkTransfer"
            pie.operator("wm.call_menu_pie", text='Copy...').name = "SUBPIE_MT_object_copy"
        elif obj.type == 'ARMATURE':
            pie.prop(obj.data, "pose_position", expand=True)
        elif obj.type == 'CAMERA':
            op = pie.operator("wm.context_modal_mouse", text='Adjust Focal Length')
            op.data_path_iter = "selected_editable_objects"
            op.data_path_item = "data.lens"
            op.header_text = "Camera Focal Length: %.1fmm"
            op.input_scale = 0.1
            op = pie.operator("wm.context_modal_mouse", text='Adjust Focus Distance')
            op.data_path_iter = "selected_editable_objects"
            op.data_path_item = "data.dof.focus_distance"
            op.header_text = "Focus Distance: %.3f"
            op.input_scale = 0.02
        else:
            pie.separator()
            pie.separator()

        # SOUTH
        pie.operator("wm.call_menu_pie", text='Apply...').name = "SUBPIE_MT_applyTransform"

        # NORTH
        if len(sel) > 1:
            if obj.type in {'MESH', 'CURVE'}:
                pie.operator("wm.call_menu_pie", text='Join/Bool...').name = "SUBPIE_MT_joinMeshes"
            else:
                pie.operator("object.join")
        elif obj.type in {'MESH', 'CURVE', 'SURFACE'}:
            pie.operator("wm.call_menu_pie", text='Add Interactive...').name = "SUBPIE_MT_addMeshInteractive"
        elif obj.type == 'CAMERA':
            pie.operator("view3d.object_as_camera")
        else:
            pie.separator()

        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Parent/Link...').name = "SUBPIE_MT_parent"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Convert...').name = "SUBPIE_MT_convert"
        # SOUTH-WEST
        pie.operator("object.delete")
        # SOUTH-EAST
        pie.operator("mesh.separate", text='Separate Loose').type = 'LOOSE'

    def draw_object_add_menu(self, pie, context):
        # WEST
        pie.operator("wm.call_menu_pie", text="Mesh...", icon='MESH_CUBE').name = "SUBPIE_MT_add_mesh"
        # EAST
        pie.operator("wm.call_menu_pie", text="Curves & Text...", icon='CURVE_DATA').name = "SUBPIE_MT_add_curves_text"
        # SOUTH
        pie.operator("wm.call_menu_pie", text="Empties...", icon='EMPTY_DATA').name = "SUBPIE_MT_add_empties"
        # NORTH
        pie.operator("wm.call_menu_pie", text="Lights & Probes...", icon='LIGHT').name = "SUBPIE_MT_add_lights_probes"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Camera & Images...", icon='CAMERA_DATA').name = "SUBPIE_MT_add_cameras_speakers"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text="Grease Pencil...", icon='OUTLINER_OB_GREASEPENCIL').name = "SUBPIE_MT_add_greasepencil"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text="Force Fields...", icon='FORCE_DRAG').name = "SUBPIE_MT_add_forcefield"
        # SOUTH-EAST
        pie.operator("object.armature_add", text="Armature", icon='ARMATURE_DATA')

    def draw_sculpt(self, pie, context):
        global brush_icons
        pie.scale_y = 1.2

        # WEST
        pie.operator('wm.call_menu_pie', text="    Transform Brushes...",
                     icon_value=brush_icons['snake_hook']).name = SUBPIE_MT_sculpt_brush_select_transform.bl_idname
        # EAST
        pie.operator('wm.call_menu_pie', text="    Volume Brushes...",
                     icon_value=brush_icons['blob']).name = SUBPIE_MT_sculpt_brush_select_volume.bl_idname

        # SOUTH
        if blender_uses_brush_assets():
            sculpt_settings = context.tool_settings.sculpt
            brush = sculpt_settings.brush
            col = pie.column()
            brush_row = col.row()
            brush_row.scale_y = 0.75
            brush_row.scale_x = 0.15
            BrushAssetShelf.draw_popup_selector(brush_row, context, brush, show_name=False)
            name_row = col.row().box()
            if brush:
                name_row.label(text=brush.name)
        else:
            pie.separator()

        # NORTH
        draw_brush_operator(pie, 'Mask', 'mask')
        # NORTH-WEST
        draw_brush_operator(pie, 'Grab', 'grab')
        # NORTH-EAST
        draw_brush_operator(pie, 'Draw', 'draw')
        # SOUTH-WEST
        pie.operator('wm.call_menu_pie', text="    Contrast Brushes...",
                     icon_value=brush_icons['flatten']).name = SUBPIE_MT_sculpt_brush_select_contrast.bl_idname
        # SOUTH-EAST
        pie.operator('wm.call_menu_pie', text="    Special Brushes...",
                     icon_value=brush_icons['draw_face_sets']).name = SUBPIE_MT_sculpt_brush_select_special.bl_idname

    def draw_pose(self, pie, context):
        # WEST
        #pie.operator("pose.copy")
        pie.operator("wm.call_menu_pie", text='Copy...').name = "SUBPIE_MT_pose_copy"
        # EAST
        pie.operator("pose.paste").flipped = False
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Inbetweens...').name = "SUBPIE_MT_inbetweens"
        # NORTH
        pie.operator("wm.call_menu_pie", text='Motion Paths...').name = "SUBPIE_MT_motionpaths"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text='Constraints...').name = "SUBPIE_MT_constraints"
        # NORTH-EAST
        pie.operator("pose.paste", text='Paste Flipped').flipped = True
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Propagate...').name = "SUBPIE_MT_propagate"
        # SOUTH-EAST
        pie.operator("wm.call_menu_pie", text='IK...').name = "SUBPIE_MT_ik"

    def draw_paint_vertex(self, pie, context):
        pie.scale_y = 1.2
        # WEST
        draw_brush_operator(pie, 'Paint Hard', 'paint hard')
        # EAST
        draw_brush_operator(pie, 'Paint Soft', 'paint soft')
        # SOUTH
        pie.separator()
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        draw_brush_operator(pie, 'Paint Hard Pressure', 'paint hard pressure')
        # SOUTH-EAST
        pie.separator()


# HELPER FUNCTIONS ######################################################################

def blender_uses_brush_assets():
    return 'asset_activate' in dir(bpy.ops.brush)


def draw_brush_operator(layout, brush_name: str, brush_icon: str = ""):
    """Draw a brush select operator with pre-4.3 icons."""
    if blender_uses_brush_assets():
        op = layout.operator('brush.asset_activate', text="     " + brush_name,
                             icon_value=brush_icons.get(brush_icon, 0))
        op.asset_library_type = 'ESSENTIALS'
        if bpy.context.mode == 'SCULPT':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_sculpt.blend", "Brush", brush_name)
        elif bpy.context.mode == 'PAINT_VERTEX':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_vertex.blend", "Brush", brush_name)
    else:
        if brush_icon:
            op = layout.operator("paint.brush_select", text="     " + brush_name,
                                 icon_value=brush_icons[brush_icon])
            op.sculpt_tool = brush_icon.upper()
        else:
            layout.separator()


brush_icons = {}


def create_icons():
    global brush_icons
    icons_directory = Path(__file__).parent / "icons"
    for icon_path in icons_directory.iterdir():
        icon_value = bpy.app.icons.new_triangles_from_file(icon_path.as_posix())
        brush_name = icon_path.stem.split(".")[-1]
        brush_icons[brush_name] = icon_value


def release_icons():
    global brush_icons
    for value in brush_icons.values():
        bpy.app.icons.release(value)


# REGISTRATION ######################################################################

registry = [
    SetKnifeTool,
    SetLoopCutTool,
    CURVE_OT_clear_radius,
    SUBPIE_MT_merge,
    SUBPIE_MT_connect,
    SUBPIE_MT_extrudeFaces,
    SUBPIE_MT_divide,
    SUBPIE_MT_smoothCurve,
    SUBPIE_MT_curveDelete,
    SUBPIE_MT_parent,
    SUBPIE_MT_convert,
    SUBPIE_MT_joinMeshes,
    SUBPIE_MT_addMeshInteractive,
    SUBPIE_MT_applyTransform,
    SUBPIE_MT_shadeObject,
    SUBPIE_MT_LinkTransfer,
    SUBPIE_MT_CopyTransfer,
    SUBPIE_MT_inbetweens,
    SUBPIE_MT_propagate,
    SUBPIE_MT_constraints,
    SUBPIE_MT_ik,
    SUBPIE_MT_motionpaths,
    SUBPIE_MT_PieDelete,
    SUBPIE_MT_sculpt_brush_select_contrast,
    SUBPIE_MT_sculpt_brush_select_transform,
    SUBPIE_MT_sculpt_brush_select_volume,
    SUBPIE_MT_sculpt_brush_select_special,
    SUBPIE_MT_add_mesh,
    SUBPIE_MT_add_curves_text,
    SUBPIE_MT_add_empties,
    SUBPIE_MT_add_lights_probes,
    SUBPIE_MT_add_cameras_speakers,
    SUBPIE_MT_add_greasepencil,
    SUBPIE_MT_add_forcefield,
    VIEW3D_PIE_MT_context,
]

if "bl_ext.blender_org.looptools" in bpy.context.preferences.addons:
    registry.append(SUBPIE_MT_edit_mesh_looptools)


def register():
    create_icons()
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=VIEW3D_PIE_MT_context.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="3D View",
        on_drag=False,
    )
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=VIEW3D_PIE_MT_context.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="Sculpt",
        on_drag=False,
    )


def unregister():
    release_icons()
