# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu


###-----------------------------------------------------------------------------###
###                          OBJECT MODE SUB MENUS                              ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_parent(Menu):
    bl_label = "Parent"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator('object.make_links_data', text='Link Collections').type = 'GROUPS'
        # EAST
        pie.operator('object.make_links_data', text='Link Instance Collection').type = 'DUPLICOLLECTION'
        # SOUTH
        pie.operator('object.make_links_data', text='Link Material').type = 'MATERIAL'
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.operator("object.parent_set")
        # NORTH-EAST
        pie.operator("object.parent_clear")
        # SOUTH-WEST
        pie.operator('object.make_links_data', text='Link Animation Data').type = 'ANIMATION'
        # SOUTH-EAST
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
            # WEST
            pie.operator("object.boolean_brush_difference", text="Difference", icon='SELECT_SUBTRACT')
            # EAST
            pie.operator("object.boolean_brush_union", text="Union", icon='SELECT_EXTEND')
            # SOUTH
            pie.operator("object.boolean_brush_intersect", text="Intersect", icon='SELECT_INTERSECT')
            # NORTH
            pie.operator("object.join")
            # NORTH-WEST
            sub = pie.operator("object.join_modifier")
            sub.use_collections = False
            sub.name_source = 'ACTIVE_OBJECT'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            # NORTH-EAST
            sub = pie.operator("object.join_modifier", text="Join Parent Collections")
            sub.use_collections = True
            sub.inherit_name = True
            sub.name_source = 'PARENT_COLLECTION'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            # SOUTH-WEST
            pie.operator("object.boolean_brush_slice", text="Slice", icon='SELECT_DIFFERENCE')
            # SOUTH-EAST
            pie.separator()
        else:
            # WEST
            pie.operator("object.add_pie_boolean", text="Difference", icon='SELECT_SUBTRACT').boolean_type = 'DIFFERENCE'
            # EAST
            pie.operator("object.add_pie_boolean", text="Union", icon='SELECT_EXTEND').boolean_type = 'UNION'
            # SOUTH
            pie.operator("object.add_pie_boolean", text="Intersect", icon='SELECT_INTERSECT').boolean_type = 'INTERSECT'
            # NORTH
            pie.operator("object.join")
            # NORTH-WEST
            sub = pie.operator("object.join_modifier")
            sub.use_collections = False
            sub.name_source = 'ACTIVE_OBJECT'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            # NORTH-EAST
            sub = pie.operator("object.join_modifier", text="Join Parent Collections")
            sub.use_collections = True
            sub.inherit_name = True
            sub.name_source = 'PARENT_COLLECTION'
            sub.parent_destination = 'ACTIVE_COLLECTION'
            # SOUTH-WEST / SOUTH-EAST
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

        # WEST
        op = pie.operator("object.transform_apply", text="Location")
        op.location, op.rotation, op.scale = True, False, False
        # EAST
        op = pie.operator("object.transform_apply", text="Scale")
        op.location, op.rotation, op.scale = False, False, True
        # SOUTH
        op = pie.operator("object.transform_apply", text="Rotation")
        op.location, op.rotation, op.scale = False, True, False
        # NORTH
        op = pie.operator("object.transform_apply", text="All Transforms")
        op.location, op.rotation, op.scale = True, True, True
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("object.convert", text="Visual Geo to Mesh").target = 'MESH'
        # SOUTH-WEST / SOUTH-EAST
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


###-----------------------------------------------------------------------------###
###                          ADD OBJECT SUB MENUS                               ###
###-----------------------------------------------------------------------------###

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
        pie.operator("curve.create_curve_pen", text="Curve Pen", icon='CURVE_BEZCURVE')
        pie.operator("curve.create_curve_draw", text="Curve Draw", icon='GREASEPENCIL')


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


###-----------------------------------------------------------------------------###
###                              REGISTRY                                       ###
###-----------------------------------------------------------------------------###

registry = [
    SUBPIE_MT_parent,
    SUBPIE_MT_convert,
    SUBPIE_MT_joinMeshes,
    SUBPIE_MT_addMeshInteractive,
    SUBPIE_MT_applyTransform,
    SUBPIE_MT_shadeObject,
    SUBPIE_MT_add_mesh,
    SUBPIE_MT_add_curves_text,
    SUBPIE_MT_add_empties,
    SUBPIE_MT_add_lights_probes,
    SUBPIE_MT_add_cameras_speakers,
    SUBPIE_MT_add_greasepencil,
    SUBPIE_MT_add_forcefield,
]


###-----------------------------------------------------------------------------###
###                              DRAW FUNCTIONS                                 ###
###-----------------------------------------------------------------------------###

def draw_context_object(pie, context):
    obj = context.object
    sel = context.selected_objects

    if obj is not None and sel:
        _draw_object_with_selection(pie, context, obj, sel)
    else:
        _draw_object_add_menu(pie, context)


def _draw_object_with_selection(pie, context, obj, sel):
    # WEST & EAST (type-dependent)
    if obj.type in {'MESH', 'CURVE', 'SURFACE'}:
        pie.operator("wm.call_menu_pie", text='Shade...').name = "SUBPIE_MT_shadeObject"
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


def _draw_object_add_menu(pie, context):
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
