# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class NODE_PIE_MT_pivots(Menu):
    bl_idname = "NODE_PIE_MT_pivots_pie"
    bl_label = "Node Connections"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        pie = layout.menu_pie()

        if context.space_data.type != 'NODE_EDITOR' or not context.space_data.node_tree:
            return

        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST - drag across links to cut them
        pie.operator("node.links_cut", text="Cut Links", icon='SCULPTMODE_HLT')
        # EAST - drag across links to mute/unmute them
        pie.operator("node.links_mute", text="Mute Links", icon='HIDE_OFF')
        # SOUTH - sever all connections on selected nodes
        pie.operator("node.links_detach", text="Detach Links", icon='UNLINKED')
        # NORTH - auto-connect selected nodes by matching socket types
        pie.operator("node.link_make", text="Make Links", icon='LINKED')
        # NORTH-WEST - like Make Links but overwrites existing connections
        pie.operator("node.link_make", text="Make & Replace Links", icon='LINKED').replace = True
        # NORTH-EAST - swap the links between two selected nodes (NW)
        if nw_loaded:
            pie.operator("node.nw_swap_links", text="Swap Links", icon='FILE_REFRESH')
        else:
            pie.separator()
        # SOUTH-WEST - drag from node to node to connect interactively (NW)
        if nw_loaded:
            pie.operator("node.nw_lazy_connect", text="Lazy Connect", icon='DRIVER').with_menu = False
        else:
            pie.separator()
        # SOUTH-EAST - drag from node to node to insert a mix node (NW)
        if nw_loaded:
            pie.operator("node.nw_lazy_mix", text="Lazy Mix", icon='NODE')
        else:
            pie.separator()

        # Extras dropdown
        if nw_loaded:
            pie.separator()
            pie.separator()
            dropdown = pie.column()
            gap = dropdown.column()
            gap.separator()
            gap.scale_y = 8
            dropdown_menu = dropdown.box().column()
            dropdown_menu.scale_y = 1
            dropdown_menu.operator("node.nw_detach_outputs", text="Detach Outputs (Keep Inputs)")


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
