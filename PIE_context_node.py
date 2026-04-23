import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# ==============================================================================
# 1. GEOMETRY NODES SUB-MENUS
# ==============================================================================

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
        pie.operator("node.add_node", text="Join Geometry").type = 'GeometryNodeJoinGeometry'
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

# ==============================================================================
# 1. SHADER NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_sh_input(Menu):
    bl_label = "Input"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Texture Coordinate", icon='TEXTURE').type = 'ShaderNodeTexCoord'
        pie.operator("node.add_node", text="Geometry", icon='MESH_DATA').type = 'ShaderNodeNewGeometry'
        pie.operator("node.add_node", text="Object Info", icon='OBJECT_DATA').type = 'ShaderNodeObjectInfo'
        pie.operator("node.add_node", text="Value", icon='VALUE_PROP').type = 'ShaderNodeValue'
        pie.operator("node.add_node", text="RGB", icon='COLOR').type = 'ShaderNodeRGB'
        pie.operator("node.add_node", text="Attribute", icon='SPREADSHEET').type = 'ShaderNodeAttribute'

class SUBPIE_MT_sh_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Material Output", icon='MATERIAL').type = 'ShaderNodeOutputMaterial'
        pie.operator("node.add_node", text="Light Output", icon='LIGHT').type = 'ShaderNodeOutputLight'
        pie.operator("node.add_node", text="World Output", icon='WORLD').type = 'ShaderNodeOutputWorld'
        pie.operator("node.add_node", text="AOV Output", icon='RENDER_RESULT').type = 'ShaderNodeOutputAOV'

