# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

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
        pie.operator("node.add_node", text="Curve to Points", icon='PARTICLE_DATA').type = 'GeometryNodeCurveToPoints'

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
        pie.operator("node.add_node", text="Map Range", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeMapRange'

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
        pie.operator("node.add_node", text="Scene Time", icon='TIME').type = 'GeometryNodeInputSceneTime'

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
        pie.operator("node.add_node", text="Geometry to Instance", icon='OUTLINER_OB_GROUP_INSTANCE').type = 'GeometryNodeGeometryToInstance'

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
        pie.operator("node.add_node", text="Blur Attribute", icon='MOD_SMOOTH').type = 'GeometryNodeBlurAttribute'
        pie.operator("node.add_node", text="Sample Index", icon='SPREADSHEET').type = 'GeometryNodeSampleIndex'

class SUBPIE_MT_gn_points_volumes(Menu):
    bl_label = "Points & Volumes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Distribute Points on Faces", icon='PARTICLE_DATA').type = 'GeometryNodeDistributePointsOnFaces'
        pie.operator("node.add_node", text="Points", icon='PARTICLE_DATA').type = 'GeometryNodePoints'
        pie.operator("node.add_node", text="Points to Volume", icon='VOLUME_DATA').type = 'GeometryNodePointsToVolume'
        pie.operator("node.add_node", text="Volume to Mesh", icon='MESH_DATA').type = 'GeometryNodeVolumeToMesh'
        pie.operator("node.add_node", text="Points to Vertices", icon='VERTEXSEL').type = 'GeometryNodePointsToVertices'
        pie.operator("node.add_node", text="Distribute Points in Volume", icon='PARTICLE_DATA').type = 'GeometryNodeDistributePointsInVolume'
        pie.operator("node.add_node", text="Volume Cube", icon='VOLUME_DATA').type = 'GeometryNodeVolumeCube'
        pie.operator("node.add_node", text="Set Point Radius", icon='PARTICLE_DATA').type = 'GeometryNodeSetPointRadius'

class SUBPIE_MT_gn_materials(Menu):
    bl_label = "Materials & UV"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Set Material", icon='MATERIAL').type = 'GeometryNodeSetMaterial'
        pie.operator("node.add_node", text="Replace Material", icon='MATERIAL').type = 'GeometryNodeReplaceMaterial'
        pie.operator("node.add_node", text="Material Selection", icon='MATERIAL').type = 'GeometryNodeMaterialSelection'
        pie.operator("node.add_node", text="Set Material Index", icon='MATERIAL').type = 'GeometryNodeSetMaterialIndex'
        pie.operator("node.add_node", text="Input Material", icon='MATERIAL').type = 'GeometryNodeInputMaterial'
        pie.operator("node.add_node", text="Set Shade Smooth", icon='SHADING_RENDERED').type = 'GeometryNodeSetShadeSmooth'
        pie.operator("node.add_node", text="UV Unwrap", icon='UV').type = 'GeometryNodeUVUnwrap'
        pie.operator("node.add_node", text="UV Pack Islands", icon='UV').type = 'GeometryNodeUVPackIslands'


# ==============================================================================
# 2. SHADER NODES SUB-MENUS
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
        pie.operator("node.add_node", text="Fresnel", icon='NORMALS_FACE').type = 'ShaderNodeFresnel'
        pie.operator("node.add_node", text="UV Map", icon='UV').type = 'ShaderNodeUVMap'

class SUBPIE_MT_sh_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Material Output", icon='MATERIAL').type = 'ShaderNodeOutputMaterial'
        pie.operator("node.add_node", text="Light Output", icon='LIGHT').type = 'ShaderNodeOutputLight'
        pie.operator("node.add_node", text="World Output", icon='WORLD').type = 'ShaderNodeOutputWorld'
        pie.operator("node.add_node", text="AOV Output", icon='RENDER_RESULT').type = 'ShaderNodeOutputAOV'
        pie.operator("node.add_node", text="Line Style Output", icon='STROKE').type = 'ShaderNodeOutputLineStyle'
        pie.operator("node.add_node", text="Background", icon='WORLD').type = 'ShaderNodeBackground'
        pie.operator("node.add_node", text="Holdout", icon='SHADING_WIRE').type = 'ShaderNodeHoldout'
        pie.operator("node.add_node", text="Emission", icon='LIGHT').type = 'ShaderNodeEmission'

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
        pie.operator("node.add_node", text="Glossy BSDF", icon='SHADING_RENDERED').type = 'ShaderNodeBsdfGlossy'
        pie.operator("node.add_node", text="Principled Volume", icon='VOLUME_DATA').type = 'ShaderNodeVolumePrincipled'

