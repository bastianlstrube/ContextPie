# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu, Operator
from bpy.props import EnumProperty


# Properties checked in order — first match wins.
_PRIORITY_PROPS = (
    'operation', 'blend_type', 'mode', 'interpolation',
    'distribution', 'data_type', 'domain',
)

# Base-class Node properties that are enum-typed but not a "mode" selector.
_SKIP_PROPS = frozenset({
    'rna_type', 'type', 'location', 'width', 'width_hidden', 'height',
    'label', 'use_custom_color', 'color', 'select',
    'show_options', 'show_preview', 'hide', 'mute', 'name',
})


def _find_mode_property(node):
    """Return the identifier of the node's primary mode/operation enum property."""
    for name in _PRIORITY_PROPS:
        prop = node.bl_rna.properties.get(name)
        if prop and prop.type == 'ENUM' and not prop.is_readonly:
            return name
    for prop in node.bl_rna.properties:
        if (prop.type == 'ENUM'
                and not prop.is_readonly
                and prop.identifier not in _SKIP_PROPS):
            return prop.identifier
    return None


def _mode_items(self, context):
    """Dynamic enum items read from the active node's primary enum property."""
    items = [('NONE', "No Mode Found", "")]
    if context and context.active_node:
        prop_name = _find_mode_property(context.active_node)
        if prop_name:
            rna_prop = context.active_node.bl_rna.properties.get(prop_name)
            if rna_prop:
                items = [
                    (item.identifier, item.name, item.description, item.icon, i)
                    for i, item in enumerate(rna_prop.enum_items_static)
                ]
    # Store on the function to prevent Python GC'ing the list before Blender reads it.
    _mode_items._cache = items
    return items


# ==============================================================================
# NODE_OT_cpie_set_mode — apply one enum value to all selected matching nodes
# ==============================================================================

class NODE_OT_cpie_set_mode(Operator):
    bl_idname = "node.cpie_set_mode"
    bl_label = "Set Node Mode"
    bl_description = "Set operation/mode on all selected nodes that support it"
    bl_options = {'REGISTER', 'UNDO'}

    value: EnumProperty(items=_mode_items)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'NODE_EDITOR'
                and context.space_data.node_tree is not None)

    def execute(self, context):
        for node in context.selected_nodes:
            prop_name = _find_mode_property(node)
            if prop_name:
                try:
                    setattr(node, prop_name, self.value)
                except Exception:
                    pass
        return {'FINISHED'}


# ==============================================================================
# NODE_OT_cpie_cycle_mode — modal: scroll / arrow-keys cycle through options
# ==============================================================================

class NODE_OT_cpie_cycle_mode(Operator):
    bl_idname = "node.cpie_cycle_mode"
    bl_label = "Cycle Node Mode"
    bl_description = (
        "Scroll or arrow-keys to cycle through the node's operation/mode "
        "on all selected nodes. Click or Enter to confirm, Esc to cancel"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'NODE_EDITOR'
                and context.space_data.node_tree is not None
                and context.active_node is not None)

    def invoke(self, context, event):
        active = context.active_node
        prop_name = _find_mode_property(active)
        if not prop_name:
            self.report({'WARNING'}, "No mode property found on active node")
            return {'CANCELLED'}

        self._prop_name = prop_name
        rna_prop = active.bl_rna.properties[prop_name]
        self._items = [item.identifier for item in rna_prop.enum_items_static]

        self._originals = {}
        for node in context.selected_nodes:
            if hasattr(node, prop_name):
                self._originals[node] = getattr(node, prop_name)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'WHEELUPMOUSE', 'UP_ARROW'} and event.value == 'PRESS':
            self._step(context, 1)
            return {'RUNNING_MODAL'}
        if event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW'} and event.value == 'PRESS':
            self._step(context, -1)
            return {'RUNNING_MODAL'}
        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            for node, orig in self._originals.items():
                try:
                    setattr(node, self._prop_name, orig)
                except Exception:
                    pass
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def _step(self, context, direction):
        active = context.active_node
        if not active or not hasattr(active, self._prop_name):
            return
        current = getattr(active, self._prop_name)
        items = self._items
        idx = items.index(current) if current in items else 0
        new_val = items[(idx + direction) % len(items)]
        for node in context.selected_nodes:
            if hasattr(node, self._prop_name):
                try:
                    setattr(node, self._prop_name, new_val)
                except Exception:
                    pass


# ==============================================================================
# SUBPIE_MT_node_dynamic_mode — pie built from the active node's enum property
# ==============================================================================

class SUBPIE_MT_node_dynamic_mode(Menu):
    bl_label = "Node Mode"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_set_mode", "value")


registry = [
    NODE_OT_cpie_set_mode,
    NODE_OT_cpie_cycle_mode,
    SUBPIE_MT_node_dynamic_mode,
]
