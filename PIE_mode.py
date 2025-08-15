# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Context Pie: Mode Selection 'Right Mouse'",
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}


import bpy
from bpy.types import Menu
from .hotkeys import register_hotkey
from bl_ui.properties_paint_common import (
    UnifiedPaintPanel,
)
#from bpy.app.translations import contexts as i18n_contexts

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

class SUBPIE_MT_objectSelect(Menu):
    bl_label = "Select"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        pie.operator_enum("object.select_grouped", "type")
        '''
        # WEST
        pie.separator()
        # EAST
        op = pie.operator("mesh.object.select_hierarchy", text='Parent')
        op.direction = 'PARENT'
        op.extend = False
        # SOUTH
        op = pie.operator("mesh.object.select_hierarchy", text='Child')
        op.direction = 'CHILD'
        op.extend = False
        # NORTH
        pie.operator("mesh.select_nth", text='Checker Deselect')
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("mesh.select_mirror", text='Mirror')
        # SOUTH-WEST
        pie.operator("mesh.loop_to_region", text='Inside')        
        # SOUTH-EAST
        pie.operator("mesh.select_linked", text='Linked')
        '''

class SUBPIE_MT_meshSelect(Menu):
    bl_label = "Select"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("mesh.region_to_loop", text='Boundary')
        # EAST
        pie.operator("mesh.loop_multi_select", text='Ring').ring = True
        # SOUTH
        pie.operator("mesh.loop_multi_select", text='Loop').ring = False
        # NORTH
        pie.operator("mesh.select_nth", text='Checker Deselect')
        # NORTH-WEST
        pie.operator("mesh.select_all", text='Invert').action = 'INVERT'
        # NORTH-EAST
        pie.operator("mesh.select_mirror", text='Mirror')
        # SOUTH-WEST
        pie.operator("mesh.loop_to_region", text='Inside')        
        # SOUTH-EAST
        pie.operator("mesh.select_linked", text='Linked')

class SUBPIE_MT_curveSelect(Menu):
    bl_label = "Select"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("curve.select_previous", text='Previous')
        # EAST
        pie.operator("curve.select_next", text='Next')
        # SOUTH
        pie.operator("curve.select_similar", text='Similar Direction').type = 'DIRECTION'
        # NORTH
        pie.operator("curve.select_nth", text='Checker Deselect')
        # NORTH-WEST
        pie.operator("curve.select_all", text='Invert').action = 'INVERT'
        # NORTH-EAST
        pie.operator("curve.select_random", text='Random')
        # SOUTH-WEST
        pie.operator("curve.select_similar", text='Similar Radius').type = 'RADIUS'      
        # SOUTH-EAST
        pie.operator("curve.select_linked", text='Linked')

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


class SUBPIE_MT_curveTypeHandles(Menu):
    bl_label = "Set Curve/Handle Type"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("curve.handle_type_set", text='Automatic Handles').type = 'AUTOMATIC'
        # EAST
        pie.operator("curve.handle_type_set", text='Toggle Free/Align Handles').type = 'TOGGLE_FREE_ALIGN'
        # SOUTH
        pie.operator("curve.spline_type_set", text='Bezier Curve').type = 'BEZIER'
        # NORTH
        pie.operator("curve.handle_type_set", text='Free Handles').type = 'FREE_ALIGN'
        # NORTH-WEST
        pie.operator("curve.handle_type_set", text='Vector Handles').type = 'VECTOR'
        # NORTH-EAST
        pie.operator("curve.handle_type_set", text='Aligned Handles').type = 'ALIGNED'
        # SOUTH-WEST
        pie.operator("curve.spline_type_set", text='Poly Curve').type = 'POLY'
        # SOUTH-EAST
        pie.operator("curve.spline_type_set", text='NURBS Curve').type = 'NURBS'

