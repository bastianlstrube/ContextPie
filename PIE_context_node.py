import bpy
from bpy.types import Menu


# ADD GEOMETRY NODES SUB MENUS ###############################################################

class SUBPIE_MT_gn_mesh(Menu):
    bl_label = "Mesh Nodes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Cube", icon='MESH_CUBE').type = 'GeometryNodeMeshCube'
        pie.operator("node.add_node", text="Circle", icon='MESH_CIRCLE').type = 'GeometryNodeMeshCircle'
        pie.operator("node.add_node", text="Cylinder", icon='MESH_CYLINDER').type = 'GeometryNodeMeshCylinder'
        pie.operator("node.add_node", text="UV Sphere", icon='MESH_UVSPHERE').type = 'GeometryNodeMeshUVSphere'
        pie.operator("node.add_node", text="Extrude Mesh", icon='MESH_DATA').type = 'GeometryNodeExtrudeMesh'
        pie.operator("node.add_node", text="Subdivide Mesh", icon='MESH_DATA').type = 'GeometryNodeSubdivideMesh'
        pie.operator("node.add_node", text="Flip Faces", icon='MESH_DATA').type = 'GeometryNodeFlipFaces'
        pie.operator("node.add_node", text="Mesh to Curve", icon='CURVE_DATA').type = 'GeometryNodeMeshToCurve'

class SUBPIE_MT_gn_curve(Menu):
    bl_label = "Curve Nodes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Bezier Segment", icon='CURVE_BEZCURVE').type = 'GeometryNodeCurvePrimitiveBezierSegment'
        pie.operator("node.add_node", text="Curve Circle", icon='CURVE_BEZCIRCLE').type = 'GeometryNodeCurvePrimitiveCircle'
        pie.operator("node.add_node", text="Curve Line", icon='CURVE_PATH').type = 'GeometryNodeCurvePrimitiveLine'
        pie.operator("node.add_node", text="Resample Curve", icon='CURVE_DATA').type = 'GeometryNodeResampleCurve'
        pie.operator("node.add_node", text="Trim Curve", icon='CURVE_DATA').type = 'GeometryNodeTrimCurve'
        pie.operator("node.add_node", text="Fill Curve", icon='MESH_DATA').type = 'GeometryNodeFillCurve'
        pie.operator("node.add_node", text="Curve to Mesh", icon='MESH_DATA').type = 'GeometryNodeCurveToMesh'

class SUBPIE_MT_gn_utilities(Menu):
    bl_label = "Utilities & Math"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath'
        pie.operator("node.add_node", text="Vector Math", icon='CON_KINEMATIC').type = 'ShaderNodeVectorMath'
        pie.operator("node.add_node", text="Boolean Math", icon='CON_KINEMATIC').type = 'FunctionNodeBooleanMath'
        pie.operator("node.add_node", text="Random Value", icon='RNDCURVE').type = 'FunctionNodeRandomValue'
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'ShaderNodeValToRGB'
        pie.operator("node.add_node", text="Float Curve", icon='CURVE_DATA').type = 'ShaderNodeFloatCurve'
        pie.operator("node.add_node", text="Switch", icon='ARROW_LEFTRIGHT').type = 'GeometryNodeSwitch'

class SUBPIE_MT_gn_io(Menu):
    bl_label = "Input & Output"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Group Input", icon='FORWARD').type = 'NodeGroupInput'
        pie.operator("node.add_node", text="Group Output", icon='BACK').type = 'NodeGroupOutput'
        pie.operator("node.add_node", text="Value", icon='VALUE_PROP').type = 'ShaderNodeValue'
        pie.operator("node.add_node", text="Integer", icon='LINENUMBERS_ON').type = 'FunctionNodeInputInt'
        pie.operator("node.add_node", text="Boolean", icon='CHECKBOX_HLT').type = 'FunctionNodeInputBool'
        pie.operator("node.add_node", text="Object Info", icon='OBJECT_DATA').type = 'GeometryNodeObjectInfo'
        pie.operator("node.add_node", text="Collection Info", icon='OUTLINER_COLLECTION').type = 'GeometryNodeCollectionInfo'

