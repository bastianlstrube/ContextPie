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
# 2. LABELS & SETTINGS SUB-MENU (Node Wrangler)
# ==============================================================================

class SUBPIE_MT_nw_labels_settings(Menu):
    bl_label = "Labels & Settings"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Opened from NORTH-EAST: cluster items at NE/N/E/NW/SE, separators at W/S/SW.
        # WEST
        pie.separator()
        # EAST
        pie.operator("node.nw_reload_images", text="Reload Images", icon='FILE_REFRESH')
        # SOUTH
        pie.separator()
        # NORTH
        pie.operator("node.nw_modify_label", text="Modify Label", icon='SORTALPHA')
        # NORTH-WEST
        pie.operator("node.nw_copy_settings", text="Copy Settings", icon='COPYDOWN')
        # NORTH-EAST - primary (occupies Align Nodes' former mode-pie slot)
        pie.operator("node.nw_align_nodes", text="Align Nodes", icon='ALIGN_JUSTIFY')
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST - clear the label off selected nodes (option=True targets selection)
        pie.operator("node.nw_clear_label", text="Clear Label", icon='X').option = True


# ==============================================================================
# 3. MAIN NODE MODE PIE
# ==============================================================================

class CPIE_MT_mode_node(Menu):
    bl_idname = "CPIE_MT_mode_node"
    bl_label = "Mode Pie: Node Editor"

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
        # NORTH-EAST - Node Wrangler labels, settings & align utilities submenu
        if nw_loaded:
            pie.operator("wm.call_menu_pie", text="Labels & Settings...", icon='ALIGN_JUSTIFY').name = "SUBPIE_MT_nw_labels_settings"
        else:
            pie.separator()
        # SOUTH-WEST - wrap selected nodes in a frame
        pie.operator("node.join", text="Frame Selected", icon='STICKY_UVS_LOC')
        # SOUTH-EAST - select submenu (consistent with all other mode pies)
        pie.operator("wm.call_menu_pie", text="Select...", icon='RESTRICT_SELECT_OFF').name = "SUBPIE_MT_nodeSelect"

        # Extras dropdown
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        dropdown_menu.operator("node.detach", text="Remove from Frame", icon='GROUP_VERTEX')
        if nw_loaded:
            dropdown_menu.operator("node.nw_link_out", text="Link to Output", icon='DRIVER')
        elif is_geo:
            dropdown_menu.operator("node.link_viewer", text="Link to Viewer", icon='HIDE_OFF')


# ==============================================================================
# 4. REGISTRATION
# ==============================================================================

registry = [
    SUBPIE_MT_nodeSelect,
    SUBPIE_MT_nw_labels_settings,
    CPIE_MT_mode_node,
]

def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=CPIE_MT_mode_node.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        keymap_name="Node Editor",
        on_drag=True,
    )

def unregister():
    pass