class SUBPIE_MT_sh_shader(Menu):
    bl_label = "Shader"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Principled BSDF", icon='SHADING_RENDERED').type = 'ShaderNodeBsdfPrincipled'
        pie.operator("node.add_node", text="Emission", icon='LIGHT').type = 'ShaderNodeEmission'
        pie.operator("node.add_node", text="Mix Shader", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeMixShader'
        pie.operator("node.add_node", text="Transparent BSDF", icon='SHADING_WIRE').type = 'ShaderNodeBsdfTransparent'
        pie.operator("node.add_node", text="Glass BSDF", icon='SHADING_RENDERED').type = 'ShaderNodeBsdfGlass'
        pie.operator("node.add_node", text="Volume Scatter", icon='VOLUME_DATA').type = 'ShaderNodeVolumeScatter'

class SUBPIE_MT_sh_texture(Menu):
    bl_label = "Texture"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Image Texture", icon='IMAGE_DATA').type = 'ShaderNodeTexImage'
        pie.operator("node.add_node", text="Noise Texture", icon='TEXTURE').type = 'ShaderNodeTexNoise'
        pie.operator("node.add_node", text="Voronoi Texture", icon='TEXTURE').type = 'ShaderNodeTexVoronoi'
        pie.operator("node.add_node", text="Gradient Texture", icon='TEXTURE').type = 'ShaderNodeTexGradient'
        pie.operator("node.add_node", text="Wave Texture", icon='TEXTURE').type = 'ShaderNodeTexWave'

class SUBPIE_MT_sh_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'ShaderNodeValToRGB'
        pie.operator("node.add_node", text="Mix Color", icon='COLOR').type = 'ShaderNodeMix'
        pie.operator("node.add_node", text="RGB Curves", icon='CURVE_DATA').type = 'ShaderNodeRGBCurve'
        pie.operator("node.add_node", text="Hue/Saturation", icon='COLOR').type = 'ShaderNodeHueSaturation'
        pie.operator("node.add_node", text="Invert Color", icon='COLOR').type = 'ShaderNodeInvert'

class SUBPIE_MT_sh_vector(Menu):
    bl_label = "Vector"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Mapping", icon='ORIENTATION_GLOBAL').type = 'ShaderNodeMapping'
        pie.operator("node.add_node", text="Bump", icon='FORCE_TEXTURE').type = 'ShaderNodeBump'
        pie.operator("node.add_node", text="Displacement", icon='FORCE_TEXTURE').type = 'ShaderNodeDisplacement'
        pie.operator("node.add_node", text="Normal Map", icon='NORMALS_FACE').type = 'ShaderNodeNormalMap'
        pie.operator("node.add_node", text="Vector Math", icon='CON_KINEMATIC').type = 'ShaderNodeVectorMath'

class SUBPIE_MT_sh_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath'
        pie.operator("node.add_node", text="Map Range", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeMapRange'
        pie.operator("node.add_node", text="Separate Color", icon='COLOR').type = 'ShaderNodeSeparateColor'
        pie.operator("node.add_node", text="Combine Color", icon='COLOR').type = 'ShaderNodeCombineColor'
        pie.operator("node.add_node", text="Separate XYZ", icon='AXIS_SIDE').type = 'ShaderNodeSeparateXYZ'
        pie.operator("node.add_node", text="Combine XYZ", icon='AXIS_SIDE').type = 'ShaderNodeCombineXYZ'

# ==============================================================================
# 2. COMPOSITOR NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_co_input(Menu):
    bl_label = "Input"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Render Layers", icon='RENDERLAYERS').type = 'CompositorNodeRLayers'
        pie.operator("node.add_node", text="Image", icon='IMAGE_DATA').type = 'CompositorNodeImage'
        pie.operator("node.add_node", text="Movie Clip", icon='TRACKER').type = 'CompositorNodeMovieClip'
        pie.operator("node.add_node", text="Value", icon='VALUE_PROP').type = 'CompositorNodeValue'
        pie.operator("node.add_node", text="RGB", icon='COLOR').type = 'CompositorNodeRGB'

class SUBPIE_MT_co_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Composite", icon='RENDER_RESULT').type = 'CompositorNodeComposite'
        pie.operator("node.add_node", text="Viewer", icon='HIDE_ON').type = 'CompositorNodeViewer'
        pie.operator("node.add_node", text="File Output", icon='FILE_IMAGE').type = 'CompositorNodeOutputFile'

class SUBPIE_MT_co_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Mix", icon='COLOR').type = 'CompositorNodeMixRGB'
        pie.operator("node.add_node", text="Alpha Over", icon='IMAGE_ALPHA').type = 'CompositorNodeAlphaOver'
        pie.operator("node.add_node", text="Color Balance", icon='COLOR').type = 'CompositorNodeColorBalance'
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'CompositorNodeValToRGB'
        pie.operator("node.add_node", text="Hue Saturation Value", icon='COLOR').type = 'CompositorNodeHueSat'

class SUBPIE_MT_co_filter(Menu):
    bl_label = "Filter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Blur", icon='MOD_SMOOTH').type = 'CompositorNodeBlur'
        pie.operator("node.add_node", text="Glare", icon='LIGHT_SUN').type = 'CompositorNodeGlare'
        pie.operator("node.add_node", text="Directional Blur", icon='MOD_SMOOTH').type = 'CompositorNodeDBlur'
        pie.operator("node.add_node", text="Sun Beams", icon='LIGHT_SUN').type = 'CompositorNodeSunBeams'
        pie.operator("node.add_node", text="Pixelate", icon='TEXTURE').type = 'CompositorNodePixelate'

class SUBPIE_MT_co_transform(Menu):
    bl_label = "Transform"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Transform", icon='ORIENTATION_GLOBAL').type = 'CompositorNodeTransform'
        pie.operator("node.add_node", text="Translate", icon='NODE').type = 'CompositorNodeTranslate'
        pie.operator("node.add_node", text="Scale", icon='NODE').type = 'CompositorNodeScale'
        pie.operator("node.add_node", text="Rotate", icon='NODE').type = 'CompositorNodeRotate'
        pie.operator("node.add_node", text="Flip", icon='NODE').type = 'CompositorNodeFlip'

class SUBPIE_MT_co_matte(Menu):
    bl_label = "Matte & Mask"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Cryptomatte", icon='RESTRICT_COLOR_OFF').type = 'CompositorNodeCryptomatteV2'
        pie.operator("node.add_node", text="Keying", icon='IMAGE_ALPHA').type = 'CompositorNodeKeying'
        pie.operator("node.add_node", text="Color Key", icon='IMAGE_ALPHA').type = 'CompositorNodeColorMatte'
        pie.operator("node.add_node", text="Box Mask", icon='MOD_MASK').type = 'CompositorNodeBoxMask'
        pie.operator("node.add_node", text="Ellipse Mask", icon='MOD_MASK').type = 'CompositorNodeEllipseMask'

class SUBPIE_MT_co_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'CompositorNodeMath'
        pie.operator("node.add_node", text="Set Alpha", icon='IMAGE_ALPHA').type = 'CompositorNodeSetAlpha'
        pie.operator("node.add_node", text="ID Mask", icon='MOD_MASK').type = 'CompositorNodeIDMask'
        pie.operator("node.add_node", text="RGB to BW", icon='COLOR').type = 'CompositorNodeRGBToBW'

# ==============================================================================
# 3. MAIN CONTEXT MENU
# ==============================================================================

class NODE_PIE_MT_context(Menu):
    bl_idname = "NODE_PIE_MT_context_pie"
    bl_label = "Node Context Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        pie = layout.menu_pie()

        if context.space_data.type != 'NODE_EDITOR' or not context.space_data.node_tree:
            return

        selected_nodes = context.selected_nodes
        num_selected = len(selected_nodes)

        if num_selected == 0:
            tree_type = context.space_data.tree_type
            if tree_type == 'GeometryNodeTree':
                self.draw_no_nodes_geo(pie, context)
            elif tree_type == 'ShaderNodeTree':
                self.draw_no_nodes_shader(pie, context)
            elif tree_type == 'CompositorNodeTree':
                self.draw_no_nodes_comp(pie, context)
            else:
                pie.label(text="Tree type not supported")
        elif num_selected == 1:
            self.draw_single_node(pie, context)
        else:
            self.draw_multi_nodes(pie, context)

    # --- ADD NODE PIES (Dynamic based on workspace) ---
    
    def draw_no_nodes_geo(self, pie, context):
        # Insert your 8 SUBPIE_MT_gn_... menus here from the previous step
        pie.operator("wm.call_menu_pie", text="Mesh Nodes...", icon='MESH_DATA').name = "SUBPIE_MT_gn_mesh"
        pie.operator("wm.call_menu_pie", text="Curve Nodes...", icon='CURVE_DATA').name = "SUBPIE_MT_gn_curve"
        pie.operator("wm.call_menu_pie", text="Utilities & Math...", icon='CON_KINEMATIC').name = "SUBPIE_MT_gn_utilities"
        pie.operator("wm.call_menu_pie", text="Input & Output...", icon='NODETREE').name = "SUBPIE_MT_gn_io"
        pie.operator("wm.call_menu_pie", text="Geometry & Instances...", icon='GROUP_VERTEX').name = "SUBPIE_MT_gn_geometry_instances"
        pie.operator("wm.call_menu_pie", text="Attributes & Textures...", icon='SPREADSHEET').name = "SUBPIE_MT_gn_attributes"
        pie.operator("wm.call_menu_pie", text="Points & Volumes...", icon='PARTICLE_DATA').name = "SUBPIE_MT_gn_points_volumes"
        pie.operator("wm.call_menu_pie", text="Materials...", icon='MATERIAL').name = "SUBPIE_MT_gn_materials"

    def draw_no_nodes_shader(self, pie, context):
        # WEST
        pie.operator("wm.call_menu_pie", text="Texture...", icon='TEXTURE').name = "SUBPIE_MT_sh_texture"
        # EAST
        pie.operator("wm.call_menu_pie", text="Color...", icon='COLOR').name = "SUBPIE_MT_sh_color"
        # SOUTH
        pie.operator("wm.call_menu_pie", text="Converter...", icon='CON_KINEMATIC').name = "SUBPIE_MT_sh_converter"
        # NORTH
        pie.operator("wm.call_menu_pie", text="Input...", icon='FORWARD').name = "SUBPIE_MT_sh_input"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Shader...", icon='SHADING_RENDERED').name = "SUBPIE_MT_sh_shader"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text="Output...", icon='BACK').name = "SUBPIE_MT_sh_output"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text="Vector...", icon='ORIENTATION_GLOBAL').name = "SUBPIE_MT_sh_vector"
        # SOUTH-EAST
        pie.operator("node.add_node", text="Group Input", icon='NODETREE').type = 'NodeGroupInput'

    def draw_no_nodes_comp(self, pie, context):
        # WEST
        pie.operator("wm.call_menu_pie", text="Filter...", icon='MOD_SMOOTH').name = "SUBPIE_MT_co_filter"
        # EAST
        pie.operator("wm.call_menu_pie", text="Color...", icon='COLOR').name = "SUBPIE_MT_co_color"
        # SOUTH
        pie.operator("wm.call_menu_pie", text="Converter...", icon='CON_KINEMATIC').name = "SUBPIE_MT_co_converter"
        # NORTH
        pie.operator("wm.call_menu_pie", text="Input...", icon='FORWARD').name = "SUBPIE_MT_co_input"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Transform...", icon='ORIENTATION_GLOBAL').name = "SUBPIE_MT_co_transform"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text="Output...", icon='BACK').name = "SUBPIE_MT_co_output"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text="Matte & Mask...", icon='IMAGE_ALPHA').name = "SUBPIE_MT_co_matte"
        # SOUTH-EAST
        pie.operator("node.add_node", text="Group Input", icon='NODETREE').type = 'NodeGroupInput'

    # --- SELECTION PIES (Universal across all editors) ---

    def draw_single_node(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        pie.operator("node.delete_reconnect", text="Delete & Reconnect", icon='X') # WEST
        pie.operator("node.links_detach", text="Detach Links", icon='UNLINKED') # EAST
        pie.operator("node.mute_toggle", text="Mute / Unmute", icon='HIDE_OFF') # SOUTH
        if nw_loaded: # NORTH
            pie.operator("node.nw_preview_node", text="Preview Node", icon='HIDE_ON')
        else:
            pie.operator("node.view_toggle", text="Toggle Viewer", icon='HIDE_ON')
        pie.operator("node.duplicate_move", text="Duplicate", icon='DUPLICATE') # NORTH-WEST
        pie.operator("node.duplicate_move_keep_inputs", text="Duplicate (Keep Inputs)", icon='DUPLICATE') # NORTH-EAST
        pie.operator("node.delete", text="Delete", icon='TRASH') # SOUTH-WEST
        if nw_loaded: # SOUTH-EAST
            pie.operator("node.nw_add_reroutes", text="Add Reroutes", icon='NODE')
        else:
            pie.operator("node.clipboard_copy", text="Copy Node", icon='COPYDOWN')

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

        pie.operator("node.delete_reconnect", text="Delete & Reconnect", icon='X') # WEST
        if nw_loaded: # EAST
            pie.operator("node.nw_align_nodes", text="Align Nodes", icon='ALIGN_JUSTIFY')
        else:
            pie.operator("node.translate_attach", text="Attach Nodes", icon='LINKED')
        pie.operator("node.join", text="Frame Selected") # SOUTH
        
        # NORTH (Dynamic merge based on tree/selection via Node Wrangler)
        if nw_loaded:
            pie.operator("node.nw_merge_nodes", text="Merge / Join Nodes", icon='TRACKING_FORWARDS')
        else:
            pie.operator("node.add_node", text="Add Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath' 
            
        pie.operator("node.duplicate_move", text="Duplicate", icon='DUPLICATE') # NORTH-WEST
        if nw_loaded: # NORTH-EAST
            pie.operator("node.nw_swap_links", text="Swap Links", icon='FILE_REFRESH')
        else:
            pie.operator("node.links_detach", text="Detach Links", icon='UNLINKED')
        pie.operator("node.delete", text="Delete", icon='TRASH') # SOUTH-WEST
        pie.operator("node.mute_toggle", text="Mute / Unmute Selected", icon='HIDE_OFF') # SOUTH-EAST

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


# ==============================================================================
# 4. REGISTRATION
# ==============================================================================

# Ensure the Geometry nodes sub-menus from the previous response are appended to this list!
registry = [
SUBPIE_MT_gn_mesh,
    SUBPIE_MT_gn_curve, SUBPIE_MT_gn_utilities, SUBPIE_MT_gn_io, SUBPIE_MT_gn_geometry_instances, 
    SUBPIE_MT_gn_attributes, SUBPIE_MT_gn_points_volumes, SUBPIE_MT_gn_materials,
    SUBPIE_MT_sh_input, SUBPIE_MT_sh_output, SUBPIE_MT_sh_shader, SUBPIE_MT_sh_texture,
    SUBPIE_MT_sh_color, SUBPIE_MT_sh_vector, SUBPIE_MT_sh_converter,
    SUBPIE_MT_co_input, SUBPIE_MT_co_output, SUBPIE_MT_co_color, SUBPIE_MT_co_filter,
    SUBPIE_MT_co_transform, SUBPIE_MT_co_matte, SUBPIE_MT_co_converter,
    NODE_PIE_MT_context,
]

def register():
    # Loop over your classes here using bpy.utils.register_class(cls)
    # Then map the hotkey:
    
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=NODE_PIE_MT_context.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="Node Editor", 
        on_drag=False,
    )

def unregister():
    pass