class VIEW3D_PIE_MT_mode(Menu):
    bl_idname = "PIE_MT_context_mode"
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        mode_actions = {
            'OBJECT': self.draw_object_mode,
            'EDIT_MESH': self.draw_edit_mesh_mode,
            'EDIT_CURVE': self.draw_edit_curve_mode,
            'POSE': self.draw_pose_mode,
            'EDIT_LATTICE': self.draw_edit_lattice_mode,
            'EDIT_ARMATURE': self.draw_edit_armature_mode,
            'EDIT_GPENCIL': self.draw_edit_gpencil_mode,
            'EDIT_GREASE_PENCIL': self.draw_edit_gpencil_mode,
            'PAINT_GREASE_PENCIL': self.draw_edit_gpencil_mode,
            'SCULPT_GREASE_PENCIL': self.draw_edit_gpencil_mode,
            'PAINT_VERTEX': self.draw_paint_vertex_mode,
            'PAINT_TEXTURE': self.draw_paint_texture_mode,
            'PAINT_WEIGHT': self.draw_paint_weight_mode,
            'SCULPT': self.draw_sculpt_mode,
        }

        if context.mode in mode_actions:
            mode_actions[context.mode](pie, context)

    def draw_object_mode(self, pie, context):

        obj = context.object
        sel = context.selected_objects

        if obj and sel and obj.type in {'MESH', 'GPENCIL', 'GREASEPENCIL'}:
            # WEST EAST NORTH SOUTH N-W N-E
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"

        elif obj and sel and obj.type in {'CURVE', 'SURFACE', 'LATTICE', 'FONT'}:
            # WEST EAST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"

        elif obj and sel and obj.type == 'ARMATURE':
            # WEST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            # EAST
            pie.separator()
            pie.separator()
            pie.separator()
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"
        elif obj and sel and obj.type == 'EMPTY':
            # WEST EAST SOUTH NORTH
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()
            pie.separator()
            # SOUTH WEST
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            # SOUTH EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_objectSelect"

    def draw_edit_mesh_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
        # SOUTH
        pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
        # NORTH
        pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'
        # NORTH WEST
        # --------------------- ADD NORMALS SUB PIE HERE -------------------------------
        pie.separator()
        # SOUTH WEST
        # NORTH EAST
        pie.operator("wm.call_menu_pie", text='Split/Separate...').name = "SUBPIE_MT_separate"
        pie.menu("VIEW3D_MT_edit_mesh_context_menu", text="Context Menu", icon="COLLAPSEMENU")
        # SOUTH EAST
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_meshSelect"

    def draw_edit_curve_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator("curve.switch_direction")
        # SOUTH
        pie.operator("wm.call_menu_pie", text='Curve/Handle Type...').name = "SUBPIE_MT_curveTypeHandles"
        # NORTH
        pie.operator("curve.cyclic_toggle")
        # NORTH WEST
        pie.separator()
        # NORTH EAST
        pie.separator()
        # SOUTH WEST
        pie.menu("VIEW3D_MT_edit_curve_context_menu", text="Context Menu", icon="COLLAPSEMENU")
        # SOUTH EAST
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_curveSelect"

    def draw_pose_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        pie.menu("VIEW3D_MT_pose_context_menu", text="Pose Context Menu", icon="COLLAPSEMENU")
        pie.separator()

    def draw_edit_lattice_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST SOUTH NORTH N-W N-E
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        # SOUTH WEST
        pie.menu("VIEW3D_MT_edit_lattice_context_menu")

    def draw_edit_armature_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        pie.menu("VIEW3D_MT_edit_armature_names")
        pie.separator() 

    ## GREASE PENCIL MODES
    def draw_edit_gpencil_mode(self, pie, context):
        # WEST
        pie.operator_enum("OBJECT_OT_mode_set", "mode")
    '''
    def draw_paint_gpencil_mode(self, pie, context):
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def draw_sculpt_gpencil_mode(self, pie, context):
        pie.operator_enum("OBJECT_OT_mode_set", "mode")
    '''
    ## BRUSH MODE SECTION
    def draw_paint_vertex_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.vertex_paint.brush
        capabilities = brush.vertex_paint_capabilities

        self.draw_brush_properties(box, context, brush, capabilities)

    def draw_paint_texture_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.image_paint.brush
        capabilities = brush.image_paint_capabilities

        self.draw_brush_properties(box, context, brush, capabilities)

    def draw_paint_weight_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.weight_paint.brush
        capabilities = brush.weight_paint_capabilities

        self.draw_brush_properties(box, context, brush, capabilities)

    def draw_sculpt_mode(self, pie, context):
        # WEST
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        # EAST
        pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle")
        box = pie.box()
        brush = context.tool_settings.sculpt.brush
        capabilities = brush.sculpt_capabilities

        self.draw_brush_properties(box, context, brush, capabilities)

    def draw_brush_properties(self, box, context, brush, capabilities):

        def draw_property(box, context, brush, prop, text=None):
            unified_name = f"use_unified_{prop}"
            pressure_name = f"use_pressure_{prop}"
            try:
                UnifiedPaintPanel.prop_unified(
                    box, context, brush, prop,
                    unified_name=unified_name,
                    pressure_name=pressure_name,
                    text=text, slider=True,
                )
            except Exception as e:
                print(f"Error drawing property {prop}: {e}")

        if hasattr(capabilities, "has_color") and capabilities.has_color:
            split = box.split(factor=0.1)
            UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
            UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
            if hasattr(brush, "blend"):
                box.prop(brush, "blend", text="")

        ups = context.tool_settings.unified_paint_settings
        size_prop = "size"
        size_owner = ups if ups.use_unified_size else brush
        if size_owner.use_locked_size == 'SCENE':
            size_prop = "unprojected_radius"

        draw_property(box, context, brush, size_prop, text="Radius")
        draw_property(box, context, brush, "strength", text="Strength")


        sculpt_properties = {
            "auto_smooth_factor": "Auto Smooth",
            "normal_weight": "Normal Weight",
            "crease_pinch_factor": ("Pinch", "Magnify"),
            "rake_factor": "Rake Factor",
            "plane_offset": "Plane Offset",
            "plane_trim": "Distance",
            "height": "Height",
            "weight": "Weight"
        }

        for prop, text in sculpt_properties.items():
            if hasattr(capabilities, f"has_{prop}") and getattr(capabilities, f"has_{prop}"):
                if isinstance(text, tuple):
                    text = text[1] if brush.sculpt_tool in {'BLOB', 'SNAKE_HOOK'} else text[0]
                draw_property(box, context, brush, prop, text=text)

