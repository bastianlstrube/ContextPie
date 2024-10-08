# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Context Pie: 'Shift + Right Mouse'",
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}

import os
import bpy
from bpy.types import Menu
from .hotkeys import register_hotkey

from bpy.app.translations import contexts as i18n_contexts

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
        pie.separator()
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
        pie.separator()
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

# Sub Pie for mesh face/edge divisions
class SUBPIE_MT_divide(Menu):
    bl_label = "Divide"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
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

# Sub Pie for curve operators
class SUBPIE_MT_smoothCurve(Menu):
    bl_label = "Smooth"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("curve.smooth_weight")
        # EAST
        pie.operator("curve.smooth")
        # SOUTH
        pie.operator("curve.smooth_radius")
        # NORTH
        pie.operator("curve.smooth_tilt")

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

# Sub Pie Menu for mesh merge operators
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

# Sub Pie Menu for Delete, ripped directly from 3D Viewport Pie Menus
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

# Pie Sculpt More Brushes
class SUBPIE_MT_SculptMoreBrushes(Menu):
    bl_label = "More Brushes"

    def draw(self, context):
        global brush_icons
        layout = self.layout
        pie = layout.menu_pie()
        pie.scale_y = 1.2

        # WEST
        pie.operator("paint.brush_select", text='    Mask',
                        icon_value=brush_icons["mask"]).sculpt_tool = 'MASK'
        # EAST
        pie.operator("paint.brush_select", text='    Fill/Deepen',
                        icon_value=brush_icons["fill"]).sculpt_tool = 'FILL'
        # SOUTH
        pie.operator("paint.brush_select", text='    Smooth',
                        icon_value=brush_icons["smooth"]).sculpt_tool = 'SMOOTH'
        # NORTH
        pie.operator("paint.brush_select", text='    Layer',
                        icon_value=brush_icons["layer"]).sculpt_tool = 'LAYER'
        # NORTH-WEST
        pie.operator("paint.brush_select", text='    Pinch/Magnify',
                        icon_value=brush_icons["pinch"]).sculpt_tool = 'PINCH'
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("paint.brush_select", text='    Flatten',
                        icon_value=brush_icons["flatten"]).sculpt_tool = 'FLATTEN'
        # SOUTH-EAST
        pie.operator("paint.brush_select", text='    Scrape/Peaks',
                        icon_value=brush_icons["scrape"]).sculpt_tool = 'SCRAPE'

# Pie Sculpt Grab Bruhes
class SUBPIE_MT_SculptGrab(Menu):
    bl_label = "Grab Brushes"

    def draw(self, context):
        global brush_icons
        layout = self.layout
        pie = layout.menu_pie()
        pie.scale_y = 1.2
        # WEST
        pie.operator("paint.brush_select",
                        text='    Snakehook', icon_value=brush_icons["snake_hook"]).sculpt_tool = 'SNAKE_HOOK'
        # EAST
        pie.operator("paint.brush_select",
                        text='    Nudge', icon_value=brush_icons["nudge"]).sculpt_tool = 'NUDGE'
        # SOUTH
        pie.operator("paint.brush_select",
                        text='    Thumb', icon_value=brush_icons["thumb"]).sculpt_tool = 'THUMB'
        # NORTH
        pie.operator("paint.brush_select",
                        text='    Rotate', icon_value=brush_icons["rotate"]).sculpt_tool = 'ROTATE'
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.operator("paint.brush_select",
                        text='    Grab', icon_value=brush_icons["grab"]).sculpt_tool = 'GRAB'




