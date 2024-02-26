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
    "description": "Context Sensitive Pie Menu",
    "author": "Bastian L Strube, Frederik Storm",
    "blender": (4, 0, 0),
    "location": "3D View",
    "category": "Interface"}

import os
import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)
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
        pie.operator("mesh.edge_split", text='Split By Vertice').type = 'VERT'
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
        pie.operator("wm.tool_set_by_id", text="Extrud To Cursor Tool").name = "builtin.extrude_to_cursor"
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
        op = pie.operator("object.transform_apply", text="All Trasnforms")
        op.location = True
        op.rotation = True
        op.scale = True

# Sub Pie Menu for mesh merge operators
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
                subPie.name = "PIE_MT_delete"
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
                subPie.name = "PIE_MT_delete"
                
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
                deletePie.name = "PIE_MT_delete"
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
            pie.separator()
            # EAST
            pie.operator("wm.call_menu_pie", text='Smooth...').name = "SUBPIE_MT_smoothCurve"
            # SOUTH
            pie.operator("curve.extrude_move")
            # NORTH
            pie.operator("transform.tilt")
            # NORTH-WEST
            pie.operator("curve.tilt_clear")
            # NORTH-EAST
            pie.operator("curve.subdivide")
            # SOUTH-WEST
            pie.operator("transform.transform", text='Radius').mode = 'CURVE_SHRINKFATTEN'
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

                # SOUTH
                pie.operator("wm.call_menu_pie", text='Apply...').name = "SUBPIE_MT_applyTransform"

                # NORTH
                pie.operator("object.join")
                
                # NORTH-WEST
                pie.operator("object.parent_set")

                # NORTH-EAST
                pie.operator("object.parent_clear")

                # SOUTH-WEST
                pie.separator()

                # SOUTH-EAST
                pie.operator("mesh.separate", text='Separate Loose').type = 'LOOSE'

                # Static non pie menu
                pie.separator()
                pie.separator()
                dropdown = pie.column()
                gap = dropdown.column()
                gap.separator()
                gap.scale_y = 8
                dropdown_menu = dropdown.box().column()
                dropdown_menu.scale_y=1
                

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

            #global brush_icons
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            pie.menu_contents("PIE_MT_sculpt")

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
            pie.separator()

            # SOUTH-WEST
            pie.separator()

            # SOUTH-EAST
            pie.separator()

            # Static non pie menu
            pie.separator()


classes = [
    SUBPIE_MT_merge, 
    SUBPIE_MT_connect, 
    SUBPIE_MT_extrudeFaces,
    SUBPIE_MT_separate,
    SUBPIE_MT_divide,
    SUBPIE_MT_smoothCurve,
    SUBPIE_MT_applyTransform,
    SUBPIE_MT_inbetweens,
    SUBPIE_MT_motionpaths,
    VIEW3D_PIE_MT_context,
]

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    #From this forum post: https://devtalk.blender.org/t/addon-shortcuts/2410/7
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "VIEW3D_PIE_MT_context"
        addon_keymaps.append((km, kmi))
""" This is from Keymap
    ("wm.call_menu_pie",
     {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
     {"properties":
      [("name", 'VIEW3D_PIE_context'),
"""
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()

    #bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_context")


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

"""
