# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


# ==============================================================================
# ADD-NODE HELPER — shared by every category sub-pie
# ==============================================================================
# When _ADD_CONNECT_MODE is on, the category sub-pies are being browsed through the
# single-node "Add Connect" pie, so their leaves spawn a node *and* wire the active
# node into it. Otherwise (the no-selection add pies) they just drop a bare node.
# The flag is reset every time the main context pie is drawn (see NODE_PIE_MT_context).
_ADD_CONNECT_MODE = False


def _add_node_op(pie, text, node_type, icon='NONE'):
    """Emit an add-node button, routed to the connect operator while in Add Connect mode."""
    if _ADD_CONNECT_MODE:
        pie.operator("node.cpie_add_connect", text=text, icon=icon).node_type = node_type
    else:
        pie.operator("node.add_node", text=text, icon=icon).type = node_type


class CONTEXTPIE_OT_combine_selected(bpy.types.Operator):
    """Combine the first outputs of selected nodes into a Combine XYZ or Combine Color node"""
    bl_idname = "node.cpie_combine_selected"
    bl_label = "Combine Selected Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    combine_type: bpy.props.EnumProperty(
        items=[
            ('XYZ', "Combine XYZ", "Combine into XYZ"),
            ('COLOR', "Combine Color", "Combine into Color"),
        ],
        default='XYZ'
    )

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None and len(context.selected_nodes) > 0

    def execute(self, context):
        tree = context.space_data.node_tree
        nodes = tree.nodes
        links = tree.links
        selected_nodes = context.selected_nodes

        if not selected_nodes:
            return {'CANCELLED'}

        tree_type = tree.bl_idname

        # Determine Target Node Type based on the editor context
        if self.combine_type == 'XYZ':
            if tree_type in ('GeometryNodeTree', 'ShaderNodeTree'):
                target_type = 'ShaderNodeCombineXYZ'
            else:
                self.report({'WARNING'}, "Combine XYZ not supported in this tree type.")
                return {'CANCELLED'}
        else: # COLOR
            if tree_type == 'ShaderNodeTree':
                target_type = 'ShaderNodeCombineColor'
            elif tree_type == 'GeometryNodeTree':
                target_type = 'FunctionNodeCombineColor'
            elif tree_type == 'CompositorNodeTree':
                target_type = 'CompositorNodeCombineColor'
            else:
                self.report({'WARNING'}, "Combine Color not supported in this tree type.")
                return {'CANCELLED'}

        # Spawn the node
        new_node = nodes.new(type=target_type)

        # Maintain frame attachment if nodes are inside a frame
        active_node = context.active_node
        parent_frame = active_node.parent if (active_node in selected_nodes) else selected_nodes[0].parent
        if parent_frame:
            new_node.parent = parent_frame

        # Position it to the right of the selected block
        avg_x = sum(n.location.x for n in selected_nodes) / len(selected_nodes)
        avg_y = sum(n.location.y for n in selected_nodes) / len(selected_nodes)
        max_width = max(n.width for n in selected_nodes)
        new_node.location = (avg_x + max_width + 40, avg_y)

        # Helper Function: Recursively trace upstream to find the channel identity (X/Y/Z/W or R/G/B/A)
        def get_logical_index(socket, depth=0):
            if depth > 5: return None # Prevent infinite loops

            name = socket.name.upper()
            if name in ('X', 'R', 'RED'): return 0
            if name in ('Y', 'G', 'GREEN'): return 1
            if name in ('Z', 'B', 'BLUE'): return 2
            if name in ('W', 'A', 'ALPHA'): return 3

            # If the socket name is generic (like "Value"), trace its node's inputs backward
            for inp in socket.node.inputs:
                if inp.is_linked:
                    idx = get_logical_index(inp.links[0].from_socket, depth + 1)
                    if idx is not None:
                        return idx
            return None

        # Gather "Terminal" outputs: outputs that don't plug into another selected node
        selected_nodes.sort(key=lambda n: n.location.y, reverse=True) # Fallback sorting
        terminal_sockets = _terminal_outputs(selected_nodes)

        # Setup target slots (Combine XYZ has 3, Combine Color has 4)
        num_slots = min(len(new_node.inputs), 4)
        slots = [None] * num_slots
        leftovers = []

        # Pass 1: Analyze terminal sockets and place them in their traced logical slots
        for out in terminal_sockets:
            idx = get_logical_index(out)
            if idx is not None and idx < num_slots and slots[idx] is None:
                slots[idx] = out
            else:
                leftovers.append(out)

        # Pass 2: Fill any remaining empty slots with the leftovers top-to-bottom
        for i in range(num_slots):
            if slots[i] is None and leftovers:
                slots[i] = leftovers.pop(0)

        # Connect the slots to the new node
        for i, out in enumerate(slots):
            if out is not None:
                links.new(out, new_node.inputs[i])

        # Deselect old nodes, make the new node active
        for n in selected_nodes:
            n.select = False
        new_node.select = True
        tree.nodes.active = new_node

        return {'FINISHED'}


###-----------------------------------------------------------------------------###
###                          Delete Add Reroute                                 ###
###-----------------------------------------------------------------------------###

class NODE_OT_delete_add_reroute(bpy.types.Operator):
    """Delete the active node and insert a reroute node precisely at the active output socket"""
    bl_idname = "node.delete_add_reroute"
    bl_label = "Delete Add Reroute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space and space.type == 'NODE_EDITOR' and space.edit_tree and context.active_node

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        node = context.active_node
        
        if node.type == 'REROUTE':
            self.report({'INFO'}, "Selected node is already a reroute.")
            return {'CANCELLED'}
        
        # Cache links and parent frame data
        incoming = [l for l in node_tree.links if l.to_node == node]
        outgoing = [l for l in node_tree.links if l.from_node == node]
        parent_frame = node.parent
        loc = node.location.copy()
        
        width = node.dimensions.x
        height = node.dimensions.y
        
        # Fallback dimensions if Blender hasn't fully drawn the node yet
        if width == 0:  width = 140
        if height == 0: height = 100
        
        # 1. Align X to the exact right edge of the node (where output sockets live)
        loc.x += width - 14
        
        # 2. Align Y to the specific output socket being replaced
        if outgoing:
            try:
                outputs_list = list(node.outputs)
                # Sort outgoing links to reliably pick the top-most *connected* output socket
                outgoing.sort(key=lambda l: outputs_list.index(l.from_socket))
                primary_socket = outgoing[0].from_socket
                socket_index = outputs_list.index(primary_socket)
            except ValueError:
                socket_index = 0
            
            if node.hide:
                # If the node is hidden/collapsed, all sockets pack into the vertical center
                loc.y -= 18
            else:
                # Standard Blender node UI metrics calculation:
                # Header height is roughly 34px, each consecutive socket down adds 22px
                loc.y -= (34 + (socket_index * 22))
        else:
            # Fallback if nothing was hooked to outputs: drop it at vertical center
            loc.y -= height / 2
        
        # Determine the primary incoming source socket to bridge from
        src_socket = None
        if incoming:
            try:
                inputs_list = list(node.inputs)
                incoming.sort(key=lambda l: inputs_list.index(l.to_socket))
            except ValueError:
                pass
            src_socket = incoming[0].from_socket
        
        # Collect all destination sockets
        dst_sockets = [l.to_socket for l in outgoing]
        
        # Remove the old node
        node_tree.nodes.remove(node)
        
        # Create the new universal Reroute node
        reroute = node_tree.nodes.new('NodeReroute')
        
        # Maintain frame attachment
        if parent_frame:
            reroute.parent = parent_frame
            
        reroute.location = loc
        
        # Reconnect the lines
        if src_socket:
            node_tree.links.new(src_socket, reroute.inputs[0])
            
        for dst in dst_sockets:
            node_tree.links.new(reroute.outputs[0], dst)
            
        # Keep the new reroute active and selected
        reroute.select = True
        node_tree.nodes.active = reroute
        
        return {'FINISHED'}


###-----------------------------------------------------------------------------###
###                            LINK OPERATORS                                   ###
###-----------------------------------------------------------------------------###

class NODE_OT_cpie_link_active_replace_parent(bpy.types.Operator):
    """Link active node to selected nodes, replacing links that come from the active node's closest upstream ancestor"""
    bl_idname = "node.cpie_link_active_replace_parent"
    bl_label = "Intercept Parent Link"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR'
                and space.node_tree is not None
                and context.active_node is not None
                and len(context.selected_nodes) > 1)

    def execute(self, context):
        tree = context.space_data.node_tree
        links = tree.links
        active_node = context.active_node
        other_selected = [n for n in context.selected_nodes if n != active_node]

        if not other_selected:
            return {'CANCELLED'}

        # Step 1: Trace upstream ancestry of the active node using BFS to map distances
        ancestry = {}  # node -> distance hierarchy steps
        queue = [(active_node, 0)]
        visited = {active_node}

        while queue:
            curr_node, dist = queue.pop(0)
            for inp in curr_node.inputs:
                if inp.is_linked and inp.enabled and not inp.hide:
                    for link in inp.links:
                        from_node = link.from_node
                        if from_node not in visited:
                            visited.add(from_node)
                            ancestry[from_node] = dist + 1
                            queue.append((from_node, dist + 1))

        # Helper to find a type-compatible output from active_node
        def find_compatible_output(target_input):
            for out in active_node.outputs:
                if out.enabled and not out.hide and out.type == target_input.type:
                    return out
            for out in active_node.outputs:
                if out.enabled and not out.hide:
                    return out
            return None

        # Step 2: Analyze and re-link selected nodes
        for s in other_selected:
            replaced = False
            candidate_links = []

            # Find inputs connected to any upstream ancestor of the active node
            for inp in s.inputs:
                if inp.is_linked and inp.enabled and not inp.hide:
                    for link in inp.links:
                        if link.from_node in ancestry:
                            candidate_links.append((link, inp, ancestry[link.from_node]))

            if candidate_links:
                # Sort by closest parent ancestor (shortest step distance)
                candidate_links.sort(key=lambda item: item[2])

                # Intercept the closest parent's link
                link_to_replace, target_input, _ = candidate_links[0]
                out_socket = find_compatible_output(target_input)

                if out_socket:
                    links.remove(link_to_replace)
                    links.new(out_socket, target_input)
                    replaced = True

            # Fallback: If no common parent chain exists, link active directly to an available input
            if not replaced:
                target_input = None
                first_out = next((out for out in active_node.outputs if out.enabled and not out.hide), None)
                if first_out:
                    for inp in s.inputs:
                        if inp.enabled and not inp.hide and not inp.is_linked and inp.type == first_out.type:
                            target_input = inp
                            break
                    if not target_input:
                        for inp in s.inputs:
                            if inp.enabled and not inp.hide and not inp.is_linked:
                                target_input = inp
                                break
                    if not target_input and s.inputs:
                        target_input = next((inp for inp in s.inputs if inp.enabled and not inp.hide), None)

                    if target_input:
                        out_socket = find_compatible_output(target_input)
                        if out_socket:
                            links.new(out_socket, target_input)

        return {'FINISHED'}


