# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu, Operator

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# ==============================================================================
#                               OPERATORS
# ==============================================================================

class IMAGE_OT_cpie_uv_snap_set(Operator):
    """Set the active UV snap element exclusively (clearing other selections)"""
    bl_idname = "image.cpie_uv_snap_set"
    bl_label = "Set UV Snap Element"
    bl_options = {'REGISTER', 'UNDO'}

    element: bpy.props.EnumProperty(
        items=[
            ('INCREMENT', "Increment", ""),
            ('VERTEX', "Vertex", ""),
            ('GRID', "Grid", ""),
        ]
    )

    def execute(self, context):
        try:
            # Overwrite the flag set container to enforce strict single-choice selection
            context.tool_settings.snap_uv_element = {self.element}
        except Exception as e:
            self.report({'WARNING'}, f"Could not set UV snap element: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}


# ==============================================================================
#                                   MENUS
# ==============================================================================

class SUBPIE_MT_uv_snap(Menu):
    bl_idname = "SUBPIE_MT_uv_snap"
    bl_label = "UV Snap Settings"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        ts = context.tool_settings

        # Read the current flag set container state to drive menu button highlighting
        current_elements = getattr(ts, "snap_uv_element", set())

        # 1. WEST (Left)
        op = pie.operator("image.cpie_uv_snap_set", text="Increment", icon='SNAP_INCREMENT', 
                          depress=('INCREMENT' in current_elements))
        op.element = 'INCREMENT'
        
        # 2. EAST (Right) - Matches your 3D Vertex layout placement
        op = pie.operator("image.cpie_uv_snap_set", text="Vertex", icon='SNAP_VERTEX', 
                          depress=('VERTEX' in current_elements))
        op.element = 'VERTEX'
        
        # 3. SOUTH (Bottom) - Matches your 3D Magnet toggle layout placement
        pie.prop(ts, "use_snap_uv", text="Snap On/Off", toggle=True, icon="SNAP_ON")
        
        # 4. NORTH (Top) - Unified absolute grid check with fail-safe properties
        if hasattr(ts, "use_snap_grid_absolute"):
            pie.prop(ts, "use_snap_grid_absolute", text="Absolute Grid", toggle=True, icon='SNAP_GRID')
        elif hasattr(ts, "use_snap_uv_grid_absolute"):
            pie.prop(ts, "use_snap_uv_grid_absolute", text="Absolute Grid", toggle=True, icon='SNAP_GRID')
        else:
            pie.separator()
        
        # 5. NORTH-WEST
        pie.separator()
        
        # 6. NORTH-EAST
        pie.separator()
        
        # 7. SOUTH-WEST (Bottom-Left) - Matches your 3D Grid layout placement
        op = pie.operator("image.cpie_uv_snap_set", text="Grid", icon='SNAP_GRID', 
                          depress=('GRID' in current_elements))
        op.element = 'GRID'
        
        # 8. SOUTH-EAST
        pie.separator()


class IMAGE_PIE_MT_uvPivots(Menu):
    bl_idname = "PIE_MT_context_uvpivots"
    bl_label = "UV Pivots"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # 1. WEST
        pie.separator()
        # 2. EAST
        pie.operator("wm.call_menu_pie", text='Pivot...', icon="RIGHTARROW_THIN").name = "IMAGE_MT_pivot_pie"
        # 3. SOUTH - Wired into our fixed single-choice tool snapping submenu
        pie.operator("wm.call_menu_pie", text='Snap...', icon="RIGHTARROW_THIN").name = "SUBPIE_MT_uv_snap"
        # 4. NORTH
        pie.operator("wm.call_menu_pie", text='Proportional...', icon="RIGHTARROW_THIN").name = "SUBPIE_MT_proportional_edt"
        # 5. NORTH-WEST
        pie.separator()
        # 6. NORTH-EAST
        pie.separator()
        # 7. SOUTH-WEST
        pie.separator()
        # 8. SOUTH-EAST
        pie.separator()


# Make sure the operator class is appended into the registry array list so the addon boots it
registry = [
    IMAGE_OT_cpie_uv_snap_set,
    SUBPIE_MT_uv_snap,
    IMAGE_PIE_MT_uvPivots,
]


def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=IMAGE_PIE_MT_uvPivots.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
        keymap_name="UV Editor",
    )