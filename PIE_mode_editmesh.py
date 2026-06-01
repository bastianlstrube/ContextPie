# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie

###-----------------------------------------------------------------------------###
###                             CUSTOM OPERATORS                                ###
###-----------------------------------------------------------------------------###

class CPIE_OT_interactive_automerge_threshold(bpy.types.Operator):
    bl_idname = "mesh.interactive_automerge_threshold"
    bl_label = "Interactive Automerge Threshold"
    bl_description = "Drag mouse horizontally to interactively adjust the AutoMerge threshold"
    bl_options = {'REGISTER', 'UNDO'}

    init_mouse_x: bpy.props.IntProperty()
    init_threshold: bpy.props.FloatProperty()

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            delta = event.mouse_x - self.init_mouse_x
            sensitivity = 0.00005 if event.shift else 0.0005
            
            # Calculate and apply new threshold (clamped to 0 minimum)
            new_threshold = self.init_threshold + (delta * sensitivity)
            context.scene.tool_settings.double_threshold = max(0.0, new_threshold)
            
            # Displays live feedback clearly in the 3D Viewport Header
            context.area.header_text_set(
                f"AutoMerge Threshold: {context.scene.tool_settings.double_threshold:.4f}m  |  "
                f"[Left-Click] Confirm  |  [Right-Click/Esc] Cancel"
            )

        elif event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            context.area.header_text_set(None) # Clear header
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.scene.tool_settings.double_threshold = self.init_threshold
            context.area.header_text_set(None) # Clear header
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            # Store starting positions
            self.init_mouse_x = event.mouse_x
            self.init_threshold = context.scene.tool_settings.double_threshold
            
            # Make AutoMerge turn on automatically if they run this tool
            context.scene.tool_settings.use_mesh_automerge = True
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}

###-----------------------------------------------------------------------------###
###                     SELECT & SEPARATE SUBPIES                               ###
###-----------------------------------------------------------------------------###


class SUBPIE_MT_meshSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("mesh.region_to_loop", text='Boundary')
        # EAST
        pie.operator("mesh.select_edge_ring_multi", text='Ring')
        # SOUTH
        pie.operator("mesh.select_edge_loop_multi", text='Loop')
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


###-----------------------------------------------------------------------------###
###                           TOOL OPTIONS SUBPIE                               ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_tool_options(Menu):
    bl_label = "Tool Options"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        tool_settings = context.scene.tool_settings
        obj = context.active_object
        mesh = obj.data if (obj and obj.type == 'MESH') else None

        # WEST: Mesh Symmetry (X, Y, Z)
        col_mirror = pie.column()
        col_mirror.label(text="Mesh Symmetry")
        if mesh:
            col_mirror.prop(mesh, "use_mirror_x", text="X")
            col_mirror.prop(mesh, "use_mirror_y", text="Y")
            col_mirror.prop(mesh, "use_mirror_z", text="Z")
        else:
            col_mirror.label(text="No Active Mesh")

        # EAST: AutoMerge & Threshold Slider
        pie.prop(tool_settings, "use_mesh_automerge", text="AutoMerge")

        # SOUTH: Live Unwrap
        pie.prop(tool_settings, "use_edge_path_live_unwrap", text="Live Unwrap")

        # NORTH: Correct Face Attributes
        pie.prop(tool_settings, "use_transform_correct_face_attributes", text="Correct Face Attributes")

        # NORTH-WEST
        pie.separator()
        # NORTH-EAST: AutoMerge & Interactive Drag Button
        #box_merge = pie.box().column()
        #box_merge.prop(tool_settings, "use_mesh_automerge", text="AutoMerge")
        # Snappy interactive tool triggers dynamic mouse adjustments
        pie.operator("mesh.interactive_automerge_threshold", text="Automerge Threshold", icon="MOUSE_MOVE")
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


class CPIE_MT_mode_editmesh(Menu):
    bl_idname = "CPIE_MT_mode_editmesh"
    bl_label = "Mode Pie: Edit Mesh"

    def draw(self, context):
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
        pie.operator("wm.call_menu_pie", text='Tool Options...').name = "SUBPIE_MT_tool_options"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Split/Separate...').name = "SUBPIE_MT_separate"
        # SOUTH-WEST
        pie.menu("VIEW3D_MT_edit_mesh_context_menu", text="Context Menu", icon="COLLAPSEMENU")
        # SOUTH-EAST
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_meshSelect"


registry = [
    CPIE_OT_interactive_automerge_threshold,
    SUBPIE_MT_meshSelect,
    SUBPIE_MT_separate,
    SUBPIE_MT_tool_options,
    CPIE_MT_mode_editmesh,
]


def register():
    default_keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
    if "Mesh" not in default_keymaps:
        return
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=CPIE_MT_mode_editmesh.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        keymap_name="Mesh",
        on_drag=True,
    )