# ==============================================================================
# ADD CONNECT — spawn a node from the add pies and wire the active node into it
# ==============================================================================

def _best_connect(source, new_node, links):
    """Link the active node's most reasonable output into the new node's matching input.

    Prefers an exact socket-type match (favouring the new node's first/primary input),
    then an implicitly-convertible match, then falls back to first-output -> first-input.
    Returns True if a link was made.
    """
    def _norm(s):
        return 'VALUE' if s.type == 'INT' else s.type

    src_outs = [o for o in source.outputs
                if not o.hide and o.enabled and o.bl_idname != 'NodeSocketVirtual']
    dst_ins = [i for i in new_node.inputs
               if not i.hide and i.enabled and i.bl_idname != 'NodeSocketVirtual']
    if not src_outs or not dst_ins:
        return False

    # Tier 1: exact type match, prioritising the new node's primary (top-most) inputs.
    for inp in dst_ins:
        for out in src_outs:
            if _norm(out) == _norm(inp):
                links.new(out, inp)
                return True

    # Tier 2: implicitly-convertible match (skip geometry/shader, which never convert).
    for inp in dst_ins:
        if _norm(inp) in _NONCONVERTIBLE:
            continue
        for out in src_outs:
            if _norm(out) in _NONCONVERTIBLE:
                continue
            links.new(out, inp)
            return True

    # Tier 3: blind fallback — primary output into primary input.
    links.new(src_outs[0], dst_ins[0])
    return True


class NODE_OT_cpie_add_connect(bpy.types.Operator):
    """Add a node and wire the active node's most reasonable output into it"""
    bl_idname = "node.cpie_add_connect"
    bl_label = "Add & Connect Node"
    bl_options = {'REGISTER', 'UNDO'}

    node_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR'
                and space.node_tree is not None
                and (context.active_node is not None or len(context.selected_nodes) > 0))

    def execute(self, context):
        tree = context.space_data.node_tree
        source = context.active_node
        if source is None:
            sel = context.selected_nodes
            source = sel[0] if sel else None
        if source is None or not self.node_type:
            return {'CANCELLED'}

        try:
            new_node = tree.nodes.new(type=self.node_type)
        except Exception:
            self.report({'WARNING'}, "Could not add node of type %s" % self.node_type)
            return {'CANCELLED'}

        # Maintain frame attachment if the source node is inside a frame
        if source.parent:
            new_node.parent = source.parent

        # Drop the new node just to the right of the source, vertically aligned.
        new_node.location = (source.location.x + source.width + 50, source.location.y)
        _best_connect(source, new_node, tree.links)

        for n in context.selected_nodes:
            n.select = False
        new_node.select = True
        tree.nodes.active = new_node
        return {'FINISHED'}


class NODE_OT_cpie_add_connect_start(bpy.types.Operator):
    """Open the add-node pie; the chosen node will be wired to the active node"""
    bl_idname = "node.cpie_add_connect_start"
    bl_label = "Add Connect"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR'
                and space.node_tree is not None
                and (context.active_node is not None or len(context.selected_nodes) > 0))

    def execute(self, context):
        global _ADD_CONNECT_MODE
        _ADD_CONNECT_MODE = True
        bpy.ops.wm.call_menu_pie(name="SUBPIE_MT_add_connect")
        return {'FINISHED'}


# ==============================================================================
# MAGIC MERGE — auto-detect output socket types and route to a typed sub-pie
# ==============================================================================

# Enum-item caches, populated lazily from node bl_rna so they don't drift.
# Module-level lists keep string refs alive across the EnumProperty callback.
_BOOL_OPS_CACHE = []
_MATH_OPS_CACHE = []
_VEC_MATH_OPS_CACHE = []
_MIX_BLEND_CACHE = []
_GEO_OPS_CACHE = [
    ('JOIN',       "Join Geometry", "Join all selected geometry into one stream"),
    ('UNION',      "Union",         "Mesh Boolean union of selected meshes"),
    ('DIFFERENCE', "Difference",    "Mesh Boolean difference (first minus rest)"),
    ('INTERSECT',  "Intersect",     "Mesh Boolean intersection of selected meshes"),
]

# Socket types Magic Merge can route. Each maps to its specific merge sub-pie plus a
# label/icon for the chooser button. _MERGE_DISPLAY_ORDER also fixes the chooser order.
_MERGE_ROUTING = {
    'GEOMETRY': ("SUBPIE_MT_merge_geometry", "Geometry", 'MESH_DATA'),
    'SHADER':   ("SUBPIE_MT_merge_shader",   "Shader",   'SHADING_RENDERED'),
    'RGBA':     ("SUBPIE_MT_merge_color",    "Color",    'COLOR'),
    'VECTOR':   ("SUBPIE_MT_merge_vector",   "Vector",   'ORIENTATION_GLOBAL'),
    'VALUE':    ("SUBPIE_MT_merge_float",    "Math",     'CON_KINEMATIC'),
    'BOOLEAN':  ("SUBPIE_MT_merge_boolean",  "Boolean",  'CON_KINEMATIC'),
}
_MERGE_DISPLAY_ORDER = list(_MERGE_ROUTING.keys())

# Which merge socket types make sense per editor, since not every type has a merge node
# in every tree (no geometry/boolean in shader, no shader/vector in the compositor, …).
_SUPPORTED_MERGE_TYPES = {
    'GeometryNodeTree':   {'GEOMETRY', 'RGBA', 'VECTOR', 'VALUE', 'BOOLEAN'},
    'ShaderNodeTree':     {'SHADER', 'RGBA', 'VECTOR', 'VALUE'},
    'CompositorNodeTree': {'RGBA', 'VALUE'},
}

# Node spawned for a numeric/colour merge, per editor. GEOMETRY/SHADER/BOOLEAN are
# single-editor and handled directly by their own operators.
_MERGE_NODE = {
    'VALUE':  {'GeometryNodeTree': 'ShaderNodeMath',
               'ShaderNodeTree':   'ShaderNodeMath',
               'CompositorNodeTree': 'CompositorNodeMath'},
    'VECTOR': {'GeometryNodeTree': 'ShaderNodeVectorMath',
               'ShaderNodeTree':   'ShaderNodeVectorMath'},
    'RGBA':   {'GeometryNodeTree': 'ShaderNodeMix',
               'ShaderNodeTree':   'ShaderNodeMix',
               'CompositorNodeTree': 'CompositorNodeMixRGB'},
}

# Types that don't implicitly convert: a geometry/shader merge only ever accepts a
# geometry/shader socket, never an incidental Value/Material/etc.
_NONCONVERTIBLE = {'GEOMETRY', 'SHADER'}


def _spawn_merge_node(context, merge_type):
    """Create the numeric/colour merge node appropriate to the current editor, or None
    if that merge type has no node in this tree."""
    tree = context.space_data.node_tree
    bl_idname = _MERGE_NODE.get(merge_type, {}).get(context.space_data.tree_type)
    if not bl_idname:
        return None
    try:
        return tree.nodes.new(type=bl_idname)
    except Exception:
        return None


def _available_merge_types(selected, tree_type):
    """The mergeable socket types Magic Merge can offer for the current selection,
    restricted to what the editor supports and ordered for display. Returns a list of
    type strings (e.g. ['GEOMETRY', 'BOOLEAN']).

    Rules:
      * A node exposing exactly ONE mergeable type can only be merged that way, so such
        "locked" types are mandatory — when present, they define the whole offering.
        (A geometry-only node thus forces a geometry merge.)
      * Otherwise offer the types shared by every node (intersection), so two nodes that
        both expose Geometry and Boolean give a two-option pie.
      * If the nodes share nothing, fall back to every type present (union), letting the
        user pick which to combine on.
    """
    supported = _SUPPORTED_MERGE_TYPES.get(tree_type, set())
    node_sets = []
    for n in selected:
        s = set()
        for out in n.outputs:
            if out.hide or not out.enabled or out.bl_idname == 'NodeSocketVirtual':
                continue
            if any(link.to_node in selected for link in out.links):
                continue
            t = 'VALUE' if out.type == 'INT' else out.type
            if t in supported:
                s.add(t)
        if s:
            node_sets.append(s)

    if not node_sets:
        return []

    locked = {next(iter(s)) for s in node_sets if len(s) == 1}
    chosen = locked or set.intersection(*node_sets) or set.union(*node_sets)
    return [t for t in _MERGE_DISPLAY_ORDER if t in chosen]


def _terminal_outputs(selected):
    """The selected nodes' outputs that don't feed back into the selection, i.e. the
    sockets a merge/combine should consume. Order follows `selected`."""
    sockets = []
    for node in selected:
        for out in node.outputs:
            if out.hide or not out.enabled:
                continue
            if any(link.to_node in selected for link in out.links):
                continue
            sockets.append(out)
    return sockets