"""
class VIEW3D_PIE_MT_mode(Menu):
    bl_label  = "Mode Selection"

    def draw(self, context):
        
        if context.mode == 'OBJECT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object
            
            if obj is not None and obj.type in {'MESH', 'GPENCIL', 'GREASEPENCIL', 'FONT'}:

                # WEST # EAST # SOUTH # NORTH # NORTH-WEST # NORTH-EAST
                pie.operator_enum("OBJECT_OT_mode_set", "mode")
                # SOUTH-WEST
                pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
                # SOUTH-EAST
                subPie = pie.operator("wm.call_menu_pie", text='Select...')
                subPie.name = "SUBPIE_MT_objectSelect"

            elif obj is not None and obj.type in {'CURVE', 'SURFACE', 'LATTICE'}:

                # WEST # EAST 
                pie.operator_enum("OBJECT_OT_mode_set", "mode")
                # SOUTH
                pie.separator() 
                # NORTH 
                pie.separator()
                # NORTH-WEST 
                pie.separator()
                # NORTH-EAST
                pie.separator()
                # SOUTH-WEST
                pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
                # SOUTH-EAST
                subPie = pie.operator("wm.call_menu_pie", text='Select...')
                subPie.name = "SUBPIE_MT_objectSelect"

            elif obj is not None and obj.type == 'ARMATURE':

                # WEST # EAST # SOUTH 
                pie.operator_enum("OBJECT_OT_mode_set", "mode")
                # NORTH 
                pie.separator()
                # NORTH-WEST 
                pie.separator()
                # NORTH-EAST
                pie.separator()
                # SOUTH-WEST
                pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
                # SOUTH-EAST
                subPie = pie.operator("wm.call_menu_pie", text='Select...')
                subPie.name = "SUBPIE_MT_objectSelect"

        elif context.mode == 'EDIT_MESH':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            
            # WEST
            pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
            # EAST
            pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
            # SOUTH
            pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
            # NORTH
            pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'

            # NORTH-WEST
            pie.menu("VIEW3D_MT_edit_mesh_edges", text="edge menu", icon="COLLAPSEMENU")
            # NORTH-EAST
            pie.menu("VIEW3D_MT_edit_mesh_vertices", text="vert menu", icon="COLLAPSEMENU")
            # SOUTH-WEST
            pie.menu("VIEW3D_MT_edit_mesh_faces", text="face menu", icon="COLLAPSEMENU")
            # SOUTH-EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_meshSelect"  

        elif context.mode == 'EDIT_CURVE':

            # Else something is selected
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
            # EAST
            pie.menu("VIEW3D_MT_edit_curve_context_menu", text="curve menu", icon="COLLAPSEMENU")
            # SOUTH
            pie.operator("wm.call_menu_pie", text='Curve/Handle Type...').name = "SUBPIE_MT_curveTypeHandles"
            # NORTH
            pie.operator("curve.cyclic_toggle")
            
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.operator("curve.switch_direction")
            # SOUTH-WEST
            pie.separator()
            # SOUTH-EAST
            pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_curveSelect"

        elif context.mode == 'EDIT_GPENCIL' or context.mode == 'EDIT_GREASE_PENCIL':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            
            # WEST # EAST # SOUTH # NORTH # NORTH-WEST # NORTH-EAST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")

        elif context.mode == 'PAINT_GREASE_PENCIL':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            
            # WEST # EAST # SOUTH # NORTH # NORTH-WEST # NORTH-EAST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")

        elif context.mode == 'SCULPT_GREASE_PENCIL':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            
            # WEST # EAST # SOUTH # NORTH # NORTH-WEST # NORTH-EAST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")

        elif context.mode == 'PAINT_TEXTURE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
            # EAST
            pie.separator()
            # SOUTH
            box = pie.box()
            #show the colour picker directly

            brush = context.tool_settings.image_paint.brush
            capabilities = brush.image_paint_capabilities

            if capabilities.has_color:
                split = layout.split(factor=0.1)
                UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
                UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
                layout.prop(brush, "blend", text="")

            if capabilities.has_radius:
                UnifiedPaintPanel.prop_unified(
                    layout,
                    context,
                    brush,
                    "size",
                    unified_name="use_unified_size",
                    pressure_name="use_pressure_size",
                    slider=True,
                )
                UnifiedPaintPanel.prop_unified(
                    layout,
                    context,
                    brush,
                    "strength",
                    unified_name="use_unified_strength",
                    pressure_name="use_pressure_strength",
                    slider=True,
                )

        elif context.mode == 'PAINT_WEIGHT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
            # EAST
            pie.separator()
            # SOUTH
            box = pie.box()
            brush = context.tool_settings.weight_paint.brush
            UnifiedPaintPanel.prop_unified(
                layout,
                context,
                brush,
                "weight",
                unified_name="use_unified_weight",
                slider=True,
            )
            UnifiedPaintPanel.prop_unified(
                layout,
                context,
                brush,
                "size",
                unified_name="use_unified_size",
                pressure_name="use_pressure_size",
                slider=True,
            )
            UnifiedPaintPanel.prop_unified(
                layout,
                context,
                brush,
                "strength",
                unified_name="use_unified_strength",
                pressure_name="use_pressure_strength",
                slider=True,
            )

        elif context.mode == 'SCULPT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
            # EAST
            #pie.prop(bpy.context.view_layer.objects.active, "use_dynamic_topology_sculpting", toggle=True)
            pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle") #, icon="OBJECT_DATAMODE")
            # SOUTH
            box = pie.box()
            #show the colour picker directly
            brush = context.tool_settings.sculpt.brush
            capabilities = brush.sculpt_capabilities

            if capabilities.has_color:
                split = box.split(factor=0.1)
                UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
                UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
                box.prop(brush, "blend", text="")

            ups = context.tool_settings.unified_paint_settings
            size = "size"
            size_owner = ups if ups.use_unified_size else brush
            if size_owner.use_locked_size == 'SCENE':
                size = "unprojected_radius"

            UnifiedPaintPanel.prop_unified(
                box,
                context,
                brush,
                size,
                unified_name="use_unified_size",
                pressure_name="use_pressure_size",
                text="Radius",
                slider=True,
            )
            UnifiedPaintPanel.prop_unified(
                box,
                context,
                brush,
                "strength",
                unified_name="use_unified_strength",
                pressure_name="use_pressure_strength",
                slider=True,
            )

            if capabilities.has_auto_smooth:
                box.prop(brush, "auto_smooth_factor", slider=True)

            if capabilities.has_normal_weight:
                box.prop(brush, "normal_weight", slider=True)

            if capabilities.has_pinch_factor:
                text = "Pinch"
                if brush.sculpt_tool in {'BLOB', 'SNAKE_HOOK'}:
                    text = "Magnify"
                box.prop(brush, "crease_pinch_factor", slider=True, text=text)

            if capabilities.has_rake_factor:
                box.prop(brush, "rake_factor", slider=True)

            if capabilities.has_plane_offset:
                box.prop(brush, "plane_offset", slider=True)
                box.prop(brush, "plane_trim", slider=True, text="Distance")

            if capabilities.has_height:
                box.prop(brush, "height", slider=True, text="Height")
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
            
            '''
            VIEW3D_PT_sculpt_context_menu

            obj = context.object
            
            if obj is not None and obj.type in {'MESH', 'CURVE', 'SURFACE'}:
                pie.operator_enum("OBJECT_OT_mode_set", "mode")
                pie.menu("VIEW3D_PIE_object_context_menu", text="Object Menu")
            '''

        elif context.mode == 'POSE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
            # EAST
            pie.separator()
            # SOUTH
            pie.menu("VIEW3D_MT_pose_context_menu", text="Pose Context Menu", icon="COLLAPSEMENU")

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

        elif context.mode == 'EDIT_LATTICE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
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
        
        elif context.mode == 'EDIT_ARMATURE':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
            # EAST
            pie.separator()
            # SOUTH
            pie.separator()
            # NORTH
            pie.separator()
            # NORTH-WEST
            pie.separator() 
            # NORTH-EAST
            pie.menu("VIEW3D_MT_edit_armature_names")
            # SOUTH-WEST
            pie.separator()
            # SOUTH-EAST
            pie.separator()

        elif context.mode == 'PAINT_VERTEX':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            # WEST
            pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
            # EAST
            pie.separator()
            # SOUTH
            box = pie.box()
            #show the colour picker directly
            brush = context.tool_settings.vertex_paint.brush
            capabilities = brush.vertex_paint_capabilities

            if capabilities.has_color:
                split = layout.split(factor=0.1)
                UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
                UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
                layout.prop(brush, "blend", text="")

            UnifiedPaintPanel.prop_unified(
                layout,
                context,
                brush,
                "size",
                unified_name="use_unified_size",
                pressure_name="use_pressure_size",
                slider=True,
            )
            UnifiedPaintPanel.prop_unified(
                layout,
                context,
                brush,
                "strength",
                unified_name="use_unified_strength",
                pressure_name="use_pressure_strength",
                slider=True,
            )
"""

registry = [
    SUBPIE_MT_objectSelect,
    SUBPIE_MT_meshSelect,
    SUBPIE_MT_curveSelect,
    SUBPIE_MT_separate,
    SUBPIE_MT_curveTypeHandles,
    VIEW3D_PIE_MT_mode,
]

addon_keymaps = []

def register():

    categories = [
        "Object Mode", 
        "Mesh", 
        "Curve", 
        "Grease Pencil Edit Mode",
        "Grease Pencil Sculpt Mode",
        "Grease Pencil Paint Mode",
        "Sculpt", 
        "Pose",
        "Lattice",
        "Armature",
        "Vertex Paint",
        "Weight Paint",
        "Image Paint",
    ]

    for cat in categories:
        WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
            pie_name=VIEW3D_PIE_MT_mode.bl_idname,
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
            keymap_name=cat,
        )
