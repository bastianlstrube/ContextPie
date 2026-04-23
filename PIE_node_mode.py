# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# ==============================================================================
# 1. SELECT SUB-MENU
# ==============================================================================

class SUBPIE_MT_nodeSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        nw_loaded = "node_wrangler" in context.preferences.addons

        # Opened from SE: cluster primary options at SE/S/E, secondary at SW/NE.

        # WEST
        pie.operator("node.select_all", text="Deselect All").action = 'DESELECT'
        # EAST
        pie.operator("node.select_linked_to", text="Linked To (Upstream)")
        # SOUTH
        pie.operator("node.select_all", text="Select All").action = 'SELECT'
        # NORTH
        pie.operator("node.select_grouped", text="Select Same Type").type = 'TYPE'
        # NORTH-WEST
        if nw_loaded:
            pie.operator("node.nw_select_parent_child", text="Select Parent Frame").option = 'PARENT'
        else:
            pie.separator()
        # NORTH-EAST
        if nw_loaded:
            pie.operator("node.nw_select_parent_child", text="Select Frame Children").option = 'CHILD'
        else:
            pie.separator()
        # SOUTH-WEST
        pie.operator("node.select_all", text="Invert").action = 'INVERT'
        # SOUTH-EAST - primary: select downstream linked nodes
        pie.operator("node.select_linked_from", text="Linked From (Downstream)")


# ==============================================================================
# 2. MAIN NODE MODE PIE
# ==============================================================================

class NODE_PIE_MT_mode(Menu):
    bl_idname = "NODE_PIE_MT_mode_pie"
    bl_label = "Node Navigation"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        pie = layout.menu_pie()

        if context.space_data.type != 'NODE_EDITOR' or not context.space_data.node_tree:
            return

        nw_loaded = "node_wrangler" in context.preferences.addons
        is_geo = context.space_data.tree_type == 'GeometryNodeTree'

        # WEST - create group from selection
        pie.operator("node.group_make", text="Make Group", icon='NODETREE')
        # EAST - dissolve group back to nodes
        pie.operator("node.group_ungroup", text="Ungroup", icon='NODETREE')
        # SOUTH - navigate up the group stack
        pie.operator("node.tree_path_parent", text="Exit Group", icon='FILE_PARENT')
        # NORTH - dive into selected group node
        pie.operator("node.group_edit", text="Enter Group", icon='NODETREE').exit = False
        # NORTH-WEST - move selection inside an existing group
        pie.operator("node.group_insert", text="Insert into Group", icon='NODETREE')
        # NORTH-EAST - link active node to viewer/output
        if nw_loaded:
            pie.operator("node.nw_link_out", text="Link to Output", icon='DRIVER')
        elif is_geo:
            pie.operator("node.link_viewer", text="Link to Viewer", icon='HIDE_OFF')
        else:
            pie.operator("node.find_node", text="Find Node...", icon='VIEWZOOM')
        # SOUTH-WEST - remove node(s) from their frame
        pie.operator("node.detach", text="Remove from Frame", icon='GROUP_VERTEX')
        # SOUTH-EAST - select submenu (consistent with all other mode pies)
        pie.operator("wm.call_menu_pie", text="Select...", icon='RESTRICT_SELECT_OFF').name = "SUBPIE_MT_nodeSelect"


# ==============================================================================
# 3. REGISTRATION
# ==============================================================================

registry = [
    SUBPIE_MT_nodeSelect,
    NODE_PIE_MT_mode,
]

def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=NODE_PIE_MT_mode.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        keymap_name="Node Editor",
        on_drag=True,
    )

def unregister():
    pass