def _terminal_scalar_count(selected):
    """How many terminal outputs are scalar (Value/Int) — the count of channels a
    Combine XYZ / Combine Color node could pack from this selection."""
    return sum(1 for s in _terminal_outputs(selected) if s.type in ('VALUE', 'INT'))


def _pull_enum(node_cls_name, prop_name):
    cls = getattr(bpy.types, node_cls_name, None)
    if cls is None:
        return []
    prop = cls.bl_rna.properties.get(prop_name)
    if prop is None:
        return []
    return [(it.identifier, it.name, it.description or "") for it in prop.enum_items]


def _bool_op_items(self, context):
    if not _BOOL_OPS_CACHE:
        _BOOL_OPS_CACHE.extend(_pull_enum('FunctionNodeBooleanMath', 'operation')
                               or [('AND', "And", "")])
    return _BOOL_OPS_CACHE


def _math_op_items(self, context):
    if not _MATH_OPS_CACHE:
        _MATH_OPS_CACHE.extend(_pull_enum('ShaderNodeMath', 'operation')
                               or [('ADD', "Add", "")])
    return _MATH_OPS_CACHE


def _vec_math_op_items(self, context):
    if not _VEC_MATH_OPS_CACHE:
        _VEC_MATH_OPS_CACHE.extend(_pull_enum('ShaderNodeVectorMath', 'operation')
                                   or [('ADD', "Add", "")])
    return _VEC_MATH_OPS_CACHE


def _mix_blend_items(self, context):
    if not _MIX_BLEND_CACHE:
        _MIX_BLEND_CACHE.extend(_pull_enum('ShaderNodeMix', 'blend_type')
                                or [('MIX', "Mix", "")])
    return _MIX_BLEND_CACHE


def _geo_op_items(self, context):
    return _GEO_OPS_CACHE


def _merge_poll(context):
    space = context.space_data
    return (space.type == 'NODE_EDITOR'
            and space.node_tree is not None
            and len(context.selected_nodes) > 0)


def _gather_merge_outputs(selected, preferred_type=None):
    """Pick one output socket per selected node to feed into the merge node, top-to-bottom.
    
    Uses a strict 5-tier priority hierarchy to ensure exact type matches are always
    preferred over implicit type conversions or blind fallbacks.
    """
    def _norm(out):
        return 'VALUE' if out.type == 'INT' else out.type

    outs = []
    for n in sorted(selected, key=lambda n: -n.location.y):
        usable = [o for o in n.outputs
                  if not o.hide and o.enabled and o.bl_idname != 'NodeSocketVirtual']
        if not usable:
            continue
        
        terminal = [o for o in usable
                    if not any(link.to_node in selected for link in o.links)]

        if preferred_type:
            # Tier 1: Exact type match in completely unlinked (terminal) sockets
            exact_terminal = next((o for o in terminal if _norm(o) == preferred_type), None)
            if exact_terminal:
                outs.append(exact_terminal)
                continue

            # Tier 2: Exact type match in any usable sockets (even if internally linked)
            exact_usable = next((o for o in usable if _norm(o) == preferred_type), None)
            if exact_usable:
                outs.append(exact_usable)
                continue

            # Tier 3: Implicitly convertible match in unlinked (terminal) sockets
            if preferred_type not in _NONCONVERTIBLE:
                conv_terminal = next((o for o in terminal if _norm(o) not in _NONCONVERTIBLE), None)
                if conv_terminal:
                    outs.append(conv_terminal)
                    continue

                # Tier 4: Implicitly convertible match in any usable sockets
                conv_usable = next((o for o in usable if _norm(o) not in _NONCONVERTIBLE), None)
                if conv_usable:
                    outs.append(conv_usable)
                    continue
        
        # Tier 5: Absolute fallback (grab the top-most valid socket left)
        if terminal:
            outs.append(terminal[0])
        else:
            outs.append(usable[0])
            
    return outs


def _position_and_wire(context, new_node):
    """Place new_node right of selection and link type-matched terminal outputs into its inputs."""
    tree = context.space_data.node_tree
    links = tree.links
    selected = [n for n in context.selected_nodes if n != new_node]
    if not selected:
        return

    # Maintain frame attachment if nodes are inside a frame
    active_node = context.active_node
    parent_frame = active_node.parent if (active_node in selected) else selected[0].parent
    if parent_frame:
        new_node.parent = parent_frame

    avg_y = sum(n.location.y for n in selected) / len(selected)
    max_x = max(n.location.x + n.width for n in selected)
    new_node.location = (max_x + 50, avg_y)

    # Automatically deduce the expected type for the target node to guide socket selection
    ntype = new_node.bl_idname
    preferred_type = None
    if ntype == 'FunctionNodeBooleanMath':
        preferred_type = 'BOOLEAN'
    elif ntype in ('ShaderNodeMath', 'CompositorNodeMath'):
        preferred_type = 'VALUE'
    elif ntype == 'ShaderNodeVectorMath':
        preferred_type = 'VECTOR'
    elif ntype == 'ShaderNodeMix':
        d_type = getattr(new_node, 'data_type', 'RGBA')
        preferred_type = d_type if d_type in ('RGBA', 'VECTOR') else 'VALUE'
    elif ntype == 'CompositorNodeMixRGB':
        preferred_type = 'RGBA'
    elif ntype in ('GeometryNodeJoinGeometry', 'GeometryNodeMeshBoolean'):
        preferred_type = 'GEOMETRY'
    elif ntype in ('ShaderNodeMixShader', 'ShaderNodeAddShader'):
        preferred_type = 'SHADER'

    def _input_eligible(inp):
        # Geometry/shader inputs must match the merge type exactly; the Mix/Add Shader
        # Factor input (a Float) is thus skipped instead of swallowing a shader output.
        if preferred_type in _NONCONVERTIBLE:
            return ('VALUE' if inp.type == 'INT' else inp.type) == preferred_type
        return True

    merge_outs = _gather_merge_outputs(selected, preferred_type=preferred_type)

    multi_in = next(
        (inp for inp in new_node.inputs
         if not inp.hide and inp.enabled and getattr(inp, 'is_multi_input', False)),
        None,
    )

    out_iter = iter(merge_outs)
    if multi_in is not None:
        for inp in new_node.inputs:
            if inp.hide or not inp.enabled or inp == multi_in:
                if inp == multi_in:
                    break
                continue
            if not _input_eligible(inp):
                continue
            try:
                out = next(out_iter)
            except StopIteration:
                break
            try: links.new(out, inp)
            except Exception: pass
        for out in out_iter:
            try: links.new(out, multi_in)
            except Exception: pass
    else:
        for inp in new_node.inputs:
            if inp.hide or not inp.enabled:
                continue
            if not _input_eligible(inp):
                continue
            try:
                out = next(out_iter)
            except StopIteration:
                break
            try: links.new(out, inp)
            except Exception: pass

    for n in selected:
        n.select = False
    new_node.select = True
    tree.nodes.active = new_node

class NODE_OT_cpie_merge_boolean(bpy.types.Operator):
    """Spawn a Boolean Math node with the chosen operation and wire selected nodes into it"""
    bl_idname = "node.cpie_merge_boolean"
    bl_label = "Merge: Boolean Math"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(name="Operation", items=_bool_op_items)

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        tree = context.space_data.node_tree
        new_node = tree.nodes.new(type='FunctionNodeBooleanMath')
        try: new_node.operation = self.operation
        except Exception: pass
        _position_and_wire(context, new_node)
        return {'FINISHED'}


class NODE_OT_cpie_merge_float(bpy.types.Operator):
    """Spawn a Math node with the chosen operation and wire selected nodes into it"""
    bl_idname = "node.cpie_merge_float"
    bl_label = "Merge: Math"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(name="Operation", items=_math_op_items)

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        new_node = _spawn_merge_node(context, 'VALUE')
        if new_node is None:
            self.report({'WARNING'}, "Math merge not available in this editor")
            return {'CANCELLED'}
        try: new_node.operation = self.operation
        except Exception: pass
        _position_and_wire(context, new_node)
        return {'FINISHED'}


class NODE_OT_cpie_merge_vector(bpy.types.Operator):
    """Spawn a Vector Math node with the chosen operation and wire selected nodes into it"""
    bl_idname = "node.cpie_merge_vector"
    bl_label = "Merge: Vector Math"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(name="Operation", items=_vec_math_op_items)

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        new_node = _spawn_merge_node(context, 'VECTOR')
        if new_node is None:
            self.report({'WARNING'}, "Vector Math merge not available in this editor")
            return {'CANCELLED'}
        try: new_node.operation = self.operation
        except Exception: pass
        _position_and_wire(context, new_node)
        return {'FINISHED'}


class NODE_OT_cpie_merge_color(bpy.types.Operator):
    """Spawn a Mix (Color) node with the chosen blend type and wire selected nodes into it"""
    bl_idname = "node.cpie_merge_color"
    bl_label = "Merge: Mix Color"
    bl_options = {'REGISTER', 'UNDO'}

    blend_type: bpy.props.EnumProperty(name="Blend", items=_mix_blend_items)

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        new_node = _spawn_merge_node(context, 'RGBA')
        if new_node is None:
            self.report({'WARNING'}, "Color merge not available in this editor")
            return {'CANCELLED'}
        # ShaderNodeMix is multi-purpose; the compositor's CompositorNodeMixRGB is not.
        if new_node.bl_idname == 'ShaderNodeMix':
            try: new_node.data_type = 'RGBA'
            except Exception: pass
        try: new_node.blend_type = self.blend_type
        except Exception: pass
        _position_and_wire(context, new_node)
        return {'FINISHED'}


