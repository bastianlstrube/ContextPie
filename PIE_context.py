# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Context Pie: 'Shift + Right Mouse'",
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}

import os
from pathlib import Path

import bpy
from bpy.types import Menu
from .hotkeys import register_hotkey

from bpy.app.translations import contexts as i18n_contexts
from bl_ui.properties_paint_common import BrushAssetShelf

# Sub Pie Menu for mesh merge operators
class SUBPIE_MT_merge(Menu):
    bl_label = "Merge"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.merge", text='Cursor').type = 'CURSOR'
        # EAST
        pie.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'
        # SOUTH
        pie.separator()
        # NORTH
        pie.operator("mesh.merge", text='Center').type = 'CENTER'
        
        '''     Unfinished detection of ['FIRST', LAST] types of mesh.merge
        is_vert_mode = context.tool_settings.mesh_select_mode[0]
        def vertsLen():
            ob = context.object
            ob.update_from_editmode() # not available in older versions!
            verts_sel = len([v for v in ob.data.vertices if v.select])
            return (verts_sel)
        verts = vertsLen()
        del vertsLen
        def mergeTypes():
            rna = bpy.ops.mesh.merge.get_rna_type()
            mergeTypLen = len( rna.properties['type'].enum_items.keys() )
            return mergeTypLen
        print('lol')
        is_vert_mode = context.tool_settings.mesh_select_mode[0]
        typeLen = mergeTypes()
        del mergeTypes
        if is_vert_mode and typeLen == 5:
        '''
        # NORTH-WEST
        pie.operator("mesh.unsubdivide")
        # NORTH-EAST
        pie.operator("mesh.remove_doubles", text="By Distance")

        try:
            # SOUTH-WEST
            pie.operator("mesh.merge", text='First').type = 'FIRST'
            # SOUTH-EAST
            pie.operator("mesh.merge", text='Last').type = 'LAST'
        except TypeError:
            pie.separator()
            pie.separator()

# Sub Pie for mesh connect operators
class SUBPIE_MT_connect(Menu):
    bl_label = "Connect"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()
        # EAST
        pie.operator("mesh.bridge_edge_loops", text="Bridge")
        # SOUTH
        pie.operator("mesh.fill_grid", text="Grid Fill Loop")
        # NORTH
        pie.operator("mesh.vert_connect_path", text="Cut Vert Path")
        # NORTH-WEST
        pie.operator("mesh.vert_connect", text="Cut Connect")
        # NORTH-EAST
        pie.operator("mesh.edge_face_add", text="Add Edge/Face")
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.operator("mesh.fill", text="Fill Loop")

# Sub Pie for mesh face split/separate operators
class SUBPIE_MT_separate(Menu):
    bl_label = "Split/Separate"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.split")
        # EAST
        pie.operator("mesh.separate", text='By Loose Parts').type = 'LOOSE'
        # SOUTH
        pie.operator("mesh.rip_move")
        # NORTH
        pie.separator()
        

        # NORTH-WEST
        pie.operator("mesh.edge_split", text='Split By Edge').type = 'EDGE'      
        # NORTH-EAST
        pie.operator("mesh.separate", text='By Material').type = 'MATERIAL'
        # SOUTH-WEST
        pie.operator("mesh.edge_split", text='Split By Vertex').type = 'VERT'
        # SOUTH-EAST
        pie.operator("mesh.separate", text='Selection').type = 'SELECTED'

# Sub Pie for mesh vert/edge/face divisions
class SUBPIE_MT_divide(Menu):
    bl_label = "Divide"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode

        if is_vert_mode:
            # WEST
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            # EAST
            pie.operator("mesh.subdivide", text='Subdivide')
            # SOUTH
            pie.separator()
            # NORTH
            pie.operator("mesh.poke")
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.operator("mesh.bevel", text='Bevel').affect = 'VERTICES'
            # SOUTH-WEST
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            # SOUTH-EAST
            pie.separator()

        if is_edge_mode:
            # WEST
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            # EAST
            pie.operator("mesh.subdivide", text='Subdivide')
            # SOUTH
            pie.operator("mesh.rip_move")
            # NORTH
            pie.operator("mesh.poke")
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.operator("mesh.bevel", text='Bevel').affect = 'EDGES'     
            # SOUTH-WEST
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            # SOUTH-EAST
            pie.operator("mesh.edge_split")

        if is_face_mode:
            # WEST
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            # EAST
            pie.operator("mesh.bevel", text='Bevel')
            # SOUTH
            pie.separator()
            # NORTH
            pie.operator("mesh.poke")
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.operator("mesh.subdivide", text='Subdivide')
            # SOUTH-WEST
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            # SOUTH-EAST
            pie.separator()