# Main Context Sensitive Pie Menu
class VIEW3D_PIE_MT_context(Menu):
    bl_label    = "Context Pie"

    def draw(self, context):

        if context.mode == 'EDIT_MESH':

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

            is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
            selected_verts_len, selected_edges_len, selected_faces_len = count_selected_items_for_objects_in_mode()

            del count_selected_items_for_objects_in_mode

            # If nothing is selected
            # (disabled for now until it can be made more useful).
            '''
            # If nothing is selected
            if not (selected_verts_len or selected_edges_len or selected_faces_len):
                layout.menu("VIEW3D_PIE_mesh_add", text="Add")

                return
            '''

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
                pie.operator("mesh.bevel", text="Bevel Vertices").affect = 'VERTICES'
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
                dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
                dropdown_menu.operator("mesh.bisect", text = "Bisect")
                dropdown_menu.operator("transform.edge_crease", text = "Crease Tool")
                separatePie = dropdown_menu.operator("wm.call_menu_pie", text='Separate...').name = "SUBPIE_MT_separate"
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Crease Tool", icon="ops.generic.select")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Connect Components")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Circularize Component")
                


            elif is_edge_mode:
                #render = context.scene.render

                # WEST
                pie.operator("mesh.knife_tool", text="Knife")
            
                # EAST
                subPie = pie.operator("wm.call_menu_pie", text='Connect...')
                subPie.name = "SUBPIE_MT_connect"

                # SOUTH
                pie.operator("mesh.extrude_edges_move", text="Extrude Edges")

                # NORTH
                subPie = pie.operator("wm.call_menu_pie", text='Merge...')
                subPie.name = "SUBPIE_MT_merge"
                #pie.operator("mesh.merge", text="Merge")
                
                
                # NORTH-WEST
                pie.operator("mesh.loopcut_slide", text="Insert Loop")
                
                # NORTH-EAST
                pie.operator("mesh.bevel", text="Bevel Edges").affect = 'EDGES'

                # SOUTH-WEST
                subPie = pie.operator("wm.call_menu_pie", text='Delete...')
                subPie.name = "SUBPIE_MT_PieDelete"
                
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
                dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
                dropdown_menu.operator("transform.edge_crease", text = "Crease Tool")
                dropdown_menu.operator("mesh.mark_sharp", text = "Mark Sharp").clear = False
                dropdown_menu.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
                dropdown_menu.operator("mesh.subdivide", text = "Add Division To Edge")
                dropdown_menu.operator("mesh.edge_split")
                dropdown_menu.operator("mesh.edge_rotate").use_ccw=False
                dropdown_menu.operator("mesh.edge_rotate").use_ccw=True
                dropdown_menu.operator("mesh.rip_move", text = "Detach Components")
                subPie = dropdown_menu.operator("wm.call_menu_pie", text='Separate')
                subPie.name = "SUBPIE_MT_separate"
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Circularize Component")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Edit Edge Flow")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Offset Edge Loop Tool")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Insert Edgeloop Tool")
                #dropdown_menu.operator("mesh.primitive_cube_add", text = "Connect Components")
                


            elif is_face_mode:

                # WEST
                pie.operator("mesh.knife_tool", text="Knife")
                # EAST
                pie.operator("mesh.unsubdivide")
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
                dropdown_menu.operator("wm.toolbar", text = "Handy Tools", icon="TOOL_SETTINGS")
                dropdown_menu.operator("mesh.bisect")
                dropdown_menu.operator("mesh.flip_normals")
                dropdown_menu.operator("mesh.rip_move", text = "Extract Faces")

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

                    pie.operator("object.shade_smooth")
                    pie.operator("object.shade_flat")
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
                '''
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
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            pie.scale_y = 1.2
            # 4 - LEFT
            pie.operator("paint.brush_select",
                        text="    Crease", icon_value=brush_icons["crease"]).sculpt_tool = 'CREASE'
            # 6 - RIGHT
            pie.operator("paint.brush_select",
                        text="    Blob", icon_value=brush_icons["blob"]).sculpt_tool = 'BLOB'
            # 2 - BOTTOM
            subPie = pie.operator("wm.call_menu_pie", text='More Brushes...', icon = "RIGHTARROW_THIN")
            subPie.name = "SUBPIE_MT_SculptMoreBrushes"

            # 8 - TOP
            pie.operator("paint.brush_select",
                        text="    Draw", icon_value=brush_icons["draw"]).sculpt_tool = 'DRAW'
            # 7 - TOP - LEFT
            pie.operator("paint.brush_select",
                        text="    Clay", icon_value=brush_icons["clay"]).sculpt_tool = 'CLAY'
            # 9 - TOP - RIGHT
            pie.operator("paint.brush_select",
                        text="    Clay Strips", icon_value=brush_icons["clay_strips"]).sculpt_tool = 'CLAY_STRIPS'
            # 1 - BOTTOM - LEFT
            pie.operator("paint.brush_select",
                        text="    Inflate/Deflate", icon_value=brush_icons["inflate"]).sculpt_tool = 'INFLATE'
            # 3 - BOTTOM - RIGHT
            subPie = pie.operator("wm.call_menu_pie", text='    Grab Brushes...', icon_value=brush_icons["grab"])
            subPie.name = "SUBPIE_MT_SculptGrab"

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
            pie.separator()
            # NORTH-EAST
            pie.operator("pose.paste", text='Paste Flipped').flipped = True
            # SOUTH-WEST
            pie.separator()
            # SOUTH-EAST
            pie.separator()


# Brush Icons for Sculpt Menu
brush_icons = {}

def create_icons():
    global brush_icons
    icons_directory = bpy.utils.system_resource('DATAFILES', path="icons")
    brushes = (
        "crease", "blob", "smooth", "draw", "clay", "clay_strips", "inflate", "grab",
        "nudge", "thumb", "snake_hook", "rotate", "flatten", "scrape", "fill", "pinch",
        "layer", "mask",
    )
    for brush in brushes:
        filename = os.path.join(icons_directory, f"brush.sculpt.{brush}.dat")
        icon_value = bpy.app.icons.new_triangles_from_file(filename)
        brush_icons[brush] = icon_value

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
    SUBPIE_MT_inbetweens,
    SUBPIE_MT_motionpaths,
    SUBPIE_MT_PieDelete,
    SUBPIE_MT_SculptMoreBrushes,
    SUBPIE_MT_SculptGrab,
    VIEW3D_PIE_MT_context,
]

addon_keymaps = []

def register():
    create_icons()

    register_hotkey(
        'wm.call_menu_pie',
        op_kwargs={'name': 'VIEW3D_PIE_MT_context'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        key_cat="3D View",
    )
    register_hotkey(
        'wm.call_menu_pie',
        op_kwargs={'name': 'VIEW3D_PIE_MT_context'},
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        key_cat="Sculpt",
    )

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
