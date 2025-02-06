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