# Sub Pie for mesh face extrusions
class SUBPIE_MT_extrudeFaces(Menu):
    bl_label = "Extrude Faces"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.inset", text="Inset").use_individual = False
        # EAST
        pie.operator("mesh.extrude_faces_move", text="Extrude Individual")
        # SOUTH
        pie.operator("view3d.edit_mesh_extrude_move_shrink_fatten", text="Extrude Along Normals")
        # NORTH
        pie.operator("mesh.solidify")
        
        # NORTH-WEST
        pie.operator("mesh.inset", text="Inset Individual").use_individual = True
        # NORTH-EAST
        pie.operator("mesh.wireframe")
        # SOUTH-WEST
        pie.operator("wm.tool_set_by_id", text="Extrude To Cursor Tool").name = "builtin.extrude_to_cursor"
        # SOUTH-EAST
        pie.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude")

# Sub Pie Menu for Mesh Delete, ripped directly from 3D Viewport Pie Menus
class SUBPIE_MT_PieDelete(Menu):
    bl_label = "Pie Delete"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        box = pie.split().column()
        box.operator("mesh.dissolve_limited", text="Limited Dissolve", icon='STICKY_UVS_LOC')
        box.operator("mesh.delete_edgeloop", text="Delete Edge Loops", icon='NONE')
        box.operator("mesh.edge_collapse", text="Edge Collapse", icon='UV_EDGESEL')
        # 6 - RIGHT
        box = pie.split().column()
        box.operator("mesh.remove_doubles", text="Merge By Distance", icon='NONE')
        box.operator("mesh.delete", text="Only Edge & Faces", icon='NONE').type = 'EDGE_FACE'
        box.operator("mesh.delete", text="Only Faces", icon='UV_FACESEL').type = 'ONLY_FACE'
        # 2 - BOTTOM
        pie.operator("mesh.dissolve_edges", text="Dissolve Edges", icon='SNAP_EDGE')
        # 8 - TOP
        pie.operator("mesh.delete", text="Delete Edges", icon='EDGESEL').type = 'EDGE'
        # 7 - TOP - LEFT
        pie.operator("mesh.delete", text="Delete Vertices", icon='VERTEXSEL').type = 'VERT'
        # 9 - TOP - RIGHT
        pie.operator("mesh.delete", text="Delete Faces", icon='FACESEL').type = 'FACE'
        # 1 - BOTTOM - LEFT
        pie.operator("mesh.dissolve_verts", text="Dissolve Vertices", icon='SNAP_VERTEX')
        # 3 - BOTTOM - RIGHT
        pie.operator("mesh.dissolve_faces", text="Dissolve Faces", icon='SNAP_FACE')

# Sub Pie for curve operators
class SUBPIE_MT_smoothCurve(Menu):
    bl_label = "Smooth"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("curve.normals_make_consistent")
        # EAST
        pie.operator("curve.smooth")
        # SOUTH
        pie.operator("curve.smooth_radius")
        # NORTH
        pie.operator("curve.smooth_tilt")
        # NORTH-WEST
        pie.operator("curve.smooth_weight")
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()

# Sub Pie for curve operators
class SUBPIE_MT_curveDelete(Menu):
    bl_label = "Delete/Clear"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("curve.dissolve_verts")
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("curve.delete", text="Delete Segment").type = 'SEGMENT'
        # NORTH
        pie.operator("curve.tilt_clear")
        
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("curve.delete", text="Delete Vert").type = 'VERT'
        # SOUTH-EAST
        pie.separator()


# OBJECT MODE SUB MENUS
# Sub Pie for object applying transform
class SUBPIE_MT_applyTransform(Menu):
    bl_label = "Apply"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        op =  pie.operator("object.transform_apply", text="Location")
        op.location = True
        op.rotation = False
        op.scale = False
        # EAST
        op =  pie.operator("object.transform_apply", text="Scale")
        op.scale = True
        op.location = False
        op.rotation = False
        # SOUTH
        op =  pie.operator("object.transform_apply", text="Rotation")
        op.rotation = True
        op.location = False
        op.scale = False
        # NORTH
        op = pie.operator("object.transform_apply", text="All Transforms")
        op.location = True
        op.rotation = True
        op.scale = True
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("object.convert", text="Visual Geo to Mesh").target = 'MESH'
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()

class SUBPIE_MT_shadeObject(Menu):
    bl_label = "Shade/Display"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("object.shade_smooth")
        # EAST & SOUTH & NORTH & NORTH-WEST  
        pie.prop(context.object, "display_type", expand=True)
        # SOUTH
        # NORTH
        # NORTH-WEST
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("object.shade_flat")
        # SOUTH-EAST
        pie.operator("object.shade_auto_smooth")