class SUBPIE_MT_sh_texture(Menu):
    bl_label = "Texture"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Image Texture", icon='IMAGE_DATA').type = 'ShaderNodeTexImage'
        pie.operator("node.add_node", text="Noise Texture", icon='TEXTURE').type = 'ShaderNodeTexNoise'
        pie.operator("node.add_node", text="Voronoi Texture", icon='TEXTURE').type = 'ShaderNodeTexVoronoi'
        pie.operator("node.add_node", text="Gradient Texture", icon='TEXTURE').type = 'ShaderNodeTexGradient'
        pie.operator("node.add_node", text="Wave Texture", icon='TEXTURE').type = 'ShaderNodeTexWave'
        pie.operator("node.add_node", text="Sky Texture", icon='LIGHT_SUN').type = 'ShaderNodeTexSky'
        pie.operator("node.add_node", text="Checker Texture", icon='TEXTURE').type = 'ShaderNodeTexChecker'
        pie.operator("node.add_node", text="Magic Texture", icon='TEXTURE').type = 'ShaderNodeTexMagic'

class SUBPIE_MT_sh_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'ShaderNodeValToRGB'
        pie.operator("node.add_node", text="Mix Color", icon='COLOR').type = 'ShaderNodeMix'
        pie.operator("node.add_node", text="RGB Curves", icon='CURVE_DATA').type = 'ShaderNodeRGBCurve'
        pie.operator("node.add_node", text="Hue/Saturation", icon='COLOR').type = 'ShaderNodeHueSaturation'
        pie.operator("node.add_node", text="Invert Color", icon='COLOR').type = 'ShaderNodeInvert'
        pie.operator("node.add_node", text="Bright/Contrast", icon='COLORSET_10_VEC').type = 'ShaderNodeBrightContrast'
        pie.operator("node.add_node", text="Gamma", icon='COLOR').type = 'ShaderNodeGamma'
        pie.operator("node.add_node", text="Light Falloff", icon='LIGHT').type = 'ShaderNodeLightFalloff'

