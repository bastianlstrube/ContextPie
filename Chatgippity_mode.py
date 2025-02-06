class VIEW3D_PIE_MT_mode(Menu):
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        mode_handlers = {
            'OBJECT': self.draw_object_mode,
            'EDIT_MESH': self.draw_edit_mesh_mode,
            'EDIT_CURVE': self.draw_edit_curve_mode,
            'EDIT_GPENCIL': self.draw_edit_gpencil_mode,
            'EDIT_GREASE_PENCIL': self.draw_edit_gpencil_mode,
            'PAINT_GREASE_PENCIL': self.draw_grease_pencil_paint_mode,
            'SCULPT_GREASE_PENCIL': self.draw_grease_pencil_paint_mode,
            'PAINT_TEXTURE': self.draw_paint_texture_mode,
            'PAINT_VERTEX': self.draw_paint_vertex_mode,
            'SCULPT': self.draw_sculpt_mode,
            'POSE': self.draw_pose_mode,
            'EDIT_LATTICE': self.draw_simple_edit_mode,
            'EDIT_ARMATURE': self.draw_edit_armature_mode,
        }

        handler = mode_handlers.get(context.mode)
        if handler:
            handler(pie, context)

    def draw_object_mode(self, pie, context):
        obj = context.object
        if obj and obj.type in {'MESH', 'GPENCIL', 'GREASEPENCIL', 'FONT'}:
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            sub_pie = pie.operator("wm.call_menu_pie", text='Select...')
            sub_pie.name = "SUBPIE_MT_objectSelect"
        elif obj and obj.type in {'CURVE', 'SURFACE', 'LATTICE'}:
            self.draw_common_object_pie(pie)
        elif obj and obj.type == 'ARMATURE':
            self.draw_common_object_pie(pie)

    def draw_common_object_pie(self, pie):
        pie.operator_enum("OBJECT_OT_mode_set", "mode")
        for _ in range(4):  # Adding separators for empty slots
            pie.separator()
        pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
        sub_pie = pie.operator("wm.call_menu_pie", text='Select...')
        sub_pie.name = "SUBPIE_MT_objectSelect"

    def draw_edit_mesh_mode(self, pie, context):
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")
        pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
        pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
        pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'
        pie.menu("VIEW3D_MT_edit_mesh_edges", text="Edge Menu", icon="COLLAPSEMENU")
        pie.menu("VIEW3D_MT_edit_mesh_vertices", text="Vert Menu", icon="COLLAPSEMENU")
        pie.menu("VIEW3D_MT_edit_mesh_faces", text="Face Menu", icon="COLLAPSEMENU")
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_meshSelect"

    def draw_edit_curve_mode(self, pie, context):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        pie.menu("VIEW3D_MT_edit_curve_context_menu", text="Curve Menu", icon="COLLAPSEMENU")
        pie.operator("wm.call_menu_pie", text='Curve/Handle Type...').name = "SUBPIE_MT_curveTypeHandles"
        pie.operator("curve.cyclic_toggle")
        pie.separator()
        pie.operator("curve.switch_direction")
        pie.separator()
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_curveSelect"

    def draw_edit_gpencil_mode(self, pie, context):
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def draw_grease_pencil_paint_mode(self, pie, context):
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def draw_paint_texture_mode(self, pie, context):
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.image_paint.brush
        capabilities = brush.image_paint_capabilities

        if capabilities.has_color:
            split = layout.split(factor=0.1)
            UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
            UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
            layout.prop(brush, "blend", text="")

        if capabilities.has_radius:
            UnifiedPaintPanel.prop_unified(layout, context, brush, "size", unified_name="use_unified_size", pressure_name="use_pressure_size", slider=True)
            UnifiedPaintPanel.prop_unified(layout, context, brush, "strength", unified_name="use_unified_strength", pressure_name="use_pressure_strength", slider=True)

    def draw_paint_vertex_mode(self, pie, context):
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")
        pie.separator()
        box = pie.box()
        brush = context.tool_settings.vertex_paint.brush
        capabilities = brush.vertex_paint_capabilities

        if capabilities.has_color:
            split = layout.split(factor=0.1)
            UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
            UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
            layout.prop(brush, "blend", text="")

        UnifiedPaintPanel.prop_unified(layout, context, brush, "size", unified_name="use_unified_size", pressure_name="use_pressure_size", slider=True)
        UnifiedPaintPanel.prop_unified(layout, context, brush, "strength", unified_name="use_unified_strength", pressure_name="use_pressure_strength", slider=True)

    def draw_sculpt_mode(self, pie, context):
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")
        pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle")
        box = pie.box()
        brush = context.tool_settings.sculpt.brush
        capabilities = brush.sculpt_capabilities

        if capabilities.has_color:
            split = box.split(factor=0.1)
            UnifiedPaintPanel.prop_unified_color(split, context, brush, "color", text="")
            UnifiedPaintPanel.prop_unified_color_picker(split, context, brush, "color", value_slider=True)
            box.prop(brush, "blend", text="")

        UnifiedPaintPanel.prop_unified(box, context, brush, "size", unified_name="use_unified_size", pressure_name="use_pressure_size", text="Radius", slider=True)
        UnifiedPaintPanel.prop_unified(box, context, brush, "strength", unified_name="use_unified_strength", pressure_name="use_pressure_strength", slider=True)

    def draw_pose_mode(self, pie, context):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        pie.separator()
        pie.menu("VIEW3D_MT_pose_context_menu", text="Pose Context Menu", icon="COLLAPSEMENU")

    def draw_simple_edit_mode(self, pie, context):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        for _ in range(7): 
            pie.separator()

    def draw_edit_armature_mode(self, pie, context):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        for _ in range(5):  
            pie.separator()
        pie.menu("VIEW3D_MT_edit_armature_names")


