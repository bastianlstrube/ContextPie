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
from bpy.app.translations import contexts as i18n_contexts


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

class VIEW3D_PIE_MT_mode(Menu):
    bl_label  = "Mode Selection"

    def draw(self, context):
        
        if context.mode == 'OBJECT':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()

            obj = context.object
            
            if obj is not None and obj.type in {'MESH', 'GPENCIL', 'FONT'}:

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
            subPie = pie.operator("wm.call_menu_pie", text='Select...')
            subPie.name = "SUBPIE_MT_meshSelect"  

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
            pie.operator("curve.spline_type_set", text='Set Type Bezier').type = 'BEZIER'
            # NORTH
            pie.operator("curve.cyclic_toggle")
            
            # NORTH-WEST
            pie.separator()
            # NORTH-EAST
            pie.operator("curve.switch_direction")
            # SOUTH-WEST
            pie.operator("curve.spline_type_set", text='Set Type Poly').type = 'POLY'
            # SOUTH-EAST
            pie.operator("curve.spline_type_set", text='Set Type NURBS').type = 'NURBS'

        elif context.mode == 'EDIT_GPENCIL':

            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            pie = layout.menu_pie()
            
            # WEST # EAST # SOUTH # NORTH # NORTH-WEST # NORTH-EAST
            pie.operator_enum("OBJECT_OT_mode_set", "mode")

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

registry = [
    SUBPIE_MT_objectSelect,
    SUBPIE_MT_meshSelect,
    VIEW3D_PIE_MT_mode,
]

addon_keymaps = []

def register():

    categories = ["Object Mode", "Mesh", "Curve", "Grease Pencil Edit Mode", "Sculpt", "Pose", "Lattice", "Armature"]

    for cat in categories:
        register_hotkey(
            'wm.call_menu_pie_drag_only_cpie',
            op_kwargs={'name': 'VIEW3D_PIE_MT_mode'},
            hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
            key_cat=cat,
        )

    
    '''wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Mesh')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Curve')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Grease Pencil Edit Mode')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Sculpt')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Pose')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Lattice')#, space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=False)
        kmi.properties.name = "VIEW3D_PIE_MT_mode"
        addon_keymaps.append((km, kmi))'''

'''def unregister():
    for cls in registry:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()

    #bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_mode")'''
