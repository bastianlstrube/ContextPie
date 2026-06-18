# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class NODE_PIE_MT_pivots(Menu):
    bl_idname = "NODE_PIE_MT_pivots_pie"
    bl_label = "Node Links"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        pie = layout.menu_pie()

        if context.space_data.type != 'NODE_EDITOR' or not context.space_data.node_tree:
            return

        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST - drag across links to cut them
        pie.operator("node.links_cut", text="Cut Links", icon='SCULPTMODE_HLT')
        # EAST - drag across links to add a reroute
        pie.operator("node.add_reroute", text="Add Reroute", icon='NODE')
        # SOUTH - sever all connections on selected nodes
        pie.operator("node.links_detach", text="Detach All Links", icon='UNLINKED')
        # NORTH - auto-connect selected nodes by matching socket types
        pie.operator("node.link_make", text="Make Links", icon='LINKED')
        # NORTH-WEST - like Make Links but overwrites existing connections
        pie.operator("node.link_make", text="Make & Replace Links", icon='LINKED').replace = True
        # NORTH-EAST - swap the links between two selected nodes (NW)
        if nw_loaded:
            pie.operator("node.nw_swap_links", text="Swap Links", icon='FILE_REFRESH')
        else:
            pie.separator()
        # SOUTH-WEST - detach only the outputs of selected nodes (NW), clustered with
        # Detach All Links (S) and Cut Links (W). (Lazy Connect can't live in a pie slot:
        # it's a click-drag modal that ends on the release that picks the slot — use NW's
        # native Alt+RMB drag instead.)
        if nw_loaded:
            pie.operator("node.nw_detach_outputs", text="Detach Outputs", icon='UNLINKED')
        else:
            pie.separator()
        # SOUTH-EAST - add reroute nodes to all outputs (NW), clustered with Add Reroute (E)
        if nw_loaded:
            pie.operator("node.nw_add_reroutes", text="Add Reroutes", icon='NODE').option = 'ALL'
        else:
            pie.separator()


# ==============================================================================
# REGISTRATION
# ==============================================================================

registry = [
    NODE_PIE_MT_pivots,
]

def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=NODE_PIE_MT_pivots.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
        keymap_name="Node Editor",
        on_drag=False,
    )

def unregister():
    pass