class SUBPIE_MT_sh_vector(Menu):
    bl_label = "Vector"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Mapping", icon='ORIENTATION_GLOBAL').type = 'ShaderNodeMapping'
        pie.operator("node.add_node", text="Bump", icon='FORCE_TEXTURE').type = 'ShaderNodeBump'
        pie.operator("node.add_node", text="Displacement", icon='FORCE_TEXTURE').type = 'ShaderNodeDisplacement'
        pie.operator("node.add_node", text="Normal Map", icon='NORMALS_FACE').type = 'ShaderNodeNormalMap'
        pie.operator("node.add_node", text="Vector Math", icon='CON_KINEMATIC').type = 'ShaderNodeVectorMath'
        pie.operator("node.add_node", text="Vector Displacement", icon='FORCE_TEXTURE').type = 'ShaderNodeVectorDisplacement'
        pie.operator("node.add_node", text="Vector Curves", icon='CURVE_DATA').type = 'ShaderNodeVectorCurve'
        pie.operator("node.add_node", text="Vector Transform", icon='ORIENTATION_GLOBAL').type = 'ShaderNodeVectorTransform'

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
        pie.operator("node.add_node", text="Clamp", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeClamp'
        pie.operator("node.add_node", text="Blackbody", icon='LIGHT').type = 'ShaderNodeBlackbody'


# ==============================================================================
# 3. COMPOSITOR NODES SUB-MENUS
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
        pie.operator("node.add_node", text="Mask", icon='MOD_MASK').type = 'CompositorNodeMask'
        pie.operator("node.add_node", text="Bokeh Image", icon='IMAGE_DATA').type = 'CompositorNodeBokehImage'
        pie.operator("node.add_node", text="Track Position", icon='TRACKER').type = 'CompositorNodeTrackPos'

class SUBPIE_MT_co_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Composite", icon='RENDER_RESULT').type = 'CompositorNodeComposite'
        pie.operator("node.add_node", text="Viewer", icon='HIDE_ON').type = 'CompositorNodeViewer'
        pie.operator("node.add_node", text="File Output", icon='FILE_IMAGE').type = 'CompositorNodeOutputFile'
        pie.operator("node.add_node", text="Split Viewer", icon='HIDE_ON').type = 'CompositorNodeSplitViewer'
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_co_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Mix", icon='COLOR').type = 'CompositorNodeMixRGB'
        pie.operator("node.add_node", text="Alpha Over", icon='IMAGE_ALPHA').type = 'CompositorNodeAlphaOver'
        pie.operator("node.add_node", text="Color Balance", icon='COLOR').type = 'CompositorNodeColorBalance'
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'CompositorNodeValToRGB'
        pie.operator("node.add_node", text="Hue Saturation Value", icon='COLOR').type = 'CompositorNodeHueSat'
        pie.operator("node.add_node", text="RGB Curves", icon='CURVE_DATA').type = 'CompositorNodeCurveRGB'
        pie.operator("node.add_node", text="Bright/Contrast", icon='COLORSET_10_VEC').type = 'CompositorNodeBrightContrast'
        pie.operator("node.add_node", text="Gamma", icon='COLOR').type = 'CompositorNodeGamma'

class SUBPIE_MT_co_filter(Menu):
    bl_label = "Filter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Blur", icon='MOD_SMOOTH').type = 'CompositorNodeBlur'
        pie.operator("node.add_node", text="Glare", icon='LIGHT_SUN').type = 'CompositorNodeGlare'
        pie.operator("node.add_node", text="Directional Blur", icon='MOD_SMOOTH').type = 'CompositorNodeDBlur'
        pie.operator("node.add_node", text="Sun Beams", icon='LIGHT_SUN').type = 'CompositorNodeSunBeams'
        pie.operator("node.add_node", text="Pixelate", icon='TEXTURE').type = 'CompositorNodePixelate'
        pie.operator("node.add_node", text="Despeckle", icon='MOD_SMOOTH').type = 'CompositorNodeDespeckle'
        pie.operator("node.add_node", text="Filter", icon='FILTER').type = 'CompositorNodeFilter'
        pie.operator("node.add_node", text="Bokeh Blur", icon='IMAGE_DATA').type = 'CompositorNodeBokehBlur'

class SUBPIE_MT_co_transform(Menu):
    bl_label = "Transform"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Transform", icon='ORIENTATION_GLOBAL').type = 'CompositorNodeTransform'
        pie.operator("node.add_node", text="Translate", icon='NODE').type = 'CompositorNodeTranslate'
        pie.operator("node.add_node", text="Scale", icon='NODE').type = 'CompositorNodeScale'
        pie.operator("node.add_node", text="Rotate", icon='NODE').type = 'CompositorNodeRotate'
        pie.operator("node.add_node", text="Flip", icon='NODE').type = 'CompositorNodeFlip'
        pie.operator("node.add_node", text="Crop", icon='FULLSCREEN_EXIT').type = 'CompositorNodeCrop'
        pie.operator("node.add_node", text="Movie Distortion", icon='TRACKER').type = 'CompositorNodeMovieDistortion'
        pie.operator("node.add_node", text="Corner Pin", icon='NODE').type = 'CompositorNodeCornerPin'

class SUBPIE_MT_co_matte(Menu):
    bl_label = "Matte & Mask"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Cryptomatte", icon='RESTRICT_COLOR_OFF').type = 'CompositorNodeCryptomatteV2'
        pie.operator("node.add_node", text="Keying", icon='IMAGE_ALPHA').type = 'CompositorNodeKeying'
        pie.operator("node.add_node", text="Color Key", icon='IMAGE_ALPHA').type = 'CompositorNodeColorMatte'
        pie.operator("node.add_node", text="Box Mask", icon='MOD_MASK').type = 'CompositorNodeBoxMask'
        pie.operator("node.add_node", text="Ellipse Mask", icon='MOD_MASK').type = 'CompositorNodeEllipseMask'
        pie.operator("node.add_node", text="Luminance Key", icon='IMAGE_ALPHA').type = 'CompositorNodeLumaMatte'
        pie.operator("node.add_node", text="Chroma Key", icon='IMAGE_ALPHA').type = 'CompositorNodeChromaMatte'
        pie.operator("node.add_node", text="Difference Key", icon='IMAGE_ALPHA').type = 'CompositorNodeDiffMatte'