class SUBPIE_MT_LinkTransfer(Menu):
    bl_label = "Link"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("wm.call_menu_pie", text='Copy/Transfer...').name = "SUBPIE_MT_CopyTransfer"
        # EAST
        pie.operator('object.make_links_data', text='Link Material').type = 'MATERIAL'
        # SOUTH
        pie.operator('object.make_links_data', text='Link Animation Data').type = 'ANIMATION'
        # NORTH
        pie.operator('object.make_links_data', text='Link Collections').type = 'GROUPS'
        # NORTH-WEST
        pie.operator('object.make_links_data', text='Link Instance Collection').type = 'DUPLICOLLECTION'
        # NORTH-EAST
        pie.operator('object.make_links_data', text='Link Object Data').type = 'OBDATA'
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()

class SUBPIE_MT_CopyTransfer(Menu):
    bl_label = "Copy/Transfer"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator('object.data_transfer')
        # EAST
        pie.operator('object.constraints_copy', text='Copy Constraints')
        # SOUTH
        pie.operator('object.join_uvs', text='Copy UV Maps')
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.operator('object.make_links_data', text='Copy Grease Pencil FX').type = 'EFFECTS'
        # NORTH-EAST
        pie.operator('object.modifiers_copy_to_selected', text='Copy Modifiers')
        # SOUTH-WEST
        pie.operator('object.datalayout_transfer')
        # SOUTH-EAST
        pie.separator()

# Sub Pie Menu for animation inbetween ops
class SUBPIE_MT_inbetweens(Menu):
    bl_label = "Inbetweens"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("pose.push_rest")

        # EAST
        pie.operator("pose.relax_rest")

        # SOUTH
        pie.operator("pose.blend_to_neighbor")

        # NORTH
        pie.operator("pose.breakdown")
        
        # NORTH-WEST
        pie.separator()
               

        # NORTH-EAST
        pie.separator()

        # SOUTH-WEST
        pie.operator("pose.push")

        # SOUTH-EAST
        pie.operator("pose.relax")

# Sub Pie Menu for propagate Options
class SUBPIE_MT_propagate(Menu):
    bl_label = "propagate"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("pose.propagate",text =  "Selected Markers").mode = 'SELECTED_MARKERS'

        # EAST
        pie.operator("pose.propagate",text = "Selected Keys").mode = 'SELECTED_KEYS'

        # SOUTH
        pie.operator("pose.propagate",text = "Last Key").mode = 'LAST_KEY'

        # NORTH
        pie.operator("pose.propagate",text = "Next Key").mode = 'NEXT_KEY'
        
        # NORTH-WEST
        pie.operator("pose.propagate",text = "Before Frame").mode = 'BEFORE_FRAME'
               
        # NORTH-EAST
        pie.operator("pose.propagate",text = "Before End").mode = 'BEFORE_END'

        # SOUTH-WEST
        pie.separator()

        # SOUTH-EAST
        pie.separator()

# Sub Pie Menu for Constraints Option
class SUBPIE_MT_constraints(Menu):
    bl_label = "constraints"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()

        # EAST
        pie.separator()

        # SOUTH
        pie.operator("pose.constraints_clear",text = "Clear Constraints")

        # NORTH
        pie.operator("pose.constraint_add_with_targets",text = "Constraint with targets")

        # NORTH-WEST
        pie.separator()
               
        # NORTH-EAST
        pie.separator()

        # SOUTH-WEST
        pie.separator()

        # SOUTH-EAST
        pie.separator()
    
# Sub Pie Menu for Inverse Kinametics    
class SUBPIE_MT_ik(Menu):
    bl_label = "ik"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()

        # EAST
        pie.separator()
        
        # SOUTH
        pie.operator("pose.ik_clear",text = "Clear IK")

        # NORTH
        pie.operator("pose.ik_add",text = "Add IK")
        
        # NORTH-WEST
        pie.separator()

        # NORTH-EAST
        pie.separator()

        # SOUTH-WEST
        pie.separator()

        # SOUTH-EAST
        pie.separator()

# Sub Pie Menu for animation motion paths
class SUBPIE_MT_motionpaths(Menu):
    bl_label = "Motion Paths"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()

        # EAST
        pie.separator()

        # SOUTH
        pie.operator("pose.paths_clear")

        # NORTH
        calc = pie.operator("pose.paths_calculate")
        calc.start_frame = context.scene.frame_start
        calc.end_frame = context.scene.frame_end
        calc.bake_location = 'HEADS'

        
        # NORTH-WEST
        pie.operator("pose.paths_update_visible")
               

        # NORTH-EAST
        pie.operator("pose.paths_update")

        # SOUTH-WEST
        pie.separator()

        # SOUTH-EAST 
        pie.separator()