class NODE_OT_cpie_merge_shader(bpy.types.Operator):
    """Spawn a Mix or Add Shader node and wire selected shader outputs into it"""
    bl_idname = "node.cpie_merge_shader"
    bl_label = "Merge: Shader"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(
        name="Operation",
        items=[('MIX', "Mix Shader", "Blend the shaders with a Mix Shader node"),
               ('ADD', "Add Shader", "Sum the shaders with an Add Shader node")],
    )

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        tree = context.space_data.node_tree
        bl_idname = 'ShaderNodeAddShader' if self.operation == 'ADD' else 'ShaderNodeMixShader'
        try:
            new_node = tree.nodes.new(type=bl_idname)
        except Exception:
            self.report({'WARNING'}, "Shader merge not available in this editor")
            return {'CANCELLED'}
        _position_and_wire(context, new_node)
        return {'FINISHED'}


class NODE_OT_cpie_merge_geometry(bpy.types.Operator):
    """Spawn a Join Geometry or Mesh Boolean node and wire selected nodes into it"""
    bl_idname = "node.cpie_merge_geometry"
    bl_label = "Merge: Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(name="Operation", items=_geo_op_items)

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        tree = context.space_data.node_tree
        if self.operation == 'JOIN':
            new_node = tree.nodes.new(type='GeometryNodeJoinGeometry')
        else:
            new_node = tree.nodes.new(type='GeometryNodeMeshBoolean')
            try: new_node.operation = self.operation
            except Exception: pass
        _position_and_wire(context, new_node)
        return {'FINISHED'}


class NODE_OT_cpie_magic_merge(bpy.types.Operator):
    """Detect the mergeable output types of selected nodes. Opens a chooser pie when
    more than one option is available (multiple merge types, or a Combine XYZ/Color
    alternative), or goes straight to the merge pie when only one is"""
    bl_idname = "node.cpie_magic_merge"
    bl_label = "Magic Merge"

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        selected = context.selected_nodes
        tree_type = context.space_data.tree_type
        types = _available_merge_types(selected, tree_type)
        if not types:
            self.report({'WARNING'}, "No mergeable outputs in the selection")
            return {'CANCELLED'}

        # 2+ scalar outputs in an editor with Combine nodes means the chooser has a
        # Combine XYZ/Color option to offer beyond the plain same-type merge.
        can_combine = (_terminal_scalar_count(selected) >= 2
                       and tree_type in ('GeometryNodeTree', 'ShaderNodeTree', 'CompositorNodeTree'))

        # A single mergeable type with no combine alternative -> jump straight to its
        # enumerate pie; otherwise let the user pick (merge type or Combine) in the chooser.
        if len(types) == 1 and not can_combine:
            bpy.ops.wm.call_menu_pie(name=_MERGE_ROUTING[types[0]][0])
        else:
            bpy.ops.wm.call_menu_pie(name="SUBPIE_MT_merge_chooser")
        return {'FINISHED'}


class SUBPIE_MT_merge_chooser(Menu):
    bl_label = "Merge Type"
    def draw(self, context):
        pie = self.layout.menu_pie()
        selected = context.selected_nodes
        tree_type = context.space_data.tree_type
        # Recomputed from the live selection so the slots always match what's mergeable.
        for t in _available_merge_types(selected, tree_type):
            pie_name, label, icon = _MERGE_ROUTING[t]
            pie.operator("wm.call_menu_pie", text=label, icon=icon).name = pie_name

        # With two or more terminal scalar outputs, also offer packing them into a
        # Combine XYZ / Combine Color node instead of a same-type merge.
        if _terminal_scalar_count(selected) >= 2:
            if tree_type in ('GeometryNodeTree', 'ShaderNodeTree'):
                pie.operator("node.cpie_combine_selected", text="Combine XYZ",
                             icon='ORIENTATION_GLOBAL').combine_type = 'XYZ'
            if tree_type in ('GeometryNodeTree', 'ShaderNodeTree', 'CompositorNodeTree'):
                pie.operator("node.cpie_combine_selected", text="Combine Color",
                             icon='COLOR').combine_type = 'COLOR'


class SUBPIE_MT_merge_boolean(Menu):
    bl_label = "Merge: Boolean Math"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_merge_boolean", "operation")


class SUBPIE_MT_merge_float(Menu):
    bl_label = "Merge: Math"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_merge_float", "operation")


class SUBPIE_MT_merge_vector(Menu):
    bl_label = "Merge: Vector Math"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_merge_vector", "operation")


class SUBPIE_MT_merge_color(Menu):
    bl_label = "Merge: Mix Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_merge_color", "blend_type")


class SUBPIE_MT_merge_shader(Menu):
    bl_label = "Merge: Shader"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_merge_shader", "operation")


class SUBPIE_MT_merge_geometry(Menu):
    bl_label = "Merge: Geometry"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.cpie_merge_geometry", "operation")


# ==============================================================================
# 1. GEOMETRY NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_gn_mesh(Menu):
    bl_label = "Mesh Nodes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Cube", 'GeometryNodeMeshCube', 'MESH_CUBE')
        _add_node_op(pie, "Circle", 'GeometryNodeMeshCircle', 'MESH_CIRCLE')
        _add_node_op(pie, "Cylinder", 'GeometryNodeMeshCylinder', 'MESH_CYLINDER')
        _add_node_op(pie, "UV Sphere", 'GeometryNodeMeshUVSphere', 'MESH_UVSPHERE')
        _add_node_op(pie, "Extrude Mesh", 'GeometryNodeExtrudeMesh', 'MESH_DATA')
        _add_node_op(pie, "Subdivide Mesh", 'GeometryNodeSubdivideMesh', 'MESH_DATA')
        _add_node_op(pie, "Flip Faces", 'GeometryNodeFlipFaces', 'MESH_DATA')
        _add_node_op(pie, "Mesh to Curve", 'GeometryNodeMeshToCurve', 'CURVE_DATA')

class SUBPIE_MT_gn_curve(Menu):
    bl_label = "Curve Nodes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Bezier Segment", 'GeometryNodeCurvePrimitiveBezierSegment', 'CURVE_BEZCURVE')
        _add_node_op(pie, "Curve Circle", 'GeometryNodeCurvePrimitiveCircle', 'CURVE_BEZCIRCLE')
        _add_node_op(pie, "Curve Line", 'GeometryNodeCurvePrimitiveLine', 'CURVE_PATH')
        _add_node_op(pie, "Resample Curve", 'GeometryNodeResampleCurve', 'CURVE_DATA')
        _add_node_op(pie, "Trim Curve", 'GeometryNodeTrimCurve', 'CURVE_DATA')
        _add_node_op(pie, "Fill Curve", 'GeometryNodeFillCurve', 'MESH_DATA')
        _add_node_op(pie, "Curve to Mesh", 'GeometryNodeCurveToMesh', 'MESH_DATA')
        _add_node_op(pie, "Curve to Points", 'GeometryNodeCurveToPoints', 'PARTICLE_DATA')