class SUBPIE_MT_co_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'CompositorNodeMath'
        pie.operator("node.add_node", text="Set Alpha", icon='IMAGE_ALPHA').type = 'CompositorNodeSetAlpha'
        pie.operator("node.add_node", text="ID Mask", icon='MOD_MASK').type = 'CompositorNodeIDMask'
        pie.operator("node.add_node", text="RGB to BW", icon='COLOR').type = 'CompositorNodeRGBToBW'
        pie.operator("node.add_node", text="Separate Color", icon='COLOR').type = 'CompositorNodeSeparateColor'
        pie.operator("node.add_node", text="Combine Color", icon='COLOR').type = 'CompositorNodeCombineColor'
        pie.operator("node.add_node", text="Alpha Convert", icon='IMAGE_ALPHA').type = 'CompositorNodePremulKey'
        pie.operator("node.add_node", text="Normalize", icon='NORMALIZE_FCURVES').type = 'CompositorNodeNormalize'


# ==============================================================================
# 4. SHARED UTILITY SUB-MENUS
# ==============================================================================

class SUBPIE_MT_node_group(Menu):
    bl_label = "Group"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Opened from SE: cluster at SE/E, separators elsewhere.
        # WEST
        pie.separator()
        # EAST - adjacent to SE
        pie.operator("node.add_node", text="Group Input", icon='FORWARD').type = 'NodeGroupInput'
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
        # SOUTH-EAST - primary
        pie.operator("node.add_node", text="Group Output", icon='BACK').type = 'NodeGroupOutput'


class SUBPIE_MT_node_delete(Menu):
    bl_label = "Delete"

    def draw(self, context):
        pie = self.layout.menu_pie()
        nw_loaded = "node_wrangler" in context.preferences.addons
        # Opened from SW: cluster at SW/S/W, separators elsewhere.
        # WEST - adjacent to SW
        if nw_loaded:
            pie.operator("node.nw_del_unused", text="Delete Unused", icon='TRASH')
        else:
            pie.separator()
        # EAST
        pie.separator()
        # SOUTH - adjacent to SW
        pie.operator("node.delete", text="Delete", icon='TRASH')
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST - primary
        pie.operator("node.delete_reconnect", text="Delete & Reconnect", icon='X')
        # SOUTH-EAST
        pie.separator()


# ==============================================================================
# 5. MULTI-SELECTION SUB-MENUS
# ==============================================================================