### SUB PIE MENUS FOR SCULPT BRUSH SELECT, COPIED DIRECTLY FROM EXTENSION "3D VIEWPORT PIE MENUS"
class SUBPIE_MT_sculpt_brush_select_contrast(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_contrast"
    bl_label = "Contrast Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # 4 - LEFT
        draw_brush_operator(pie, 'Flatten/Contrast', 'flatten')
        # 6 - RIGHT
        draw_brush_operator(pie, 'Scrape/Fill', 'scrape')
        # 2 - BOTTOM
        draw_brush_operator(pie, 'Fill/Deepen', 'fill')
        # 8 - TOP
        draw_brush_operator(pie, 'Scrape Multiplane', 'multiplane_scrape')
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        draw_brush_operator(pie, 'Smooth', 'smooth')
        # 3 - BOTTOM - RIGHT

class SUBPIE_MT_sculpt_brush_select_transform(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_transform"
    bl_label = "Transform Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # 4 - LEFT
        draw_brush_operator(pie, 'Elastic Deform', 'elastic_deform')
        # 6 - RIGHT
        draw_brush_operator(pie, 'Nudge', 'nudge')
        # 2 - BOTTOM
        draw_brush_operator(pie, 'Relax Slide', 'topology')
        # 8 - TOP
        draw_brush_operator(pie, 'Snake Hook', 'snake_hook')
        # 7 - TOP - LEFT
        draw_brush_operator(pie, 'Twist', 'rotate')
        # 9 - TOP - RIGHT
        draw_brush_operator(pie, 'Pose', 'pose')
        # 1 - BOTTOM - LEFT
        draw_brush_operator(pie, 'Pinch/Magnify', 'pinch')
        # 3 - BOTTOM - RIGHT
        draw_brush_operator(pie, 'Thumb', 'thumb')

class SUBPIE_MT_sculpt_brush_select_volume(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_volume"
    bl_label = "Volume Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # 4 - LEFT
        draw_brush_operator(pie, 'Blob', 'blob')
        # 6 - RIGHT
        draw_brush_operator(pie, 'Clay', 'clay')
        # 2 - BOTTOM
        draw_brush_operator(pie, 'Inflate/Deflate', 'inflate')
        # 8 - TOP
        draw_brush_operator(pie, 'Draw Sharp', 'draw_sharp')
        # 7 - TOP - LEFT
        draw_brush_operator(pie, 'Clay Strips', 'clay_strips')
        # 9 - TOP - RIGHT
        draw_brush_operator(pie, 'Crease', 'crease')
        # 1 - BOTTOM - LEFT
        draw_brush_operator(pie, 'Clay Thumb', 'clay_thumb')
        # 3 - BOTTOM - RIGHT
        draw_brush_operator(pie, 'Layer', 'layer')

class SUBPIE_MT_sculpt_brush_select_special(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_special"
    bl_label = "Special Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # 4 - LEFT
        draw_brush_operator(pie, 'Cloth', 'cloth')
        # 6 - RIGHT
        draw_brush_operator(pie, 'Erase Multires Displacement', 'displacement_eraser')
        # 2 - BOTTOM
        draw_brush_operator(pie, 'Density', 'simplify')
        # 8 - TOP
        draw_brush_operator(pie, 'Paint', 'paint')
        # 7 - TOP - LEFT
        draw_brush_operator(pie, 'Smear', 'smear')
        # 9 - TOP - RIGHT
        draw_brush_operator(pie, 'Face Set Paint', 'draw_face_sets')
        # 1 - BOTTOM - LEFT
        draw_brush_operator(pie, 'Boundary', 'boundary')
        # 3 - BOTTOM - RIGHT
        draw_brush_operator(pie, 'Smear Multires Displacement', 'displacement_smear')

### Add Objects Categories Menus, when nothing is selected
class SUBPIE_MT_add_mesh(Menu):
    bl_label = "Mesh"
    def draw(self, context):
        mesh_pie = self.layout.menu_pie()
        mesh_pie.operator("mesh.primitive_cube_add", text="Cube")
        mesh_pie.operator("mesh.primitive_plane_add", text="Plane")
        mesh_pie.operator("mesh.primitive_uv_sphere_add", text="UV Sphere")
        mesh_pie.operator("mesh.primitive_ico_sphere_add", text="Ico Sphere")
        mesh_pie.operator("mesh.primitive_cylinder_add", text="Cylinder")
        mesh_pie.operator("mesh.primitive_cone_add", text="Cone")
        mesh_pie.operator("mesh.primitive_torus_add", text="Torus")
        mesh_pie.operator("mesh.primitive_grid_add", text="Grid")

class SUBPIE_MT_add_curves_text(Menu):
    bl_label = "Curves & Text"
    def draw(self, context):
        curves_text_pie = self.layout.menu_pie()
        curves_text_pie.operator("curve.primitive_bezier_curve_add", text="Bezier")
        curves_text_pie.operator("curve.primitive_bezier_circle_add", text="Circle")
        curves_text_pie.operator("curve.primitive_nurbs_circle_add", text="NURBS Circle")
        curves_text_pie.operator("curve.primitive_nurbs_curve_add", text="NURBS Curve")
        curves_text_pie.operator("curve.primitive_nurbs_path_add", text="NURBS Path")
        curves_text_pie.operator("object.text_add", text="Text")

class SUBPIE_MT_add_empties(Menu):
    bl_label = "Empties"
    def draw(self, context):
        empties_armatures_pie = self.layout.menu_pie()
        empties_armatures_pie.operator_enum("object.empty_add", "type")  # Use operator_enum

class SUBPIE_MT_add_lights_probes(Menu):
    bl_label = "Lights & Probes"
    def draw(self, context):
        lights_probes_pie = self.layout.menu_pie()
        lights_probes_pie.operator_enum("object.light_add", "type")  # Use operator_enum
        lights_probes_pie.operator_enum("object.lightprobe_add", "type")  # Use operator_enum

class SUBPIE_MT_add_cameras_speakers(Menu):
    bl_label = "Camera, Images & Speakers"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("object.camera_add", text="Camera")
        pie.operator("object.speaker_add", text="Speaker")
        pie.operator("object.empty_image_add", text="Reference").background = False
        pie.operator("object.empty_image_add", text="Background").background = True
        pie.operator("image.import_as_mesh_planes", text="Image Mesh Plane")

class SUBPIE_MT_add_greasepencil(Menu):
    bl_label = "Grease Pencil"
    def draw(self, context):
        gp_instances_pie = self.layout.menu_pie()

        # Grease Pencil (Updated for Blender 4.3+, with layer creation)
        gp_instances_pie.operator_enum("object.grease_pencil_add", "type")

class SUBPIE_MT_add_forcefield(Menu):
    bl_label = "Volumes & Force Fields"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("object.effector_add", "type")


# Main Context Sensitive Pie Menu
class VIEW3D_PIE_MT_context(Menu):
    bl_label    = "Context Pie"

    def draw(self, context):

        if context.mode == 'EDIT_MESH':
            ''' COUNTING LENGTH OF SELECTION LISTS FOR EACH COMPONENT TYPE
            def count_selected_items_for_objects_in_mode():
                selected_verts_len = 0
                selected_edges_len = 0
                selected_faces_len = 0
                for ob in context.objects_in_mode_unique_data:
                    v, e, f = ob.data.count_selected_items()
                    selected_verts_len += v
                    selected_edges_len += e
                    selected_faces_len += f
                return (selected_verts_len, selected_edges_len, selected_faces_len)
            
            selected_verts_len, selected_edges_len, selected_faces_len = count_selected_items_for_objects_in_mode()
            del count_selected_items_for_objects_in_mode
            '''

            is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode

            # Else something is selected
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            if is_vert_mode:
                
                # WEST
                pie.operator("mesh.knife_tool", text="Knife")
                # EAST
                subPie = pie.operator("wm.call_menu_pie", text='Connect...', icon = "RIGHTARROW_THIN")
                subPie.name = "SUBPIE_MT_connect"
                # SOUTH
                pie.operator("mesh.extrude_vertices_move", text="Extrude Vertices")
                # NORTH
                subPie = pie.operator("wm.call_menu_pie", text='Merge...', icon = "RIGHTARROW_THIN")
                subPie.name = "SUBPIE_MT_merge"                
                # NORTH-WEST
                pie.operator("mesh.loopcut_slide", text="Insert Loop")
                # NORTH-EAST
                #pie.operator("mesh.bevel", text="Bevel Vertices").affect = 'VERTICES'
                subPie = pie.operator("wm.call_menu_pie", text='Divide...')
                subPie.name = "SUBPIE_MT_divide"
                # SOUTH-WEST
                subPie = pie.operator("wm.call_menu_pie", text='Delete...', icon = "RIGHTARROW_THIN")
                subPie.name = "SUBPIE_MT_PieDelete"
                # SOUTH-EAST
                pie.operator("transform.vert_slide", text="Slide Vertex")
                
                # Static Vert menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                dropdown_menu.operator("mesh.bisect", text = "Bisect")
                separatePie = dropdown_menu.operator("wm.call_menu_pie", text='Separate...').name = "SUBPIE_MT_separate"
                

            elif is_edge_mode:

                # WEST
                pie.operator("mesh.knife_tool", text="Knife")
                # EAST
                pie.operator("wm.call_menu_pie", text='Connect...').name = "SUBPIE_MT_connect"
                # SOUTH
                pie.operator("mesh.extrude_edges_move", text="Extrude Edges")
                # NORTH
                pie.operator("wm.call_menu_pie", text='Merge...').name = "SUBPIE_MT_merge"
                # NORTH-WEST
                pie.operator("mesh.loopcut_slide", text="Insert Loop")
                # NORTH-EAST
                pie.operator("wm.call_menu_pie", text='Divide...').name = "SUBPIE_MT_divide"
                # SOUTH-WEST
                pie.operator("wm.call_menu_pie", text='Delete...').name = "SUBPIE_MT_PieDelete"
                # SOUTH-EAST
                pie.operator("transform.edge_slide", text="Slide Edge")
                
                # Static edge menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                dropdown_menu.operator("mesh.mark_sharp", text = "Mark Sharp").clear = False
                dropdown_menu.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
                dropdown_menu.operator("mesh.edge_rotate", text="Rotate CW").use_ccw=False
                dropdown_menu.operator("mesh.edge_rotate", text="Rotate CCW").use_ccw=True
                dropdown_menu.operator("mesh.mark_seam", text='Mark Seam').clear = False
                dropdown_menu.operator("mesh.mark_seam", text='Clear Seam').clear = True
                dropdown_menu.operator("transform.edge_crease")
                dropdown_menu.operator("transform.edge_bevelweight")
                dropdown_menu.operator("wm.call_menu_pie", text='Separate').name = "SUBPIE_MT_separate"
                

            elif is_face_mode:

                # WEST
                pie.operator("mesh.knife_tool", text="Knife")
                # EAST
                pie.operator("transform.shrink_fatten")
                # SOUTH
                subPie = pie.operator("wm.call_menu_pie", text='Extrude Faces...')
                subPie.name = "SUBPIE_MT_extrudeFaces"
                #pie.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude Faces")
                # NORTH
                subPie = pie.operator("wm.call_menu_pie", text='Merge...')
                subPie.name = "SUBPIE_MT_merge"
                #pie.operator("mesh.merge", text="Merge")
                
                # NORTH-WEST
                pie.operator("mesh.loopcut_slide", text="Insert Loop")
                # NORTH-EAST
                subPie = pie.operator("wm.call_menu_pie", text='Divide...')
                subPie.name = "SUBPIE_MT_divide"
                # SOUTH-WEST
                deletePie = pie.operator("wm.call_menu_pie", text='Delete...')
                deletePie.name = "SUBPIE_MT_PieDelete"
                # SOUTH-EAST
                separatePie = pie.operator("wm.call_menu_pie", text='Split/Separate...')
                separatePie.name = "SUBPIE_MT_separate"

                # Static face menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                dropdown_menu.operator("mesh.bisect")
                dropdown_menu.operator("mesh.flip_normals")

        if context.mode == 'EDIT_CURVE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

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
            deletePie = pie.operator("wm.call_menu_pie", text='Delete...', icon = "RIGHTARROW_THIN")
            deletePie.name = "SUBPIE_MT_curveDelete"
            # SOUTH-EAST
            pie.operator("curve.separate")

        if context.mode == 'OBJECT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object
            sel = context.selected_objects

            if obj is not None and sel:
                
                # WEST & EAST
                if obj.type in {'MESH', 'CURVE', 'SURFACE'}:
                    pie.operator("wm.call_menu_pie", text='Shade...').name = "SUBPIE_MT_shadeObject"
                    pie.operator("wm.call_menu_pie", text='Link/Transfer...').name = "SUBPIE_MT_LinkTransfer"
                elif obj.type == 'ARMATURE':
                    arm = obj.data
                    pie.prop(arm, "pose_position", expand=True)
                else:
                    pie.separator()
                    pie.separator()

                # SOUTH
                pie.operator("wm.call_menu_pie", text='Apply...').name = "SUBPIE_MT_applyTransform"

                # NORTH
                pie.operator("object.join")
                
                # NORTH-WEST
                pie.operator("object.parent_set")

                # NORTH-EAST
                pie.operator("object.parent_clear")

                # SOUTH-WEST
                pie.operator("object.delete")

                # SOUTH-EAST
                pie.operator("mesh.separate", text='Separate Loose').type = 'LOOSE'

                
            else:
                pie.operator("wm.call_menu_pie", text="Mesh...").name = "SUBPIE_MT_add_mesh"
                pie.operator("wm.call_menu_pie", text="Curves & Text...").name = "SUBPIE_MT_add_curves_text"
                pie.operator("wm.call_menu_pie", text="Empties...").name = "SUBPIE_MT_add_empties"
                pie.operator("wm.call_menu_pie", text="Lights & Probes...").name = "SUBPIE_MT_add_lights_probes"
                pie.operator("wm.call_menu_pie", text="Camera & Images...").name = "SUBPIE_MT_add_cameras_speakers"
                pie.operator("wm.call_menu_pie", text="Grease Pencil...").name = "SUBPIE_MT_add_greasepencil"
                pie.operator("wm.call_menu_pie", text="Force Fields...").name = "SUBPIE_MT_add_forcefield"
                pie.operator("object.armature_add", text="Armature")

                '''
                # WEST
                pie.operator("mesh.primitive_cube_add")
                # EAST
                pie.operator("mesh.primitive_plane_add")
                # SOUTH
                pie.operator("mesh.primitive_uv_sphere_add")
                # NORTH
                pie.operator("mesh.primitive_cylinder_add")
                
                # NORTH-WEST
                pie.operator("mesh.primitive_torus_add")
                # NORTH-EAST
                pie.operator("mesh.primitive_circle_add")
                # SOUTH-WEST
                pie.operator("mesh.primitive_cone_add")
                # SOUTH-EAST
                pie.operator("mesh.primitive_ico_sphere_add")

                PUT MENU WITH CURVES
                # Static face menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
                dropdown_menu.operator("mesh.edge_split")
                '''

        # Straight from Blenders Pie Addon Sculpt 'W' Menu
        if context.mode == 'SCULPT':

            global brush_icons
            layout = self.layout
            pie = layout.menu_pie()
            pie.scale_y = 1.2

            # 4 - LEFT
            pie.operator(
                'wm.call_menu_pie',
                text="    Transform Brushes...",
                icon_value=brush_icons['snake_hook'],
            ).name = SUBPIE_MT_sculpt_brush_select_transform.bl_idname
            # 6 - RIGHT
            pie.operator(
                'wm.call_menu_pie',
                text="    Volume Brushes...",
                icon_value=brush_icons['blob'],
            ).name = SUBPIE_MT_sculpt_brush_select_volume.bl_idname
            # 2 - BOTTOM
            if blender_uses_brush_assets():
                sculpt_settings = context.tool_settings.sculpt
                brush = sculpt_settings.brush
                col = pie.column()
                brush_row = col.row()
                brush_row.scale_y = 0.75
                brush_row.scale_x = 0.15
                BrushAssetShelf.draw_popup_selector(
                    brush_row, context, brush, show_name=False
                )
                name_row = col.row().box()
                if brush:
                    name_row.label(text=brush.name)
            else:
                pie.separator()

            # 8 - TOP
            draw_brush_operator(pie, 'Mask', 'mask')
            # 7 - TOP - LEFT
            draw_brush_operator(pie, 'Grab', 'grab')
            # 9 - TOP - RIGHT
            draw_brush_operator(pie, 'Draw', 'draw')
            # 1 - BOTTOM - LEFT
            pie.operator(
                'wm.call_menu_pie',
                text="    Contrast Brushes...",
                icon_value=brush_icons['flatten'],
            ).name = SUBPIE_MT_sculpt_brush_select_contrast.bl_idname
            # 3 - BOTTOM - RIGHT
            pie.operator(
                'wm.call_menu_pie',
                text="    Special Brushes...",
                icon_value=brush_icons['draw_face_sets'],
            ).name = SUBPIE_MT_sculpt_brush_select_special.bl_idname

        if context.mode == 'POSE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object

            # WEST
            pie.operator("pose.copy")
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
            '''
            VIEW3D_MT_pose_context_menu
            layout.operator("anim.keyframe_insert", text="Insert Keyframe")
            layout.operator("anim.keyframe_insert_menu", text="Insert Keyframe with Keying Set").always_prompt = True

            layout.separator()

            layout.operator("pose.copy", icon='COPYDOWN')
            layout.operator("pose.paste", icon='PASTEDOWN').flipped = False
            layout.operator("pose.paste", icon='PASTEFLIPDOWN', text="Paste X-Flipped Pose").flipped = True

            layout.separator()

            props = layout.operator("wm.call_panel", text="Rename Active Bone...")
            props.name = "TOPBAR_PT_name"
            props.keep_open = False

            layout.separator()

            layout.operator("pose.push")
            layout.operator("pose.relax")
            layout.operator("pose.breakdown")
            layout.operator("pose.blend_to_neighbor")

            layout.separator()

            layout.operator("pose.paths_calculate", text="Calculate Motion Paths")
            layout.operator("pose.paths_clear", text="Clear Motion Paths")
            layout.operator("pose.paths_update", text="Update Armature Motion Paths")
            layout.operator("object.paths_update_visible", text="Update All Motion Paths")

            layout.separator()

            layout.operator("pose.hide").unselected = False
            layout.operator("pose.reveal")

            layout.separator()

            layout.operator("pose.user_transforms_clear")
            '''

        if context.mode == 'EDIT_ARMATURE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

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
            '''
            class VIEW3D_MT_armature_context_menu(Menu):
                bl_label = "Armature"

                def draw(self, context):
                    layout = self.layout

                    edit_object = context.edit_object
                    arm = edit_object.data

                    layout.operator_context = 'INVOKE_REGION_WIN'

                    # Add
                    layout.operator("armature.subdivide", text="Subdivide")
                    layout.operator("armature.duplicate_move", text="Duplicate")
                    layout.operator("armature.extrude_move")
                    if arm.use_mirror_x:
                        layout.operator("armature.extrude_forked")

                    layout.separator()

                    layout.operator("armature.fill")

                    layout.separator()

                    # Modify
                    layout.menu("VIEW3D_MT_mirror")
                    layout.menu("VIEW3D_MT_snap")
                    layout.operator("armature.symmetrize")
                    layout.operator("armature.switch_direction", text="Switch Direction")
                    layout.menu("VIEW3D_MT_edit_armature_names")

                    layout.separator()

                    layout.menu("VIEW3D_MT_edit_armature_parent")

                    layout.separator()

                    # Remove
                    layout.operator("armature.split")
                    layout.operator("armature.separate")
                    layout.operator("armature.dissolve")
                    layout.operator("armature.delete")


            class VIEW3D_MT_edit_armature_names(Menu):
                bl_label = "Names"

                def draw(self, _context):
                    layout = self.layout

                    layout.operator_context = 'EXEC_REGION_WIN'
                    layout.operator("armature.autoside_names", text="Auto-Name Left/Right").type = 'XAXIS'
                    layout.operator("armature.autoside_names", text="Auto-Name Front/Back").type = 'YAXIS'
                    layout.operator("armature.autoside_names", text="Auto-Name Top/Bottom").type = 'ZAXIS'
                    layout.operator("armature.flip_names", text="Flip Names")


            class VIEW3D_MT_edit_armature_parent(Menu):
                bl_label = "Parent"
                bl_translation_context = i18n_contexts.operator_default

                def draw(self, _context):
                    layout = self.layout

                    layout.operator("armature.parent_set", text="Make")
                    layout.operator("armature.parent_clear", text="Clear")


            class VIEW3D_MT_edit_armature_roll(Menu):
                bl_label = "Bone Roll"

                def draw(self, _context):
                    layout = self.layout

                    layout.operator_menu_enum("armature.calculate_roll", "type")

                    layout.separator()

                    layout.operator("transform.transform", text="Set Roll").mode = 'BONE_ROLL'
                    layout.operator("armature.roll_clear")


            class VIEW3D_MT_edit_armature_delete(Menu):
                bl_label = "Delete"

                def draw(self, _context):
                    layout = self.layout
                    layout.operator_context = 'EXEC_AREA'

                    layout.operator("armature.delete", text="Bones")

                    layout.separator()

                    layout.operator("armature.dissolve", text="Dissolve Bones")
            '''

def blender_uses_brush_assets():
    return 'asset_activate' in dir(bpy.ops.brush)


def draw_brush_operator(layout, brush_name: str, brush_icon: str = ""):
    """Draw a brush select operator in the provided UI element with the pre-4.3 icons.
    brush_name must match the name of the Brush Asset.
    brush_icon must match the name of a file in this add-on's icons folder.
    """
    if blender_uses_brush_assets():
        # 4.3
        op = layout.operator(
            'brush.asset_activate',
            text="     " + brush_name,
            icon_value=brush_icons.get(brush_icon, 0),
        )
        op.asset_library_type = 'ESSENTIALS'
        op.relative_asset_identifier = os.path.join(
            "brushes", "essentials_brushes-mesh_sculpt.blend", "Brush", brush_name
        )
    else:
        # Pre-4.3
        if brush_icon:
            op = layout.operator(
                "paint.brush_select",
                text="     " + brush_name,
                icon_value=brush_icons[brush_icon],
            )
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



registry = [
    SUBPIE_MT_merge, 
    SUBPIE_MT_connect, 
    SUBPIE_MT_extrudeFaces,
    SUBPIE_MT_separate,
    SUBPIE_MT_divide,
    SUBPIE_MT_smoothCurve,
    SUBPIE_MT_curveDelete,
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

def register():
    create_icons()

    register_hotkey(
        'wm.call_menu_pie_drag_only_cpie',
        op_kwargs={'name': 'VIEW3D_PIE_MT_context'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        key_cat="3D View",
    )
    register_hotkey(
        'wm.call_menu_pie_drag_only_cpie',
        op_kwargs={'name': 'VIEW3D_PIE_MT_context'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        key_cat="Sculpt",
    )

def unregister():
    release_icons()

"""
EMPTY PIE MENU

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.separator()
        # EAST
        pie.separator()
        # SOUTH
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

        # Static non pie menu
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y=1

"""
