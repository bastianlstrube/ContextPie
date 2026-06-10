# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu


###-----------------------------------------------------------------------------###
###                             CUSTOM OPERATORS                                ###
###-----------------------------------------------------------------------------###

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


###-----------------------------------------------------------------------------###
###                            MERGE / CONNECT / DIVIDE                         ###
###-----------------------------------------------------------------------------###

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
        # NORTH-WEST
        pie.operator("mesh.unsubdivide")
        # NORTH-EAST
        pie.operator("mesh.remove_doubles", text="By Distance")
        # SOUTH-WEST / SOUTH-EAST
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

        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode

        # WEST
        if is_edge_mode:
            pie.operator("mesh.edge_rotate", text="Rotate Clockwise").use_ccw = False
        else:
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
        if is_edge_mode:
            pie.operator("mesh.edge_rotate", text="Rotate CCW").use_ccw = True
        else:
            pie.separator()
        # SOUTH-EAST
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
            # W
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            # E
            pie.operator("mesh.subdivide", text='Subdivide')
            # S
            pie.operator("mesh.rip_move")
            # N
            pie.operator("mesh.poke")
            # NW
            pie.separator()
            # NE
            pie.operator("mesh.bevel", text='Bevel').affect = 'VERTICES'
            # SW
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            # SE
            pie.separator()
        elif is_edge_mode:
            # W
            pie.operator("transform.edge_bevelweight")
            # E
            pie.operator("mesh.subdivide", text='Subdivide')
            # S
            pie.operator("mesh.rip_move")
            # N
            pie.operator("mesh.mark_sharp", text="Mark Sharp").clear = False
            # NW
            pie.operator("mesh.mark_seam", text='Mark Seam').clear = False
            # NE
            pie.operator("mesh.bevel", text='Bevel').affect = 'EDGES'
            # SW
            pie.operator("transform.edge_crease")
            # SE
            pie.operator("mesh.edge_split")
        elif is_face_mode:
            pie.operator("mesh.quads_convert_to_tris", text='Triangulate')
            pie.operator("mesh.flip_normals")
            pie.operator("mesh.rip_move")
            pie.operator("mesh.poke")
            pie.operator("mesh.bisect")
            pie.operator("mesh.subdivide", text='Subdivide')
            pie.operator("mesh.tris_convert_to_quads", text='Tris to Quads')
            pie.operator("mesh.split")

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


###-----------------------------------------------------------------------------###
###                            DELETE SUB PIE MENUS                             ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_delete_vertex(Menu):
    bl_label = "Delete Vertices"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("mesh.delete", text="Delete Vertices", icon='VERTEXSEL').type = 'VERT'
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("mesh.dissolve_verts", text="Dissolve Split Faces", icon='MOD_BEVEL').use_face_split = True
        # NORTH
        pie.separator()
        # NORTH-WEST / NORTH-EAST
        pie.separator()
        pie.separator()
        # SOUTH-WEST
        pie.operator("mesh.dissolve_verts", text="Dissolve Vertices", icon='SNAP_VERTEX').use_face_split = False
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_delete_edge(Menu):
    bl_label = "Delete Edges"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("mesh.delete", text="Delete Edges", icon='EDGESEL').type = 'EDGE'
        # EAST
        pie.operator("mesh.dissolve_limited", text="Limited Dissolve", icon='STICKY_UVS_LOC')
        # SOUTH
        pie.operator("mesh.delete_edgeloop", text="Delete Edge Loops", icon='NONE')
        # NORTH
        pie.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
        # NORTH-WEST
        pie.operator("mesh.dissolve_edges", text="Dissolve Keep Vert", icon='MOD_CAST').use_verts = False
        # NORTH-EAST
        pie.operator("mesh.mark_seam", text='Clear Seam').clear = True
        # SOUTH-WEST
        pie.operator("mesh.dissolve_edges", text="Dissolve Edges", icon='SNAP_EDGE').use_verts = True
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_delete_face(Menu):
    bl_label = "Delete Faces"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("mesh.dissolve_faces", text="Dissolve Faces", icon='SNAP_FACE')
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("mesh.delete", text="Only Edge & Faces", icon='NONE').type = 'EDGE_FACE'
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.operator("mesh.delete", text="Only Faces", icon='UV_FACESEL').type = 'ONLY_FACE'
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("mesh.delete", text="Delete Faces", icon='FACESEL').type = 'FACE'
        # SOUTH-EAST
        pie.separator()


###-----------------------------------------------------------------------------###
###                              DRAW FUNCTIONS                                 ###
###-----------------------------------------------------------------------------###

def draw_context_editmesh(pie, context):
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_vert_mode:
        _draw_vert(pie, context)
    elif is_edge_mode:
        _draw_edge(pie, context)
    elif is_face_mode:
        _draw_face(pie, context)


def _draw_vert(pie, context):
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
    pie.operator("wm.call_menu_pie", text="Delete...", icon='TRASH').name = "SUBPIE_MT_delete_vertex"
    # SOUTH-EAST
    pie.operator("transform.vert_slide", text="Slide Vertex")

def _draw_edge(pie, context):
    # WEST
    pie.operator("mesh.set_knife_tool", text="Knife")
    # EAST
    pie.operator("wm.call_menu_pie", text='Connect/Rotate...', icon="TRIA_RIGHT").name = "SUBPIE_MT_connect"
    # SOUTH
    pie.operator("mesh.extrude_edges_move", text="Extrude Edges")
    # NORTH
    pie.operator("wm.call_menu_pie", text='Merge...', icon="TRIA_UP").name = "SUBPIE_MT_merge"
    # NORTH-WEST
    pie.operator("mesh.set_loopcut_tool", text="Insert Loop")
    # NORTH-EAST
    pie.operator("wm.call_menu_pie", text='Divide/Mark...', icon="TRIA_RIGHT").name = "SUBPIE_MT_divide"
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text="Delete/Clear...", icon='TRASH').name = "SUBPIE_MT_delete_edge"
    # SOUTH-EAST
    pie.operator("transform.edge_slide", text="Slide Edge")

def _draw_face(pie, context):
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
    pie.operator("wm.call_menu_pie", text='Divide/Normals...', icon="TRIA_RIGHT").name = "SUBPIE_MT_divide"
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text="Delete...", icon='TRASH').name = "SUBPIE_MT_delete_face"
    # SOUTH-EAST
    pie.operator("transform.shrink_fatten")


###-----------------------------------------------------------------------------###
###                              REGISTRY                                       ###
###-----------------------------------------------------------------------------###

registry = [
    SetKnifeTool,
    SetLoopCutTool,
    SUBPIE_MT_merge,
    SUBPIE_MT_connect,
    SUBPIE_MT_divide,
    SUBPIE_MT_extrudeFaces,
    SUBPIE_MT_delete_vertex,
    SUBPIE_MT_delete_edge,
    SUBPIE_MT_delete_face,
]

if "bl_ext.blender_org.looptools" in bpy.context.preferences.addons:
    registry.append(SUBPIE_MT_edit_mesh_looptools)