class SUBPIE_MT_node_join(Menu):
    bl_label = "Join / Merge"

    def draw(self, context):
        pie = self.layout.menu_pie()
        nw_loaded = "node_wrangler" in context.preferences.addons
        tree_type = context.space_data.tree_type

        # Opened from NORTH: clump primary geo ops at N/NW/NE/W, math at E/S.

        if tree_type == 'GeometryNodeTree':
            if nw_loaded:
                # WEST - last boolean, still in upper cluster
                op = pie.operator("node.nw_merge_nodes", text="Intersect", icon='SELECT_INTERSECT')
                op.mode = 'INTERSECT'
                op.merge_type = 'GEOMETRY'
                # EAST - math begins here, moving away from north
                op = pie.operator("node.nw_merge_nodes", text="Math Add", icon='CON_KINEMATIC')
                op.mode = 'ADD'
                op.merge_type = 'MATH'
                # SOUTH - math, furthest from north
                op = pie.operator("node.nw_merge_nodes", text="Math Multiply")
                op.mode = 'MULTIPLY'
                op.merge_type = 'MATH'
                # NORTH - primary: Join Geometry
                op = pie.operator("node.nw_merge_nodes", text="Join Geometry", icon='MESH_DATA')
                op.mode = 'JOIN'
                op.merge_type = 'GEOMETRY'
                # NORTH-WEST - boolean cluster
                op = pie.operator("node.nw_merge_nodes", text="Difference", icon='SELECT_SUBTRACT')
                op.mode = 'DIFFERENCE'
                op.merge_type = 'GEOMETRY'
                # NORTH-EAST - boolean cluster
                op = pie.operator("node.nw_merge_nodes", text="Union", icon='SELECT_EXTEND')
                op.mode = 'UNION'
                op.merge_type = 'GEOMETRY'
                # SOUTH-WEST
                pie.separator()
                # SOUTH-EAST
                pie.separator()
            else:
                # WEST
                pie.operator("node.add_node", text="Intersect", icon='SELECT_INTERSECT').type = 'GeometryNodeMeshBoolean'
                # EAST
                pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath'
                # SOUTH
                pie.separator()
                # NORTH
                pie.operator("node.add_node", text="Join Geometry", icon='MESH_DATA').type = 'GeometryNodeJoinGeometry'
                # NORTH-WEST
                pie.operator("node.add_node", text="Mesh Boolean", icon='MOD_BOOLEAN').type = 'GeometryNodeMeshBoolean'
                # NORTH-EAST
                pie.operator("node.add_node", text="Vector Math", icon='CON_KINEMATIC').type = 'ShaderNodeVectorMath'
                # SOUTH-WEST
                pie.separator()
                # SOUTH-EAST
                pie.separator()

        elif tree_type == 'ShaderNodeTree':
            if nw_loaded:
                # WEST - shader cluster (opened from north, shaders near top)
                op = pie.operator("node.nw_merge_nodes", text="Mix Shader", icon='SHADING_RENDERED')
                op.mode = 'MIX'
                op.merge_type = 'SHADER'
                # EAST - math, moving south
                op = pie.operator("node.nw_merge_nodes", text="Math Add", icon='CON_KINEMATIC')
                op.mode = 'ADD'
                op.merge_type = 'MATH'
                # SOUTH - math, furthest
                op = pie.operator("node.nw_merge_nodes", text="Math Subtract")
                op.mode = 'SUBTRACT'
                op.merge_type = 'MATH'
                # NORTH - primary
                op = pie.operator("node.nw_merge_nodes", text="Add Shader", icon='ADD')
                op.mode = 'ADD'
                op.merge_type = 'SHADER'
                # NORTH-WEST - color cluster
                op = pie.operator("node.nw_merge_nodes", text="Color Mix", icon='COLOR')
                op.mode = 'MIX'
                op.merge_type = 'MIX'
                # NORTH-EAST - color cluster
                op = pie.operator("node.nw_merge_nodes", text="Color Multiply")
                op.mode = 'MULTIPLY'
                op.merge_type = 'MIX'
                # SOUTH-WEST
                pie.separator()
                # SOUTH-EAST
                pie.separator()
            else:
                pie.operator("node.add_node", text="Mix Shader", icon='SHADING_RENDERED').type = 'ShaderNodeMixShader'
                pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath'
                pie.separator()
                pie.operator("node.add_node", text="Add Shader", icon='ADD').type = 'ShaderNodeAddShader'
                pie.separator()
                pie.separator()
                pie.separator()
                pie.separator()

        elif tree_type == 'CompositorNodeTree':
            if nw_loaded:
                # WEST
                op = pie.operator("node.nw_merge_nodes", text="Color Mix", icon='COLOR')
                op.mode = 'MIX'
                op.merge_type = 'MIX'
                # EAST - math, moving south
                op = pie.operator("node.nw_merge_nodes", text="Math Add", icon='CON_KINEMATIC')
                op.mode = 'ADD'
                op.merge_type = 'MATH'
                # SOUTH - furthest
                op = pie.operator("node.nw_merge_nodes", text="Depth Combine", icon='MOD_ARRAY')
                op.mode = 'MIX'
                op.merge_type = 'DEPTH_COMBINE'
                # NORTH - primary
                op = pie.operator("node.nw_merge_nodes", text="Alpha Over", icon='IMAGE_ALPHA')
                op.mode = 'MIX'
                op.merge_type = 'ALPHAOVER'
                # NORTH-WEST
                op = pie.operator("node.nw_merge_nodes", text="Color Add")
                op.mode = 'ADD'
                op.merge_type = 'MIX'
                # NORTH-EAST
                op = pie.operator("node.nw_merge_nodes", text="Math Multiply")
                op.mode = 'MULTIPLY'
                op.merge_type = 'MATH'
                # SOUTH-WEST
                pie.separator()
                # SOUTH-EAST
                pie.separator()
            else:
                pie.operator("node.add_node", text="Alpha Over", icon='IMAGE_ALPHA').type = 'CompositorNodeAlphaOver'
                pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'CompositorNodeMath'
                pie.separator()
                pie.operator("node.add_node", text="Mix", icon='COLOR').type = 'CompositorNodeMixRGB'
                pie.separator()
                pie.separator()
                pie.separator()
                pie.separator()
        else:
            pie.label(text="No merge options for this tree")
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()