###########################################################
########## SECOND IMPROVED VERSION ########################
###########################################################

class VIEW3D_PIE_MT_mode(Menu):
    bl_label = "Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        mode_handlers = {
            'OBJECT': self.handle_object_mode,
            'EDIT_MESH': self.handle_edit_mesh_mode,
            'EDIT_CURVE': self.handle_edit_curve_mode,
            'EDIT_GPENCIL': self.handle_simple_mode,
            'EDIT_GREASE_PENCIL': self.handle_simple_mode,
            'PAINT_GREASE_PENCIL': self.handle_simple_mode,
            'SCULPT_GREASE_PENCIL': self.handle_simple_mode,
            'PAINT_TEXTURE': self.handle_paint_texture_mode,
            'PAINT_VERTEX': self.handle_paint_vertex_mode,
            'SCULPT': self.handle_sculpt_mode,
            'POSE': self.handle_pose_mode,
            'EDIT_LATTICE': self.handle_simple_mode,
            'EDIT_ARMATURE': self.handle_edit_armature_mode,
        }
        
        handler = mode_handlers.get(context.mode, self.handle_default_mode)
        handler(context, pie)

    def handle_object_mode(self, context, pie):
        obj = context.object
        if obj and obj.type in {'MESH', 'GPENCIL', 'GREASEPENCIL', 'FONT'}:
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            subPie = pie.operator("wm.call_menu_pie", text='Select...")
            subPie.name = "SUBPIE_MT_objectSelect"
        elif obj and obj.type in {'CURVE', 'SURFACE', 'LATTICE', 'ARMATURE'}:
            pie.operator_enum("OBJECT_OT_mode_set", "mode")
            pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")
            subPie = pie.operator("wm.call_menu_pie", text='Select...")
            subPie.name = "SUBPIE_MT_objectSelect"
        else:
            pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def handle_edit_mesh_mode(self, context, pie):
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
        pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
        pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'
        pie.menu("VIEW3D_MT_edit_mesh_edges", text="edge menu", icon="COLLAPSEMENU")
        pie.menu("VIEW3D_MT_edit_mesh_vertices", text="vert menu", icon="COLLAPSEMENU")
        pie.menu("VIEW3D_MT_edit_mesh_faces", text="face menu", icon="COLLAPSEMENU")
        pie.operator("wm.call_menu_pie", text='Select...").name = "SUBPIE_MT_meshSelect"

    def handle_edit_curve_mode(self, context, pie):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        pie.menu("VIEW3D_MT_edit_curve_context_menu", text="curve menu", icon="COLLAPSEMENU")
        pie.operator("wm.call_menu_pie", text='Curve/Handle Type...").name = "SUBPIE_MT_curveTypeHandles"
        pie.operator("curve.cyclic_toggle")
        pie.operator("curve.switch_direction")

    def handle_paint_texture_mode(self, context, pie):
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        brush = context.tool_settings.image_paint.brush
        capabilities = brush.image_paint_capabilities
        if capabilities.has_color:
            UnifiedPaintPanel.prop_unified_color(pie.box(), context, brush, "color", text="")
        if capabilities.has_radius:
            UnifiedPaintPanel.prop_unified(pie.box(), context, brush, "size", unified_name="use_unified_size", slider=True)

    def handle_paint_vertex_mode(self, context, pie):
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        brush = context.tool_settings.vertex_paint.brush
        UnifiedPaintPanel.prop_unified(pie.box(), context, brush, "size", unified_name="use_unified_size", slider=True)

    def handle_sculpt_mode(self, context, pie):
        pie.operator("object.mode_set", text="object mode", icon="OBJECT_DATAMODE")
        pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle")
        brush = context.tool_settings.sculpt.brush
        if brush.sculpt_capabilities.has_color:
            UnifiedPaintPanel.prop_unified_color(pie.box(), context, brush, "color", text="")

    def handle_pose_mode(self, context, pie):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        pie.menu("VIEW3D_MT_pose_context_menu", text="Pose Context Menu", icon="COLLAPSEMENU")

    def handle_edit_armature_mode(self, context, pie):
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
        pie.menu("VIEW3D_MT_edit_armature_names")

    def handle_simple_mode(self, context, pie):
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def handle_default_mode(self, context, pie):
        pie.separator()





#########################################################
################ CLAIMED IMPROVEMENTS AND COMMENTS


import bpy
from bpy.types import Menu

class VIEW3D_PIE_MT_mode(Menu):
    bl_label = "Mode Selection"

    def draw(self, context):
        mode_handlers = {
            'OBJECT': self.object_mode_pie,
            'EDIT_MESH': self.edit_mesh_pie,
            'EDIT_CURVE': self.edit_curve_pie,
            'EDIT_GPENCIL': self.edit_gpencil_pie,
            'PAINT_GREASE_PENCIL': self.paint_grease_pencil_pie,
            'SCULPT_GREASE_PENCIL': self.sculpt_grease_pencil_pie,
            'PAINT_TEXTURE': self.paint_texture_pie,
            'PAINT_VERTEX': self.paint_vertex_pie,
            'SCULPT': self.sculpt_pie,
            'POSE': self.pose_pie,
            'EDIT_LATTICE': self.edit_lattice_pie,
            'EDIT_ARMATURE': self.edit_armature_pie
        }

        handler = mode_handlers.get(context.mode, self.default_pie)
        handler(context)

    def object_mode_pie(self, context):
        """Pie menu for OBJECT mode"""
        layout = self.layout
        pie = layout.menu_pie()
        obj = context.object

        # NORTH
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

        # SOUTH
        pie.menu("VIEW3D_MT_object_context_menu", text="Object Menu")

        # EAST
        subPie = pie.operator("wm.call_menu_pie", text='Select...')
        subPie.name = "SUBPIE_MT_objectSelect"

        # WEST
        if obj and obj.type in {'CURVE', 'SURFACE', 'LATTICE', 'ARMATURE'}:
            pie.separator()

    def edit_mesh_pie(self, context):
        """Pie menu for EDIT MESH mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch back to Object Mode
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")

        # SOUTH - Edge Selection
        pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'

        # EAST - Vertex Selection
        pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'

        # WEST - Face Selection
        pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'

        # NW - Edge Menu
        pie.menu("VIEW3D_MT_edit_mesh_edges", text="Edge Menu", icon="COLLAPSEMENU")

        # NE - Vertex Menu
        pie.menu("VIEW3D_MT_edit_mesh_vertices", text="Vert Menu", icon="COLLAPSEMENU")

        # SW - Face Menu
        pie.menu("VIEW3D_MT_edit_mesh_faces", text="Face Menu", icon="COLLAPSEMENU")

        # SE - Select Menu
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_meshSelect"

    def edit_curve_pie(self, context):
        """Pie menu for EDIT CURVE mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")

        # SOUTH - Curve Menu
        pie.menu("VIEW3D_MT_edit_curve_context_menu", text="Curve Menu", icon="COLLAPSEMENU")

        # EAST - Change Curve Type
        pie.operator("wm.call_menu_pie", text='Curve/Handle Type...').name = "SUBPIE_MT_curveTypeHandles"

        # WEST - Curve Operations
        pie.operator("curve.cyclic_toggle")
        pie.operator("curve.switch_direction")

    def edit_gpencil_pie(self, context):
        """Pie menu for EDIT GREASE PENCIL mode"""
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def paint_grease_pencil_pie(self, context):
        """Pie menu for PAINT GREASE PENCIL mode"""
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def sculpt_grease_pencil_pie(self, context):
        """Pie menu for SCULPT GREASE PENCIL mode"""
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("OBJECT_OT_mode_set", "mode")

    def paint_texture_pie(self, context):
        """Pie menu for TEXTURE PAINT mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")

        # SOUTH - Separator
        pie.separator()

        # CENTER - Empty Box (for future expansion)
        pie.box()

    def paint_vertex_pie(self, context):
        """Pie menu for VERTEX PAINT mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")

        # SOUTH - Separator
        pie.separator()

        # CENTER - Empty Box (for future expansion)
        pie.box()

    def sculpt_pie(self, context):
        """Pie menu for SCULPT mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", text="Object Mode", icon="OBJECT_DATAMODE")

        # SOUTH - Toggle Dyntopo
        pie.operator("sculpt.dynamic_topology_toggle", text="Dyntopo Toggle")

        # CENTER - Empty Box (for future expansion)
        pie.box()

    def pose_pie(self, context):
        """Pie menu for POSE mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")

        # SOUTH - Pose Context Menu
        pie.menu("VIEW3D_MT_pose_context_menu", text="Pose Context Menu", icon="COLLAPSEMENU")

    def edit_lattice_pie(self, context):
        """Pie menu for EDIT LATTICE mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")

    def edit_armature_pie(self, context):
        """Pie menu for EDIT ARMATURE mode"""
        layout = self.layout
        pie = layout.menu_pie()

        # NORTH - Switch to Object Mode
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")

        # SOUTH - Armature Context Menu
        pie.menu("VIEW3D_MT_edit_armature_names")

    def default_pie(self, context):
        """Fallback pie menu if mode is not recognized"""
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("object.mode_set", icon="OBJECT_DATAMODE")