class SUBPIE_MT_gn_geometry_instances(Menu):
    bl_label = "Geometry & Instances"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Join Geometry", icon='FRAME_NEXT').type = 'GeometryNodeJoinGeometry'
        pie.operator("node.add_node", text="Transform", icon='ORIENTATION_GLOBAL').type = 'GeometryNodeTransform'
        pie.operator("node.add_node", text="Set Position", icon='SNAP_GRID').type = 'GeometryNodeSetPosition'
        pie.operator("node.add_node", text="Instance on Points", icon='PARTICLE_DATA').type = 'GeometryNodeInstanceOnPoints'
        pie.operator("node.add_node", text="Realize Instances", icon='OUTLINER_OB_GROUP_INSTANCE').type = 'GeometryNodeRealizeInstances'
        pie.operator("node.add_node", text="Separate Geometry", icon='MESH_DATA').type = 'GeometryNodeSeparateGeometry'
        pie.operator("node.add_node", text="Delete Geometry", icon='CANCEL').type = 'GeometryNodeDeleteGeometry'

class SUBPIE_MT_gn_attributes(Menu):
    bl_label = "Attributes & Textures"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Named Attribute", icon='SPREADSHEET').type = 'GeometryNodeInputNamedAttribute'
        pie.operator("node.add_node", text="Store Named Attribute", icon='SPREADSHEET').type = 'GeometryNodeStoreNamedAttribute'
        pie.operator("node.add_node", text="Capture Attribute", icon='SPREADSHEET').type = 'GeometryNodeCaptureAttribute'
        pie.operator("node.add_node", text="Noise Texture", icon='TEXTURE').type = 'ShaderNodeTexNoise'
        pie.operator("node.add_node", text="Voronoi Texture", icon='TEXTURE').type = 'ShaderNodeTexVoronoi'
        pie.operator("node.add_node", text="Gradient Texture", icon='TEXTURE').type = 'ShaderNodeTexGradient'

class SUBPIE_MT_gn_points_volumes(Menu):
    bl_label = "Points & Volumes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Distribute Points on Faces", icon='PARTICLE_DATA').type = 'GeometryNodeDistributePointsOnFaces'
        pie.operator("node.add_node", text="Points", icon='PARTICLE_DATA').type = 'GeometryNodePoints'
        pie.operator("node.add_node", text="Points to Volume", icon='VOLUME_DATA').type = 'GeometryNodePointsToVolume'
        pie.operator("node.add_node", text="Volume to Mesh", icon='MESH_DATA').type = 'GeometryNodeVolumeToMesh'
        pie.operator("node.add_node", text="Points to Vertices", icon='VERTEXSEL').type = 'GeometryNodePointsToVertices'

class SUBPIE_MT_gn_materials(Menu):
    bl_label = "Materials"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Set Material", icon='MATERIAL').type = 'GeometryNodeSetMaterial'
        pie.operator("node.add_node", text="Replace Material", icon='MATERIAL').type = 'GeometryNodeReplaceMaterial'
        pie.operator("node.add_node", text="Material Selection", icon='MATERIAL').type = 'GeometryNodeMaterialSelection'
        pie.operator("node.add_node", text="Set Material Index", icon='MATERIAL').type = 'GeometryNodeSetMaterialIndex'

# MAIN NODE CONTEXT PIE MENU ######################################################################