class SUBPIE_MT_node_duplicate(Menu):
    bl_label = "Duplicate"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Opened from NW: clump options at NW/W/N/NE, separators at S/SW/SE/E.
        # WEST - adjacent to NW
        pie.operator("node.duplicate_move_keep_inputs", text="Keep Inputs", icon='DUPLICATE')
        # EAST
        pie.separator()
        # SOUTH
        pie.separator()
        # NORTH - adjacent to NW
        pie.operator("node.clipboard_paste", text="Paste", icon='PASTEDOWN')
        # NORTH-WEST - primary, closest to origin
        pie.operator("node.duplicate_move", text="Duplicate", icon='DUPLICATE')
        # NORTH-EAST
        pie.operator("node.clipboard_copy", text="Copy", icon='COPYDOWN')
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


# ==============================================================================
# 6. MAIN CONTEXT MENU
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

    # --- ADD NODE PIES (no selection) ---

    def draw_no_nodes_geo(self, pie, context):
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
        pie.operator("wm.call_menu_pie", text="Materials & UV...", icon='MATERIAL').name = "SUBPIE_MT_gn_materials"

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
        pie.operator("wm.call_menu_pie", text="Group...", icon='NODETREE').name = "SUBPIE_MT_node_group"

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
        pie.operator("wm.call_menu_pie", text="Group...", icon='NODETREE').name = "SUBPIE_MT_node_group"

    # --- SELECTION PIES ---

    def draw_single_node(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST - sever all links on this node
        pie.operator("node.links_detach", text="Detach All Links", icon='UNLINKED')
        # EAST - detach only outputs, keep inputs (NW) or copy node
        if nw_loaded:
            pie.operator("node.nw_detach_outputs", text="Detach Outputs", icon='UNLINKED')
        else:
            pie.operator("node.clipboard_copy", text="Copy Node", icon='COPYDOWN')
        # SOUTH
        pie.operator("node.mute_toggle", text="Mute / Unmute", icon='HIDE_OFF')
        # NORTH - viewer/output link, tree-type aware
        tree_type = context.space_data.tree_type if context.space_data.node_tree else None
        if tree_type in ('GeometryNodeTree', 'CompositorNodeTree'):
            pie.operator("node.link_viewer", text="Link to Viewer", icon='HIDE_OFF')
        elif nw_loaded:
            pie.operator("node.nw_link_out", text="Link to Output", icon='DRIVER')
        else:
            pie.operator("node.view_toggle", text="Toggle Viewer", icon='HIDE_ON')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Duplicate...", icon='DUPLICATE').name = "SUBPIE_MT_node_duplicate"
        # NORTH-EAST - add reroute nodes to all outputs (NW)
        if nw_loaded:
            pie.operator("node.nw_add_reroutes", text="Add Reroutes", icon='NODE').option = 'ALL'
        else:
            pie.separator()
        # SOUTH-WEST - delete submenu
        pie.operator("wm.call_menu_pie", text="Delete...", icon='TRASH').name = "SUBPIE_MT_node_delete"
        # SOUTH-EAST - reset node to defaults (NW) or hide toggle
        if nw_loaded:
            pie.operator("node.nw_reset_nodes", text="Reset Node", icon='FILE_REFRESH')
        else:
            pie.operator("node.hide_toggle", text="Toggle Hidden", icon='HIDE_OFF')

        # Extras dropdown
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        if nw_loaded:
            dropdown_menu.operator("node.nw_copy_settings", text="Copy Settings from Active")
            dropdown_menu.operator("node.nw_copy_label", text="Copy Label from Active").option = 'FROM_ACTIVE'
            dropdown_menu.operator("node.nw_clear_label", text="Clear Label").option = True
        dropdown_menu.operator("node.hide_toggle", text="Toggle Hidden")
        dropdown_menu.operator("node.options_toggle", text="Toggle Options")

    def draw_multi_nodes(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST - sever all links on selected nodes
        pie.operator("node.links_detach", text="Detach All Links", icon='UNLINKED')
        # EAST - align selected nodes (NW) or attach
        if nw_loaded:
            pie.operator("node.nw_align_nodes", text="Align Nodes", icon='ALIGN_JUSTIFY')
        else:
            pie.operator("node.translate_attach", text="Attach Nodes", icon='LINKED')
        # SOUTH - mute/unmute, consistent with single-node
        pie.operator("node.mute_toggle", text="Mute / Unmute", icon='HIDE_OFF')
        # NORTH - merge / join (see SUBPIE_MT_node_join)
        pie.operator("wm.call_menu_pie", text='Join / Merge...', icon='TRIA_UP').name = "SUBPIE_MT_node_join"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Duplicate...", icon='DUPLICATE').name = "SUBPIE_MT_node_duplicate"
        # NORTH-EAST - link active node to all other selected (NW) or attach
        if nw_loaded:
            op = pie.operator("node.nw_link_active_to_selected", text="Link Active to Selected", icon='LINKED')
            op.replace = False
            op.use_node_name = False
            op.use_outputs_names = False
        else:
            pie.operator("node.translate_attach", text="Attach Nodes", icon='LINKED')
        # SOUTH-WEST - delete submenu
        pie.operator("wm.call_menu_pie", text="Delete...", icon='TRASH').name = "SUBPIE_MT_node_delete"
        # SOUTH-EAST - wrap in frame node
        pie.operator("node.join", text="Frame Selected", icon='STICKY_UVS_LOC')

        # Extras dropdown
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        if nw_loaded:
            dropdown_menu.operator("node.nw_link_active_to_selected", text="Link Active to Selected")
            dropdown_menu.operator("node.nw_copy_settings", text="Copy Settings from Active")
            dropdown_menu.operator("node.nw_center_nodes", text="Center Nodes")
            dropdown_menu.operator("node.nw_reload_images", text="Reload Images")
            dropdown_menu.operator("node.nw_bg_reset", text="Reset Backdrop")


# ==============================================================================
# 7. REGISTRATION
# ==============================================================================

registry = [
    SUBPIE_MT_gn_mesh,
    SUBPIE_MT_gn_curve,
    SUBPIE_MT_gn_utilities,
    SUBPIE_MT_gn_io,
    SUBPIE_MT_gn_geometry_instances,
    SUBPIE_MT_gn_attributes,
    SUBPIE_MT_gn_points_volumes,
    SUBPIE_MT_gn_materials,
    SUBPIE_MT_sh_input,
    SUBPIE_MT_sh_output,
    SUBPIE_MT_sh_shader,
    SUBPIE_MT_sh_texture,
    SUBPIE_MT_sh_color,
    SUBPIE_MT_sh_vector,
    SUBPIE_MT_sh_converter,
    SUBPIE_MT_co_input,
    SUBPIE_MT_co_output,
    SUBPIE_MT_co_color,
    SUBPIE_MT_co_filter,
    SUBPIE_MT_co_transform,
    SUBPIE_MT_co_matte,
    SUBPIE_MT_co_converter,
    SUBPIE_MT_node_group,
    SUBPIE_MT_node_delete,
    SUBPIE_MT_node_join,
    SUBPIE_MT_node_duplicate,
    NODE_PIE_MT_context,
]

def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=NODE_PIE_MT_context.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="Node Editor",
        on_drag=False,
    )

def unregister():
    pass