class SUBPIE_MT_gn_utilities(Menu):
    bl_label = "Utilities & Math"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Math", 'ShaderNodeMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Vector Math", 'ShaderNodeVectorMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Boolean Math", 'FunctionNodeBooleanMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Random Value", 'FunctionNodeRandomValue', 'RNDCURVE')
        _add_node_op(pie, "Color Ramp", 'ShaderNodeValToRGB', 'COLOR')
        _add_node_op(pie, "Float Curve", 'ShaderNodeFloatCurve', 'CURVE_DATA')
        _add_node_op(pie, "Switch", 'GeometryNodeSwitch', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Map Range", 'ShaderNodeMapRange', 'ARROW_LEFTRIGHT')

class SUBPIE_MT_gn_io(Menu):
    bl_label = "Input & Output"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # 1. WEST - Object Data
        _add_node_op(pie, "Object Info", 'GeometryNodeObjectInfo', 'OBJECT_DATA')
        # 2. EAST - Scene Data
        _add_node_op(pie, "Scene Time", 'GeometryNodeInputSceneTime', 'TIME')
        # 3. SOUTH - Basic Constant
        _add_node_op(pie, "Value", 'ShaderNodeValue', 'PROPERTIES')
        # 4. NORTH - Material Constant
        _add_node_op(pie, "Material", 'GeometryNodeInputMaterial', 'MATERIAL')
        # 5. NORTH-WEST - Collection Constant
        _add_node_op(pie, "Collection Info", 'GeometryNodeCollectionInfo', 'OUTLINER_COLLECTION')
        # 6. NORTH-EAST - Self Reference
        _add_node_op(pie, "Self Object", 'GeometryNodeSelfObject', 'NODE_SEL')
        # 7. SOUTH-WEST - Integer Constant
        _add_node_op(pie, "Integer", 'FunctionNodeInputInt', 'LINENUMBERS_ON')
        # 8. SOUTH-EAST - Boolean Constant
        _add_node_op(pie, "Boolean", 'FunctionNodeInputBool', 'CHECKBOX_HLT')

class SUBPIE_MT_gn_geometry_points(Menu):
    bl_label = "Geometry & Points"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Transform", 'GeometryNodeTransform', 'ORIENTATION_GLOBAL')
        _add_node_op(pie, "Set Position", 'GeometryNodeSetPosition', 'SNAP_GRID')
        _add_node_op(pie, "Join Geometry", 'GeometryNodeJoinGeometry')
        _add_node_op(pie, "Instance on Points", 'GeometryNodeInstanceOnPoints', 'PARTICLE_DATA')
        _add_node_op(pie, "Realize Instances", 'GeometryNodeRealizeInstances', 'OUTLINER_OB_GROUP_INSTANCE')
        _add_node_op(pie, "Separate Geometry", 'GeometryNodeSeparateGeometry', 'MESH_DATA')
        _add_node_op(pie, "Delete Geometry", 'GeometryNodeDeleteGeometry', 'CANCEL')
        _add_node_op(pie, "Distribute Points on Faces", 'GeometryNodeDistributePointsOnFaces', 'PARTICLE_DATA')

class SUBPIE_MT_gn_attributes(Menu):
    bl_label = "Attributes & Textures"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Named Attribute", 'GeometryNodeInputNamedAttribute', 'SPREADSHEET')
        _add_node_op(pie, "Store Named Attribute", 'GeometryNodeStoreNamedAttribute', 'SPREADSHEET')
        _add_node_op(pie, "Capture Attribute", 'GeometryNodeCaptureAttribute', 'SPREADSHEET')
        _add_node_op(pie, "Noise Texture", 'ShaderNodeTexNoise', 'TEXTURE')
        _add_node_op(pie, "Voronoi Texture", 'ShaderNodeTexVoronoi', 'TEXTURE')
        _add_node_op(pie, "Gradient Texture", 'ShaderNodeTexGradient', 'TEXTURE')
        _add_node_op(pie, "Blur Attribute", 'GeometryNodeBlurAttribute', 'MOD_SMOOTH')
        _add_node_op(pie, "Sample Index", 'GeometryNodeSampleIndex', 'SPREADSHEET')

class SUBPIE_MT_gn_converter(Menu):
    bl_label = "Converter"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # WEST
        _add_node_op(pie, "Mesh to Volume", 'GeometryNodeMeshToVolume', 'VOLUME_DATA')
        # EAST
        _add_node_op(pie, "Volume to Mesh", 'GeometryNodeVolumeToMesh', 'MESH_DATA')
        # SOUTH
        _add_node_op(pie, "Mesh to Points", 'GeometryNodeMeshToPoints', 'PARTICLE_DATA')
        # NORTH
        _add_node_op(pie, "Mesh to Curve", 'GeometryNodeMeshToCurve', 'CURVE_DATA')
        # NORTH-WEST
        _add_node_op(pie, "Curve to Mesh", 'GeometryNodeCurveToMesh', 'MESH_DATA')
        # NORTH-EAST
        _add_node_op(pie, "Curve to Points", 'GeometryNodeCurveToPoints', 'PARTICLE_DATA')
        # SOUTH-WEST
        _add_node_op(pie, "Points to Vertices", 'GeometryNodePointsToVertices', 'VERTEXSEL')
        # SOUTH-EAST
        _add_node_op(pie, "Points to Volume", 'GeometryNodePointsToVolume', 'VOLUME_DATA')

class SUBPIE_MT_gn_materials(Menu):
    bl_label = "Materials & UV"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Set Material", 'GeometryNodeSetMaterial', 'MATERIAL')
        _add_node_op(pie, "Replace Material", 'GeometryNodeReplaceMaterial', 'MATERIAL')
        _add_node_op(pie, "Material Selection", 'GeometryNodeMaterialSelection', 'MATERIAL')
        _add_node_op(pie, "Set Material Index", 'GeometryNodeSetMaterialIndex', 'MATERIAL')
        _add_node_op(pie, "Input Material", 'GeometryNodeInputMaterial', 'MATERIAL')
        _add_node_op(pie, "Set Shade Smooth", 'GeometryNodeSetShadeSmooth', 'SHADING_RENDERED')
        _add_node_op(pie, "UV Unwrap", 'GeometryNodeUVUnwrap', 'UV')
        _add_node_op(pie, "UV Pack Islands", 'GeometryNodeUVPackIslands', 'UV')


# ==============================================================================
# 2. SHADER NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_sh_input(Menu):
    bl_label = "Input"
    def draw(self, context):
        pie = self.layout.menu_pie()

        # 1. WEST
        _add_node_op(pie, "Color", 'ShaderNodeRGB', 'COLOR')
        # 2. EAST
        _add_node_op(pie, "Value", 'ShaderNodeValue', 'PROPERTIES')
        # 3. SOUTH
        _add_node_op(pie, "Attribute", 'ShaderNodeAttribute', 'SPREADSHEET')
        # 4. NORTH
        _add_node_op(pie, "Object Info", 'ShaderNodeObjectInfo', 'OBJECT_DATA')
        # 5. NORTH-WEST
        _add_node_op(pie, "Geometry", 'ShaderNodeNewGeometry', 'MESH_DATA')
        # 6. NORTH-EAST
        _add_node_op(pie, "UV Map", 'ShaderNodeUVMap', 'UV')
        # 7. SOUTH-WEST
        _add_node_op(pie, "Camera Data", 'ShaderNodeCameraData', 'CAMERA_DATA')
        # 8. SOUTH-EAST
        _add_node_op(pie, "Ambient Occlusion", 'ShaderNodeAmbientOcclusion', 'NODE_SEL')

class SUBPIE_MT_sh_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Material Output", 'ShaderNodeOutputMaterial', 'MATERIAL')
        _add_node_op(pie, "Light Output", 'ShaderNodeOutputLight', 'LIGHT')
        _add_node_op(pie, "World Output", 'ShaderNodeOutputWorld', 'WORLD')
        _add_node_op(pie, "AOV Output", 'ShaderNodeOutputAOV', 'RENDER_RESULT')
        _add_node_op(pie, "Line Style Output", 'ShaderNodeOutputLineStyle', 'STROKE')
        _add_node_op(pie, "Background", 'ShaderNodeBackground', 'WORLD')
        _add_node_op(pie, "Holdout", 'ShaderNodeHoldout', 'SHADING_WIRE')
        _add_node_op(pie, "Emission", 'ShaderNodeEmission', 'LIGHT')

class SUBPIE_MT_sh_shader(Menu):
    bl_label = "Shader"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Principled BSDF", 'ShaderNodeBsdfPrincipled', 'SHADING_RENDERED')
        _add_node_op(pie, "Emission", 'ShaderNodeEmission', 'LIGHT')
        _add_node_op(pie, "Mix Shader", 'ShaderNodeMixShader', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Transparent BSDF", 'ShaderNodeBsdfTransparent', 'SHADING_WIRE')
        _add_node_op(pie, "Glass BSDF", 'ShaderNodeBsdfGlass', 'SHADING_RENDERED')
        _add_node_op(pie, "Volume Scatter", 'ShaderNodeVolumeScatter', 'VOLUME_DATA')
        _add_node_op(pie, "Glossy BSDF", 'ShaderNodeBsdfGlossy', 'SHADING_RENDERED')
        _add_node_op(pie, "Principled Volume", 'ShaderNodeVolumePrincipled', 'VOLUME_DATA')

class SUBPIE_MT_sh_texture(Menu):
    bl_label = "Texture"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Image Texture", 'ShaderNodeTexImage', 'IMAGE_DATA')
        _add_node_op(pie, "Noise Texture", 'ShaderNodeTexNoise', 'TEXTURE')
        _add_node_op(pie, "Voronoi Texture", 'ShaderNodeTexVoronoi', 'TEXTURE')
        _add_node_op(pie, "Gradient Texture", 'ShaderNodeTexGradient', 'TEXTURE')
        _add_node_op(pie, "Wave Texture", 'ShaderNodeTexWave', 'TEXTURE')
        _add_node_op(pie, "Sky Texture", 'ShaderNodeTexSky', 'LIGHT_SUN')
        _add_node_op(pie, "Checker Texture", 'ShaderNodeTexChecker', 'TEXTURE')
        _add_node_op(pie, "Magic Texture", 'ShaderNodeTexMagic', 'TEXTURE')

class SUBPIE_MT_sh_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Color Ramp", 'ShaderNodeValToRGB', 'COLOR')
        _add_node_op(pie, "Mix Color", 'ShaderNodeMix', 'COLOR')
        _add_node_op(pie, "RGB Curves", 'ShaderNodeRGBCurve', 'CURVE_DATA')
        _add_node_op(pie, "Hue/Saturation", 'ShaderNodeHueSaturation', 'COLOR')
        _add_node_op(pie, "Invert Color", 'ShaderNodeInvert', 'COLOR')
        _add_node_op(pie, "Bright/Contrast", 'ShaderNodeBrightContrast', 'COLORSET_10_VEC')
        _add_node_op(pie, "Gamma", 'ShaderNodeGamma', 'COLOR')
        _add_node_op(pie, "Light Falloff", 'ShaderNodeLightFalloff', 'LIGHT')

class SUBPIE_MT_sh_vector(Menu):
    bl_label = "Vector"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Mapping", 'ShaderNodeMapping', 'ORIENTATION_GLOBAL')
        _add_node_op(pie, "Bump", 'ShaderNodeBump', 'FORCE_TEXTURE')
        _add_node_op(pie, "Displacement", 'ShaderNodeDisplacement', 'FORCE_TEXTURE')
        _add_node_op(pie, "Normal Map", 'ShaderNodeNormalMap', 'NORMALS_FACE')
        _add_node_op(pie, "Vector Math", 'ShaderNodeVectorMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Vector Displacement", 'ShaderNodeVectorDisplacement', 'FORCE_TEXTURE')
        _add_node_op(pie, "Vector Curves", 'ShaderNodeVectorCurve', 'CURVE_DATA')
        _add_node_op(pie, "Vector Transform", 'ShaderNodeVectorTransform', 'ORIENTATION_GLOBAL')

class SUBPIE_MT_sh_value(Menu):
    bl_label = "Value"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Value", 'ShaderNodeValue', 'PROPERTIES')
        _add_node_op(pie, "Math", 'ShaderNodeMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Map Range", 'ShaderNodeMapRange', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Clamp", 'ShaderNodeClamp', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Float Curve", 'ShaderNodeFloatCurve', 'CURVE_DATA')
        _add_node_op(pie, "RGB to BW", 'ShaderNodeRGBToBW', 'COLOR')
        _add_node_op(pie, "Fresnel", 'ShaderNodeFresnel', 'NODE_SEL')
        _add_node_op(pie, "Layer Weight", 'ShaderNodeLayerWeight', 'NODE_SEL')

class SUBPIE_MT_sh_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Math", 'ShaderNodeMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Map Range", 'ShaderNodeMapRange', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Separate Color", 'ShaderNodeSeparateColor', 'COLOR')
        _add_node_op(pie, "Combine Color", 'ShaderNodeCombineColor', 'COLOR')
        _add_node_op(pie, "Separate XYZ", 'ShaderNodeSeparateXYZ', 'AXIS_SIDE')
        _add_node_op(pie, "Combine XYZ", 'ShaderNodeCombineXYZ', 'AXIS_SIDE')
        _add_node_op(pie, "Clamp", 'ShaderNodeClamp', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Blackbody", 'ShaderNodeBlackbody', 'LIGHT')


# ==============================================================================
# 3. COMPOSITOR NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_co_input(Menu):
    bl_label = "Input"
    def draw(self, context):
        pie = self.layout.menu_pie()

        # WEST
        _add_node_op(pie, "Image", 'CompositorNodeImage', 'IMAGE_DATA')
        # EAST
        _add_node_op(pie, "Render Layers", 'CompositorNodeRLayers', 'RENDERLAYERS')
        # SOUTH
        _add_node_op(pie, "Value", 'CompositorNodeValue', 'PROPERTIES')
        # NORTH
        _add_node_op(pie, "Time", 'CompositorNodeTime', 'TIME')
        # NORTH-WEST
        _add_node_op(pie, "Movie Clip", 'CompositorNodeMovieClip', 'TRACKER')
        # NORTH-EAST
        _add_node_op(pie, "RGB", 'CompositorNodeRGB', 'COLOR')
        # SOUTH-WEST
        _add_node_op(pie, "Mask", 'CompositorNodeMask', 'MOD_MASK')
        # SOUTH-EAST
        _add_node_op(pie, "Track Position", 'CompositorNodeTrackPos', 'TRACKER')

class SUBPIE_MT_co_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Composite", 'CompositorNodeComposite', 'RENDER_RESULT')
        _add_node_op(pie, "Viewer", 'CompositorNodeViewer', 'HIDE_ON')
        _add_node_op(pie, "File Output", 'CompositorNodeOutputFile', 'FILE_IMAGE')
        _add_node_op(pie, "Split Viewer", 'CompositorNodeSplitViewer', 'HIDE_ON')
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_co_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Mix", 'CompositorNodeMixRGB', 'COLOR')
        _add_node_op(pie, "Alpha Over", 'CompositorNodeAlphaOver', 'IMAGE_ALPHA')
        _add_node_op(pie, "Color Balance", 'CompositorNodeColorBalance', 'COLOR')
        _add_node_op(pie, "Color Ramp", 'CompositorNodeValToRGB', 'COLOR')
        _add_node_op(pie, "Hue Saturation Value", 'CompositorNodeHueSat', 'COLOR')
        _add_node_op(pie, "RGB Curves", 'CompositorNodeCurveRGB', 'CURVE_DATA')
        _add_node_op(pie, "Bright/Contrast", 'CompositorNodeBrightContrast', 'COLORSET_10_VEC')
        _add_node_op(pie, "Gamma", 'CompositorNodeGamma', 'COLOR')

class SUBPIE_MT_co_filter(Menu):
    bl_label = "Filter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Blur", 'CompositorNodeBlur', 'MOD_SMOOTH')
        _add_node_op(pie, "Glare", 'CompositorNodeGlare', 'LIGHT_SUN')
        _add_node_op(pie, "Directional Blur", 'CompositorNodeDBlur', 'MOD_SMOOTH')
        _add_node_op(pie, "Sun Beams", 'CompositorNodeSunBeams', 'LIGHT_SUN')
        _add_node_op(pie, "Pixelate", 'CompositorNodePixelate', 'TEXTURE')
        _add_node_op(pie, "Despeckle", 'CompositorNodeDespeckle', 'MOD_SMOOTH')
        _add_node_op(pie, "Filter", 'CompositorNodeFilter', 'FILTER')
        _add_node_op(pie, "Bokeh Blur", 'CompositorNodeBokehBlur', 'IMAGE_DATA')

class SUBPIE_MT_co_transform(Menu):
    bl_label = "Transform"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Transform", 'CompositorNodeTransform', 'ORIENTATION_GLOBAL')
        _add_node_op(pie, "Translate", 'CompositorNodeTranslate', 'NODE')
        _add_node_op(pie, "Scale", 'CompositorNodeScale', 'NODE')
        _add_node_op(pie, "Rotate", 'CompositorNodeRotate', 'NODE')
        _add_node_op(pie, "Flip", 'CompositorNodeFlip', 'NODE')
        _add_node_op(pie, "Crop", 'CompositorNodeCrop', 'FULLSCREEN_EXIT')
        _add_node_op(pie, "Movie Distortion", 'CompositorNodeMovieDistortion', 'TRACKER')
        _add_node_op(pie, "Corner Pin", 'CompositorNodeCornerPin', 'NODE')

class SUBPIE_MT_co_matte(Menu):
    bl_label = "Matte & Mask"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Cryptomatte", 'CompositorNodeCryptomatteV2', 'RESTRICT_COLOR_OFF')
        _add_node_op(pie, "Keying", 'CompositorNodeKeying', 'IMAGE_ALPHA')
        _add_node_op(pie, "Color Key", 'CompositorNodeColorMatte', 'IMAGE_ALPHA')
        _add_node_op(pie, "Box Mask", 'CompositorNodeBoxMask', 'MOD_MASK')
        _add_node_op(pie, "Ellipse Mask", 'CompositorNodeEllipseMask', 'MOD_MASK')
        _add_node_op(pie, "Luminance Key", 'CompositorNodeLumaMatte', 'IMAGE_ALPHA')
        _add_node_op(pie, "Chroma Key", 'CompositorNodeChromaMatte', 'IMAGE_ALPHA')
        _add_node_op(pie, "Difference Key", 'CompositorNodeDiffMatte', 'IMAGE_ALPHA')

class SUBPIE_MT_co_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Math", 'CompositorNodeMath', 'CON_KINEMATIC')
        _add_node_op(pie, "Set Alpha", 'CompositorNodeSetAlpha', 'IMAGE_ALPHA')
        _add_node_op(pie, "ID Mask", 'CompositorNodeIDMask', 'MOD_MASK')
        _add_node_op(pie, "RGB to BW", 'CompositorNodeRGBToBW', 'COLOR')
        _add_node_op(pie, "Separate Color", 'CompositorNodeSeparateColor', 'COLOR')
        _add_node_op(pie, "Combine Color", 'CompositorNodeCombineColor', 'COLOR')
        _add_node_op(pie, "Alpha Convert", 'CompositorNodePremulKey', 'IMAGE_ALPHA')
        _add_node_op(pie, "Normalize", 'CompositorNodeNormalize', 'NORMALIZE_FCURVES')

class SUBPIE_MT_co_vector(Menu):
    bl_label = "Vector"
    def draw(self, context):
        pie = self.layout.menu_pie()
        _add_node_op(pie, "Map Range", 'CompositorNodeMapRange', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Normalize", 'CompositorNodeNormalize', 'NORMALIZE_FCURVES')
        _add_node_op(pie, "Map Value", 'CompositorNodeMapValue', 'ARROW_LEFTRIGHT')
        _add_node_op(pie, "Normal", 'CompositorNodeNormal', 'NORMALS_FACE')
        _add_node_op(pie, "Vector Curves", 'CompositorNodeCurveVec', 'CURVE_DATA')
        _add_node_op(pie, "Lens Distortion", 'CompositorNodeLensdist', 'DRIVER_DISTANCE')
        _add_node_op(pie, "Defocus", 'CompositorNodeDefocus', 'CAMERA_DATA')
        _add_node_op(pie, "Displace", 'CompositorNodeDisplace', 'MOD_DISPLACE')


# ==============================================================================
# 4. BATCH CHANGE SUB-MENUS (Node Wrangler)
# ==============================================================================

class SUBPIE_MT_nw_batch_blend(Menu):
    bl_label = "Batch: Blend Type"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.nw_batch_change", "blend_type")


class SUBPIE_MT_nw_batch_math(Menu):
    bl_label = "Batch: Math Operation"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_enum("node.nw_batch_change", "operation")


# ==============================================================================
# 5. SHARED UTILITY SUB-MENUS
# ==============================================================================


class SUBPIE_MT_node_delete(Menu):
    bl_label = "Delete"

    def draw(self, context):
        pie = self.layout.menu_pie()
        nw_loaded = "node_wrangler" in context.preferences.addons
        # Opened from SW: cluster at SW/S/W, separators elsewhere.
        # WEST - adjacent to SW
        if nw_loaded:
            pie.operator("node.nw_del_unused", text="Delete Unused", icon='TRASH')
        else:
            pie.separator()
        # EAST
        pie.separator()
        # SOUTH - adjacent to SW
        pie.operator("node.delete", text="Delete", icon='TRASH')
        # NORTH
        pie.separator()
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST - primary
        pie.operator("node.delete_reconnect", text="Delete & Reconnect", icon='X')
        # SOUTH-EAST
        pie.operator("node.delete_add_reroute", text="Delete Add Reroute", icon='LAYER_ACTIVE')


# ==============================================================================
# 6. MULTI-SELECTION SUB-MENUS
# ==============================================================================

class SUBPIE_MT_node_duplicate(Menu):
    bl_label = "Duplicate"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Opened from NW: clump options at NW/W/N/NE, separators at S/SW/SE/E.
        # WEST - adjacent to NW
        pie.operator("node.duplicate_move_keep_inputs", text="Keep Inputs", icon='DUPLICATE')
        # EAST
        pie.separator()
        # SOUTH
        pie.separator()
        # NORTH - adjacent to NW
        pie.operator("node.clipboard_paste", text="Paste", icon='PASTEDOWN')
        # NORTH-WEST - primary, closest to origin
        pie.operator("node.duplicate_move", text="Duplicate", icon='DUPLICATE')
        # NORTH-EAST
        pie.operator("node.clipboard_copy", text="Copy", icon='COPYDOWN')
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


# ==============================================================================
# 7. ADD-NODE CATEGORY CHOOSERS (shared by the no-selection pies and Add Connect)
# ==============================================================================

def _cats_geo(pie):
    # WEST
    pie.operator("wm.call_menu_pie", text="Mesh Nodes...", icon='MESH_DATA').name = "SUBPIE_MT_gn_mesh"
    # EAST
    pie.operator("wm.call_menu_pie", text="Curve Nodes...", icon='CURVE_DATA').name = "SUBPIE_MT_gn_curve"
    # SOUTH - Converter, aligned with Shader/Compositor's South
    pie.operator("wm.call_menu_pie", text="Converter...", icon='CON_KINEMATIC').name = "SUBPIE_MT_gn_converter"
    # NORTH
    pie.operator("wm.call_menu_pie", text="Input & Output...", icon='NODETREE').name = "SUBPIE_MT_gn_io"
    # NORTH-WEST
    pie.operator("wm.call_menu_pie", text="Geometry & Points...", icon='GROUP_VERTEX').name = "SUBPIE_MT_gn_geometry_points"
    # NORTH-EAST
    pie.operator("wm.call_menu_pie", text="Attributes & Textures...", icon='SPREADSHEET').name = "SUBPIE_MT_gn_attributes"
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text="Utilities & Math...", icon='CON_KINEMATIC').name = "SUBPIE_MT_gn_utilities"
    # SOUTH-EAST
    pie.operator("wm.call_menu_pie", text="Materials & UV...", icon='MATERIAL').name = "SUBPIE_MT_gn_materials"


def _cats_shader(pie):
    # WEST
    pie.operator("wm.call_menu_pie", text="Texture...", icon='TEXTURE').name = "SUBPIE_MT_sh_texture"
    # EAST
    pie.operator("wm.call_menu_pie", text="Color...", icon='COLOR').name = "SUBPIE_MT_sh_color"
    # SOUTH
    pie.operator("wm.call_menu_pie", text="Converter...", icon='CON_KINEMATIC').name = "SUBPIE_MT_sh_converter"
    # NORTH
    pie.operator("wm.call_menu_pie", text="Input...", icon='FORWARD').name = "SUBPIE_MT_sh_input"
    # NORTH-WEST
    pie.operator("wm.call_menu_pie", text="Shader...", icon='SHADING_RENDERED').name = "SUBPIE_MT_sh_shader"
    # NORTH-EAST
    pie.operator("wm.call_menu_pie", text="Output...", icon='BACK').name = "SUBPIE_MT_sh_output"
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text="Vector...", icon='ORIENTATION_GLOBAL').name = "SUBPIE_MT_sh_vector"
    # SOUTH-EAST
    pie.operator("wm.call_menu_pie", text="Value...", icon='PROPERTIES').name = "SUBPIE_MT_sh_value"


def _cats_comp(pie):
    # WEST
    pie.operator("wm.call_menu_pie", text="Filter...", icon='MOD_SMOOTH').name = "SUBPIE_MT_co_filter"
    # EAST
    pie.operator("wm.call_menu_pie", text="Color...", icon='COLOR').name = "SUBPIE_MT_co_color"
    # SOUTH
    pie.operator("wm.call_menu_pie", text="Converter...", icon='CON_KINEMATIC').name = "SUBPIE_MT_co_converter"
    # NORTH
    pie.operator("wm.call_menu_pie", text="Input...", icon='FORWARD').name = "SUBPIE_MT_co_input"
    # NORTH-WEST
    pie.operator("wm.call_menu_pie", text="Transform...", icon='ORIENTATION_GLOBAL').name = "SUBPIE_MT_co_transform"
    # NORTH-EAST
    pie.operator("wm.call_menu_pie", text="Output...", icon='BACK').name = "SUBPIE_MT_co_output"
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text="Matte & Mask...", icon='IMAGE_ALPHA').name = "SUBPIE_MT_co_matte"
    # SOUTH-EAST
    pie.operator("wm.call_menu_pie", text="Vector...", icon='ORIENTATION_GLOBAL').name = "SUBPIE_MT_co_vector"


# ------------------------------------------------------------------------------
# Context-aware Add Connect: per-editor maps of "what commonly consumes a socket of
# this type". Keyed by output socket .type (INT folded to VALUE). Tailors the single-
# node Add Connect pie to the active node's outputs; wiring is still done by
# _best_connect, which matches the chosen node's input to the right source output.
# ------------------------------------------------------------------------------

_CONNECT_GEO = {
    'GEOMETRY': [
        ("Set Position", 'GeometryNodeSetPosition', 'SNAP_GRID'),
        ("Transform", 'GeometryNodeTransform', 'ORIENTATION_GLOBAL'),
        ("Join Geometry", 'GeometryNodeJoinGeometry', 'NONE'),
        ("Instance on Points", 'GeometryNodeInstanceOnPoints', 'PARTICLE_DATA'),
        ("Extrude Mesh", 'GeometryNodeExtrudeMesh', 'MESH_DATA'),
        ("Merge by Distance", 'GeometryNodeMergeByDistance', 'AUTOMERGE_ON'),
        ("Realize Instances", 'GeometryNodeRealizeInstances', 'OUTLINER_OB_GROUP_INSTANCE'),
        ("Set Material", 'GeometryNodeSetMaterial', 'MATERIAL'),
    ],
    'VALUE': [
        ("Math", 'ShaderNodeMath', 'CON_KINEMATIC'),
        ("Map Range", 'ShaderNodeMapRange', 'ARROW_LEFTRIGHT'),
        ("Mix", 'ShaderNodeMix', 'COLOR'),
        ("Compare", 'FunctionNodeCompare', 'CON_KINEMATIC'),
        ("Float Curve", 'ShaderNodeFloatCurve', 'CURVE_DATA'),
    ],
    'VECTOR': [
        ("Vector Math", 'ShaderNodeVectorMath', 'CON_KINEMATIC'),
        ("Separate XYZ", 'ShaderNodeSeparateXYZ', 'AXIS_SIDE'),
        ("Set Position", 'GeometryNodeSetPosition', 'SNAP_GRID'),
        ("Transform", 'GeometryNodeTransform', 'ORIENTATION_GLOBAL'),
    ],
    'RGBA': [
        ("Mix Color", 'ShaderNodeMix', 'COLOR'),
        ("Color Ramp", 'ShaderNodeValToRGB', 'COLOR'),
        ("Separate Color", 'FunctionNodeSeparateColor', 'COLOR'),
    ],
    'BOOLEAN': [
        ("Boolean Math", 'FunctionNodeBooleanMath', 'CON_KINEMATIC'),
        ("Switch", 'GeometryNodeSwitch', 'ARROW_LEFTRIGHT'),
        ("Separate Geometry", 'GeometryNodeSeparateGeometry', 'MESH_DATA'),
        ("Delete Geometry", 'GeometryNodeDeleteGeometry', 'CANCEL'),
    ],
    'ROTATION': [
        ("Rotate Instances", 'GeometryNodeRotateInstances', 'DRIVER_ROTATIONAL_DIFFERENCE'),
        ("Rotate Rotation", 'FunctionNodeRotateRotation', 'DRIVER_ROTATIONAL_DIFFERENCE'),
    ],
}

_CONNECT_SHADER = {
    'SHADER': [
        ("Mix Shader", 'ShaderNodeMixShader', 'ARROW_LEFTRIGHT'),
        ("Add Shader", 'ShaderNodeAddShader', 'ADD'),
        ("Material Output", 'ShaderNodeOutputMaterial', 'MATERIAL'),
    ],
    'RGBA': [
        ("Principled BSDF", 'ShaderNodeBsdfPrincipled', 'SHADING_RENDERED'),
        ("Mix Color", 'ShaderNodeMix', 'COLOR'),
        ("Color Ramp", 'ShaderNodeValToRGB', 'COLOR'),
        ("Hue/Saturation", 'ShaderNodeHueSaturation', 'COLOR'),
        ("Invert Color", 'ShaderNodeInvert', 'COLOR'),
        ("RGB Curves", 'ShaderNodeRGBCurve', 'CURVE_DATA'),
        ("Emission", 'ShaderNodeEmission', 'LIGHT'),
    ],
    'VALUE': [
        ("Math", 'ShaderNodeMath', 'CON_KINEMATIC'),
        ("Map Range", 'ShaderNodeMapRange', 'ARROW_LEFTRIGHT'),
        ("Color Ramp", 'ShaderNodeValToRGB', 'COLOR'),
        ("Clamp", 'ShaderNodeClamp', 'ARROW_LEFTRIGHT'),
        ("Float Curve", 'ShaderNodeFloatCurve', 'CURVE_DATA'),
    ],
    'VECTOR': [
        ("Vector Math", 'ShaderNodeVectorMath', 'CON_KINEMATIC'),
        ("Mapping", 'ShaderNodeMapping', 'ORIENTATION_GLOBAL'),
        ("Bump", 'ShaderNodeBump', 'FORCE_TEXTURE'),
        ("Normal Map", 'ShaderNodeNormalMap', 'NORMALS_FACE'),
        ("Displacement", 'ShaderNodeDisplacement', 'FORCE_TEXTURE'),
    ],
}

_CONNECT_COMP = {
    'RGBA': [
        ("Mix", 'CompositorNodeMixRGB', 'COLOR'),
        ("Alpha Over", 'CompositorNodeAlphaOver', 'IMAGE_ALPHA'),
        ("Color Balance", 'CompositorNodeColorBalance', 'COLOR'),
        ("Hue Saturation Value", 'CompositorNodeHueSat', 'COLOR'),
        ("RGB Curves", 'CompositorNodeCurveRGB', 'CURVE_DATA'),
        ("Blur", 'CompositorNodeBlur', 'MOD_SMOOTH'),
        ("Glare", 'CompositorNodeGlare', 'LIGHT_SUN'),
        ("Viewer", 'CompositorNodeViewer', 'HIDE_OFF'),
    ],
    'VALUE': [
        ("Math", 'CompositorNodeMath', 'CON_KINEMATIC'),
        ("Map Range", 'CompositorNodeMapRange', 'ARROW_LEFTRIGHT'),
        ("Set Alpha", 'CompositorNodeSetAlpha', 'IMAGE_ALPHA'),
        ("Color Ramp", 'CompositorNodeValToRGB', 'COLOR'),
    ],
    'VECTOR': [
        ("Normalize", 'CompositorNodeNormalize', 'NORMALIZE_FCURVES'),
        ("Vector Curves", 'CompositorNodeCurveVec', 'CURVE_DATA'),
    ],
}

_CONNECT_MAPS = {
    'GeometryNodeTree': _CONNECT_GEO,
    'ShaderNodeTree': _CONNECT_SHADER,
    'CompositorNodeTree': _CONNECT_COMP,
}


def _source_output_types(source):
    """Distinct output socket types of `source`, in socket order, INT folded to VALUE."""
    seen = []
    for out in source.outputs:
        if out.hide or not out.enabled or out.bl_idname == 'NodeSocketVirtual':
            continue
        t = 'VALUE' if out.type == 'INT' else out.type
        if t not in seen:
            seen.append(t)
    return seen


def _draw_full_browse(pie, tree_type):
    if tree_type == 'GeometryNodeTree':
        _cats_geo(pie)
    elif tree_type == 'ShaderNodeTree':
        _cats_shader(pie)
    elif tree_type == 'CompositorNodeTree':
        _cats_comp(pie)


def _draw_context_connect(pie, context, source):
    """Add-Connect pie tailored to `source`'s output types: the per-type consumer lists
    unioned in socket order (primary output first) and deduped, capped to 7 slots plus an
    All Categories... fallback. Falls through to the full browse when nothing matches."""
    tree_type = context.space_data.tree_type
    cmap = _CONNECT_MAPS.get(tree_type)

    items = []
    if source is not None and cmap is not None:
        seen_ids = set()
        for t in _source_output_types(source):
            for label, node_type, icon in cmap.get(t, ()):
                if node_type not in seen_ids:
                    seen_ids.add(node_type)
                    items.append((label, node_type, icon))

    # No tailored matches (no source, unknown editor, or only exotic socket types) ->
    # show the full category browse as-is.
    if not items:
        _draw_full_browse(pie, tree_type)
        return

    for label, node_type, icon in items[:7]:
        _add_node_op(pie, label, node_type, icon)
    # Escape hatch: the full category browse, still in connect mode so leaves wire.
    pie.operator("wm.call_menu_pie", text="All Categories...", icon='ADD').name = "SUBPIE_MT_add_connect_all"


class SUBPIE_MT_add_connect(Menu):
    bl_label = "Add & Connect"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Same source the operator wires from: active node, else first selected.
        source = context.active_node
        if source is None and context.selected_nodes:
            source = context.selected_nodes[0]
        _draw_context_connect(pie, context, source)


class SUBPIE_MT_add_connect_all(Menu):
    bl_label = "Add & Connect — All Categories"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _draw_full_browse(pie, context.space_data.tree_type)


# ==============================================================================
# 8. MAIN CONTEXT MENU
# ==============================================================================

class NODE_PIE_MT_context(Menu):
    bl_idname = "NODE_PIE_MT_context_pie"
    bl_label = "Node Context Pie"

    def draw(self, context):
        # Reaching the main pie ends any in-progress Add Connect browse, so the category
        # sub-pies fall back to plain add-node behaviour.
        global _ADD_CONNECT_MODE
        _ADD_CONNECT_MODE = False

        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        pie = layout.menu_pie()

        if context.space_data.type != 'NODE_EDITOR' or not context.space_data.node_tree:
            return

        selected_nodes = context.selected_nodes
        num_selected = len(selected_nodes)

        if num_selected == 0:
            tree_type = context.space_data.tree_type
            if tree_type == 'GeometryNodeTree':
                self.draw_no_nodes_geo(pie, context)
            elif tree_type == 'ShaderNodeTree':
                self.draw_no_nodes_shader(pie, context)
            elif tree_type == 'CompositorNodeTree':
                self.draw_no_nodes_comp(pie, context)
            else:
                pie.label(text="Tree type not supported")
        elif num_selected == 1:
            self.draw_single_node(pie, context)
        else:
            self.draw_multi_nodes(pie, context)

    # --- ADD NODE PIES (no selection) ---

    def draw_no_nodes_geo(self, pie, context):
        _cats_geo(pie)

    def draw_no_nodes_shader(self, pie, context):
        _cats_shader(pie)

    def draw_no_nodes_comp(self, pie, context):
        _cats_comp(pie)

    # --- SELECTION PIES ---

    def draw_single_node(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST - detach only outputs, keep inputs (NW)
        if nw_loaded:
            pie.operator("node.nw_detach_outputs", text="Detach Outputs", icon='UNLINKED')
        else:
            pie.separator()
        # EAST - link to output (NW)
        if nw_loaded:
            pie.operator("node.nw_link_out", text="Link to Output", icon='DRIVER')
        else:
            pie.separator()
        # SOUTH
        pie.operator("node.mute_toggle", text="Mute / Unmute", icon='HIDE_OFF')
        # NORTH - add a node from the category pies and wire this node's best output into it
        pie.operator("node.cpie_add_connect_start", text="Add Connect...", icon='ADD')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Duplicate...", icon='DUPLICATE').name = "SUBPIE_MT_node_duplicate"
        # NORTH-EAST - add reroute nodes to all outputs (NW)
        if nw_loaded:
            pie.operator("node.nw_add_reroutes", text="Add Reroutes", icon='NODE').option = 'ALL'
        else:
            pie.separator()
        # SOUTH-WEST - delete submenu
        pie.operator("wm.call_menu_pie", text="Delete...", icon='TRASH').name = "SUBPIE_MT_node_delete"
        # SOUTH-EAST - dynamic mode/operation picker for this node type
        pie.operator("wm.call_menu_pie", text="Change Mode...", icon='DRIVER_TRANSFORM').name = "SUBPIE_MT_node_dynamic_mode"

    def draw_multi_nodes(self, pie, context):
        nw_loaded = "node_wrangler" in context.preferences.addons

        # WEST - detach only outputs, keep inputs (NW)
        if nw_loaded:
            pie.operator("node.nw_detach_outputs", text="Detach Outputs", icon='UNLINKED')
        else:
            pie.separator()
        # EAST - link active node to all other selected (NW) or attach
        if nw_loaded:
            op = pie.operator("node.nw_link_active_to_selected", text="Link Active to Selected", icon='LINKED')
            op.replace = False
            op.use_node_name = False
            op.use_outputs_names = False
        else:
            pie.operator("node.translate_attach", text="Attach Nodes", icon='LINKED')
        # SOUTH - mute/unmute, consistent with single-node
        pie.operator("node.mute_toggle", text="Mute / Unmute", icon='HIDE_OFF')
        # NORTH - Magic Merge: auto-detect mergeable output types and route to the
        # matching enumerate pie (or a type-chooser pie when several are available).
        pie.operator("node.cpie_magic_merge", text='Join / Merge...', icon='TRIA_UP')
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Duplicate...", icon='DUPLICATE').name = "SUBPIE_MT_node_duplicate"
        # NORTH-EAST
        pie.operator("node.cpie_link_active_replace_parent", text="Intercept Parent Link", icon='LINKED')
        # SOUTH-WEST - delete submenu
        pie.operator("wm.call_menu_pie", text="Delete...", icon='TRASH').name = "SUBPIE_MT_node_delete"
        # SOUTH-EAST - dynamic mode/operation picker for this node type
        pie.operator("wm.call_menu_pie", text="Change Mode...", icon='DRIVER_TRANSFORM').name = "SUBPIE_MT_node_dynamic_mode"


# ==============================================================================
# 9. REGISTRATION
# ==============================================================================

registry = [
    CONTEXTPIE_OT_combine_selected,
    NODE_OT_delete_add_reroute,
    NODE_OT_cpie_link_active_replace_parent,
    NODE_OT_cpie_add_connect,
    NODE_OT_cpie_add_connect_start,
    NODE_OT_cpie_merge_boolean,
    NODE_OT_cpie_merge_float,
    NODE_OT_cpie_merge_vector,
    NODE_OT_cpie_merge_color,
    NODE_OT_cpie_merge_shader,
    NODE_OT_cpie_merge_geometry,
    NODE_OT_cpie_magic_merge,
    SUBPIE_MT_merge_chooser,
    SUBPIE_MT_merge_boolean,
    SUBPIE_MT_merge_float,
    SUBPIE_MT_merge_vector,
    SUBPIE_MT_merge_color,
    SUBPIE_MT_merge_shader,
    SUBPIE_MT_merge_geometry,
    SUBPIE_MT_gn_mesh,
    SUBPIE_MT_gn_curve,
    SUBPIE_MT_gn_utilities,
    SUBPIE_MT_gn_io,
    SUBPIE_MT_gn_geometry_points,
    SUBPIE_MT_gn_attributes,
    SUBPIE_MT_gn_converter,
    SUBPIE_MT_gn_materials,
    SUBPIE_MT_sh_input,
    SUBPIE_MT_sh_output,
    SUBPIE_MT_sh_shader,
    SUBPIE_MT_sh_texture,
    SUBPIE_MT_sh_color,
    SUBPIE_MT_sh_vector,
    SUBPIE_MT_sh_value,
    SUBPIE_MT_sh_converter,
    SUBPIE_MT_co_input,
    SUBPIE_MT_co_output,
    SUBPIE_MT_co_color,
    SUBPIE_MT_co_filter,
    SUBPIE_MT_co_transform,
    SUBPIE_MT_co_matte,
    SUBPIE_MT_co_converter,
    SUBPIE_MT_co_vector,
    SUBPIE_MT_nw_batch_blend,
    SUBPIE_MT_nw_batch_math,
    SUBPIE_MT_node_delete,
    SUBPIE_MT_node_duplicate,
    SUBPIE_MT_add_connect,
    SUBPIE_MT_add_connect_all,
    NODE_PIE_MT_context,
]

def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=NODE_PIE_MT_context.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
        keymap_name="Node Editor",
        on_drag=False,
    )

def unregister():
    pass