class NODE_PIE_MT_context(Menu):
    bl_idname = "NODE_PIE_MT_context_pie"
    bl_label = "Node Context Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        pie = layout.menu_pie()

        # Ensure we are in a node editor and there is an active tree
        if context.space_data.type != 'NODE_EDITOR' or not context.space_data.node_tree:
            return

        selected_nodes = context.selected_nodes
        num_selected = len(selected_nodes)

        if num_selected == 0:
            self.draw_no_nodes(pie, context)
        elif num_selected == 1:
            self.draw_single_node(pie, context)
        else:
            self.draw_multi_nodes(pie, context)

    def draw_no_nodes(self, pie, context):
        # WEST
        pie.operator("wm.call_menu_pie", text="Mesh Nodes...", icon='MESH_DATA').name = "SUBPIE_MT_gn_mesh"
        # EAST
        pie.operator("wm.call_menu_pie", text="Curve Nodes...", icon='CURVE_DATA').name = "SUBPIE_MT_gn_curve"
        # SOUTH
        pie.operator("wm.call_menu_pie", text="Utilities & Math...", icon='CON_KINEMATIC').name = "SUBPIE_MT_gn_utilities"
        # NORTH
        pie.operator("wm.call_menu_pie", text="Input & Output...", icon='NODETREE').name = "SUBPIE_MT_gn_io"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Geometry & Instances...", icon='GROUP_VERTEX').name = "SUBPIE_MT_gn_geometry_instances"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text="Attributes & Textures...", icon='SPREADSHEET').name = "SUBPIE_MT_gn_attributes"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text="Points & Volumes...", icon='PARTICLE_DATA').name = "SUBPIE_MT_gn_points_volumes"
        # SOUTH-EAST
        pie.operator("wm.call_menu_pie", text="Materials...", icon='MATERIAL').name = "SUBPIE_MT_gn_materials"

    def draw_single_node(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST
        pie.operator("node.delete_reconnect", text="Delete & Reconnect", icon='X')
        # EAST
        pie.operator("node.links_detach", text="Detach Links", icon='UNLINKED')
        # SOUTH
        pie.operator("node.mute_toggle", text="Mute / Unmute", icon='HIDE_OFF')
        # NORTH
        if nw_loaded:
            pie.operator("node.nw_preview_node", text="Preview Node", icon='HIDE_ON')
        else:
            pie.operator("node.view_toggle", text="Toggle Viewer", icon='HIDE_ON')
        # NORTH-WEST
        pie.operator("node.duplicate_move", text="Duplicate", icon='DUPLICATE')
        # NORTH-EAST
        pie.operator("node.duplicate_move_keep_inputs", text="Duplicate (Keep Inputs)", icon='DUPLICATE')
        # SOUTH-WEST
        pie.operator("node.delete", text="Delete", icon='TRASH')
        # SOUTH-EAST
        if nw_loaded:
            pie.operator("node.nw_add_reroutes", text="Add Reroutes", icon='NODE')
        else:
            pie.operator("node.clipboard_copy", text="Copy Node", icon='COPYDOWN')

        # Static dropdown menu for single node settings
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        dropdown_menu.operator("node.nw_copy_settings", text="Copy Settings") if nw_loaded else None
        dropdown_menu.operator("node.hide_toggle", text="Toggle Hidden")
        dropdown_menu.operator("node.options_toggle", text="Toggle Options")

    def draw_multi_nodes(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST
        pie.operator("node.delete_reconnect", text="Delete & Reconnect", icon='X')
        # EAST
        if nw_loaded:
            pie.operator("node.nw_align_nodes", text="Align Nodes", icon='ALIGN_JUSTIFY')
        else:
            pie.operator("node.translate_attach", text="Attach Nodes", icon='LINKED')
        # SOUTH
        pie.operator("node.join", text="Frame Selected", icon='FRAME_DATA') # Wraps nodes in a Frame
        # NORTH
        if nw_loaded:
            # This handles Join Geometry, Math, Mix RGB, etc. based on selected socket types
            pie.operator("node.nw_merge_nodes", text="Merge / Join Nodes", icon='TRACKING_FORWARDS')
        else:
            # Fallback if NW isn't loaded (requires manual node creation)
            pie.operator("node.add_node", text="Add Join Geometry", icon='TRACKING_FORWARDS').type = 'GeometryNodeJoinGeometry'
        # NORTH-WEST
        pie.operator("node.duplicate_move", text="Duplicate", icon='DUPLICATE')
        # NORTH-EAST
        if nw_loaded:
            pie.operator("node.nw_swap_links", text="Swap Links", icon='FILE_REFRESH')
        else:
            pie.operator("node.links_detach", text="Detach Links", icon='UNLINKED')
        # SOUTH-WEST
        pie.operator("node.delete", text="Delete", icon='TRASH')
        # SOUTH-EAST
        pie.operator("node.mute_toggle", text="Mute / Unmute Selected", icon='HIDE_OFF')

        # Static dropdown menu for multi-node operations
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        if nw_loaded:
            dropdown_menu.operator("node.nw_frame_selected", text="NW Frame Selected")
            dropdown_menu.operator("node.nw_clear_viewer", text="Clear Viewers")
            dropdown_menu.operator("node.nw_bg_sync", text="Sync Background")


# REGISTRATION ######################################################################

registry = [
    SUBPIE_MT_gn_mesh,
    SUBPIE_MT_gn_curve,
    SUBPIE_MT_gn_utilities,
    SUBPIE_MT_gn_io,
    SUBPIE_MT_gn_geometry_instances,
    SUBPIE_MT_gn_attributes,
    SUBPIE_MT_gn_points_volumes,
    SUBPIE_MT_gn_materials,
    NODE_PIE_MT_context,
]

def register():
    # If your main file handles the bpy.utils.register_class loop over the registry,
    # you just need to add the hotkey binding here:
    
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=NODE_PIE_MT_context.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="Node Editor",
        on_drag=False,
    )


def unregister():
    # Assuming your main unregister function handles the class unregistration 
    # and hotkey removal via your custom wrapper.
    pass