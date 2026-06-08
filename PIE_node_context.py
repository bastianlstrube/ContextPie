# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie



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
        terminal_sockets = []

        for node in selected_nodes:
            for out in node.outputs:
                if out.hide or not out.enabled:
                    continue

                # Check if this output feeds internally into our selected group
                is_internal = any((link.to_node in selected_nodes) for link in out.links)

                if not is_internal:
                    terminal_sockets.append(out)

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
    """Detect the mergeable output types of selected nodes. Opens a type-chooser pie
    when more than one type is available, or goes straight to the merge pie when only one is"""
    bl_idname = "node.cpie_magic_merge"
    bl_label = "Magic Merge"

    @classmethod
    def poll(cls, context):
        return _merge_poll(context)

    def execute(self, context):
        types = _available_merge_types(context.selected_nodes, context.space_data.tree_type)
        if not types:
            self.report({'WARNING'}, "No mergeable outputs in the selection")
            return {'CANCELLED'}

        # One mergeable type -> jump straight to its enumerate pie; otherwise let the
        # user pick which type to merge on via the chooser pie.
        if len(types) == 1:
            bpy.ops.wm.call_menu_pie(name=_MERGE_ROUTING[types[0]][0])
        else:
            bpy.ops.wm.call_menu_pie(name="SUBPIE_MT_merge_chooser")
        return {'FINISHED'}


class SUBPIE_MT_merge_chooser(Menu):
    bl_label = "Merge Type"
    def draw(self, context):
        pie = self.layout.menu_pie()
        # Recomputed from the live selection so the slots always match what's mergeable.
        for t in _available_merge_types(context.selected_nodes, context.space_data.tree_type):
            pie_name, label, icon = _MERGE_ROUTING[t]
            pie.operator("wm.call_menu_pie", text=label, icon=icon).name = pie_name


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
        pie.operator("node.add_node", text="Cube", icon='MESH_CUBE').type = 'GeometryNodeMeshCube'
        pie.operator("node.add_node", text="Circle", icon='MESH_CIRCLE').type = 'GeometryNodeMeshCircle'
        pie.operator("node.add_node", text="Cylinder", icon='MESH_CYLINDER').type = 'GeometryNodeMeshCylinder'
        pie.operator("node.add_node", text="UV Sphere", icon='MESH_UVSPHERE').type = 'GeometryNodeMeshUVSphere'
        pie.operator("node.add_node", text="Extrude Mesh", icon='MESH_DATA').type = 'GeometryNodeExtrudeMesh'
        pie.operator("node.add_node", text="Subdivide Mesh", icon='MESH_DATA').type = 'GeometryNodeSubdivideMesh'
        pie.operator("node.add_node", text="Flip Faces", icon='MESH_DATA').type = 'GeometryNodeFlipFaces'
        pie.operator("node.add_node", text="Mesh to Curve", icon='CURVE_DATA').type = 'GeometryNodeMeshToCurve'

class SUBPIE_MT_gn_curve(Menu):
    bl_label = "Curve Nodes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Bezier Segment", icon='CURVE_BEZCURVE').type = 'GeometryNodeCurvePrimitiveBezierSegment'
        pie.operator("node.add_node", text="Curve Circle", icon='CURVE_BEZCIRCLE').type = 'GeometryNodeCurvePrimitiveCircle'
        pie.operator("node.add_node", text="Curve Line", icon='CURVE_PATH').type = 'GeometryNodeCurvePrimitiveLine'
        pie.operator("node.add_node", text="Resample Curve", icon='CURVE_DATA').type = 'GeometryNodeResampleCurve'
        pie.operator("node.add_node", text="Trim Curve", icon='CURVE_DATA').type = 'GeometryNodeTrimCurve'
        pie.operator("node.add_node", text="Fill Curve", icon='MESH_DATA').type = 'GeometryNodeFillCurve'
        pie.operator("node.add_node", text="Curve to Mesh", icon='MESH_DATA').type = 'GeometryNodeCurveToMesh'
        pie.operator("node.add_node", text="Curve to Points", icon='PARTICLE_DATA').type = 'GeometryNodeCurveToPoints'

class SUBPIE_MT_gn_utilities(Menu):
    bl_label = "Utilities & Math"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath'
        pie.operator("node.add_node", text="Vector Math", icon='CON_KINEMATIC').type = 'ShaderNodeVectorMath'
        pie.operator("node.add_node", text="Boolean Math", icon='CON_KINEMATIC').type = 'FunctionNodeBooleanMath'
        pie.operator("node.add_node", text="Random Value", icon='RNDCURVE').type = 'FunctionNodeRandomValue'
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'ShaderNodeValToRGB'
        pie.operator("node.add_node", text="Float Curve", icon='CURVE_DATA').type = 'ShaderNodeFloatCurve'
        pie.operator("node.add_node", text="Switch", icon='ARROW_LEFTRIGHT').type = 'GeometryNodeSwitch'
        pie.operator("node.add_node", text="Map Range", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeMapRange'

class SUBPIE_MT_gn_io(Menu):
    bl_label = "Input & Output"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # 1. WEST - Object Data
        pie.operator("node.add_node", text="Object Info", icon='OBJECT_DATA').type = 'GeometryNodeObjectInfo'
        # 2. EAST - Scene Data
        pie.operator("node.add_node", text="Scene Time", icon='TIME').type = 'GeometryNodeInputSceneTime'
        # 3. SOUTH - Basic Constant
        pie.operator("node.add_node", text="Value", icon='PROPERTIES').type = 'ShaderNodeValue'
        # 4. NORTH - Material Constant
        pie.operator("node.add_node", text="Material", icon='MATERIAL').type = 'GeometryNodeInputMaterial'
        # 5. NORTH-WEST - Collection Constant
        pie.operator("node.add_node", text="Collection Info", icon='OUTLINER_COLLECTION').type = 'GeometryNodeCollectionInfo'
        # 6. NORTH-EAST - Self Reference
        pie.operator("node.add_node", text="Self Object", icon='NODE_SEL').type = 'GeometryNodeSelfObject'
        # 7. SOUTH-WEST - Integer Constant
        pie.operator("node.add_node", text="Integer", icon='LINENUMBERS_ON').type = 'FunctionNodeInputInt'
        # 8. SOUTH-EAST - Boolean Constant
        pie.operator("node.add_node", text="Boolean", icon='CHECKBOX_HLT').type = 'FunctionNodeInputBool'

class SUBPIE_MT_gn_geometry_instances(Menu):
    bl_label = "Geometry & Instances"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Join Geometry").type = 'GeometryNodeJoinGeometry'
        pie.operator("node.add_node", text="Transform", icon='ORIENTATION_GLOBAL').type = 'GeometryNodeTransform'
        pie.operator("node.add_node", text="Set Position", icon='SNAP_GRID').type = 'GeometryNodeSetPosition'
        pie.operator("node.add_node", text="Instance on Points", icon='PARTICLE_DATA').type = 'GeometryNodeInstanceOnPoints'
        pie.operator("node.add_node", text="Realize Instances", icon='OUTLINER_OB_GROUP_INSTANCE').type = 'GeometryNodeRealizeInstances'
        pie.operator("node.add_node", text="Separate Geometry", icon='MESH_DATA').type = 'GeometryNodeSeparateGeometry'
        pie.operator("node.add_node", text="Delete Geometry", icon='CANCEL').type = 'GeometryNodeDeleteGeometry'
        pie.operator("node.add_node", text="Geometry to Instance", icon='OUTLINER_OB_GROUP_INSTANCE').type = 'GeometryNodeGeometryToInstance'

class SUBPIE_MT_gn_attributes(Menu):
    bl_label = "Attributes & Textures"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Named Attribute", icon='SPREADSHEET').type = 'GeometryNodeInputNamedAttribute'
        pie.operator("node.add_node", text="Store Named Attribute", icon='SPREADSHEET').type = 'GeometryNodeStoreNamedAttribute'
        pie.operator("node.add_node", text="Capture Attribute", icon='SPREADSHEET').type = 'GeometryNodeCaptureAttribute'
        pie.operator("node.add_node", text="Noise Texture", icon='TEXTURE').type = 'ShaderNodeTexNoise'
        pie.operator("node.add_node", text="Voronoi Texture", icon='TEXTURE').type = 'ShaderNodeTexVoronoi'
        pie.operator("node.add_node", text="Gradient Texture", icon='TEXTURE').type = 'ShaderNodeTexGradient'
        pie.operator("node.add_node", text="Blur Attribute", icon='MOD_SMOOTH').type = 'GeometryNodeBlurAttribute'
        pie.operator("node.add_node", text="Sample Index", icon='SPREADSHEET').type = 'GeometryNodeSampleIndex'

class SUBPIE_MT_gn_points_volumes(Menu):
    bl_label = "Points & Volumes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Distribute Points on Faces", icon='PARTICLE_DATA').type = 'GeometryNodeDistributePointsOnFaces'
        pie.operator("node.add_node", text="Points", icon='PARTICLE_DATA').type = 'GeometryNodePoints'
        pie.operator("node.add_node", text="Points to Volume", icon='VOLUME_DATA').type = 'GeometryNodePointsToVolume'
        pie.operator("node.add_node", text="Volume to Mesh", icon='MESH_DATA').type = 'GeometryNodeVolumeToMesh'
        pie.operator("node.add_node", text="Points to Vertices", icon='VERTEXSEL').type = 'GeometryNodePointsToVertices'
        pie.operator("node.add_node", text="Distribute Points in Volume", icon='PARTICLE_DATA').type = 'GeometryNodeDistributePointsInVolume'
        pie.operator("node.add_node", text="Volume Cube", icon='VOLUME_DATA').type = 'GeometryNodeVolumeCube'
        pie.operator("node.add_node", text="Set Point Radius", icon='PARTICLE_DATA').type = 'GeometryNodeSetPointRadius'

class SUBPIE_MT_gn_materials(Menu):
    bl_label = "Materials & UV"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Set Material", icon='MATERIAL').type = 'GeometryNodeSetMaterial'
        pie.operator("node.add_node", text="Replace Material", icon='MATERIAL').type = 'GeometryNodeReplaceMaterial'
        pie.operator("node.add_node", text="Material Selection", icon='MATERIAL').type = 'GeometryNodeMaterialSelection'
        pie.operator("node.add_node", text="Set Material Index", icon='MATERIAL').type = 'GeometryNodeSetMaterialIndex'
        pie.operator("node.add_node", text="Input Material", icon='MATERIAL').type = 'GeometryNodeInputMaterial'
        pie.operator("node.add_node", text="Set Shade Smooth", icon='SHADING_RENDERED').type = 'GeometryNodeSetShadeSmooth'
        pie.operator("node.add_node", text="UV Unwrap", icon='UV').type = 'GeometryNodeUVUnwrap'
        pie.operator("node.add_node", text="UV Pack Islands", icon='UV').type = 'GeometryNodeUVPackIslands'


# ==============================================================================
# 2. SHADER NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_sh_input(Menu):
    bl_label = "Input"
    def draw(self, context):
        pie = self.layout.menu_pie()

        # 1. WEST
        pie.operator("node.add_node", text="Color", icon='COLOR').type = 'ShaderNodeRGB'
        # 2. EAST
        pie.operator("node.add_node", text="Value", icon='PROPERTIES').type = 'ShaderNodeValue'
        # 3. SOUTH
        pie.operator("node.add_node", text="Attribute", icon='SPREADSHEET').type = 'ShaderNodeAttribute'
        # 4. NORTH
        pie.operator("node.add_node", text="Object Info", icon='OBJECT_DATA').type = 'ShaderNodeObjectInfo'
        # 5. NORTH-WEST
        pie.operator("node.add_node", text="Geometry", icon='MESH_DATA').type = 'ShaderNodeNewGeometry'
        # 6. NORTH-EAST
        pie.operator("node.add_node", text="UV Map", icon='UV').type = 'ShaderNodeUVMap'
        # 7. SOUTH-WEST
        pie.operator("node.add_node", text="Camera Data", icon='CAMERA_DATA').type = 'ShaderNodeCameraData'
        # 8. SOUTH-EAST
        pie.operator("node.add_node", text="Ambient Occlusion", icon='NODE_SEL').type = 'ShaderNodeAmbientOcclusion'

class SUBPIE_MT_sh_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Material Output", icon='MATERIAL').type = 'ShaderNodeOutputMaterial'
        pie.operator("node.add_node", text="Light Output", icon='LIGHT').type = 'ShaderNodeOutputLight'
        pie.operator("node.add_node", text="World Output", icon='WORLD').type = 'ShaderNodeOutputWorld'
        pie.operator("node.add_node", text="AOV Output", icon='RENDER_RESULT').type = 'ShaderNodeOutputAOV'
        pie.operator("node.add_node", text="Line Style Output", icon='STROKE').type = 'ShaderNodeOutputLineStyle'
        pie.operator("node.add_node", text="Background", icon='WORLD').type = 'ShaderNodeBackground'
        pie.operator("node.add_node", text="Holdout", icon='SHADING_WIRE').type = 'ShaderNodeHoldout'
        pie.operator("node.add_node", text="Emission", icon='LIGHT').type = 'ShaderNodeEmission'

class SUBPIE_MT_sh_shader(Menu):
    bl_label = "Shader"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Principled BSDF", icon='SHADING_RENDERED').type = 'ShaderNodeBsdfPrincipled'
        pie.operator("node.add_node", text="Emission", icon='LIGHT').type = 'ShaderNodeEmission'
        pie.operator("node.add_node", text="Mix Shader", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeMixShader'
        pie.operator("node.add_node", text="Transparent BSDF", icon='SHADING_WIRE').type = 'ShaderNodeBsdfTransparent'
        pie.operator("node.add_node", text="Glass BSDF", icon='SHADING_RENDERED').type = 'ShaderNodeBsdfGlass'
        pie.operator("node.add_node", text="Volume Scatter", icon='VOLUME_DATA').type = 'ShaderNodeVolumeScatter'
        pie.operator("node.add_node", text="Glossy BSDF", icon='SHADING_RENDERED').type = 'ShaderNodeBsdfGlossy'
        pie.operator("node.add_node", text="Principled Volume", icon='VOLUME_DATA').type = 'ShaderNodeVolumePrincipled'

class SUBPIE_MT_sh_texture(Menu):
    bl_label = "Texture"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Image Texture", icon='IMAGE_DATA').type = 'ShaderNodeTexImage'
        pie.operator("node.add_node", text="Noise Texture", icon='TEXTURE').type = 'ShaderNodeTexNoise'
        pie.operator("node.add_node", text="Voronoi Texture", icon='TEXTURE').type = 'ShaderNodeTexVoronoi'
        pie.operator("node.add_node", text="Gradient Texture", icon='TEXTURE').type = 'ShaderNodeTexGradient'
        pie.operator("node.add_node", text="Wave Texture", icon='TEXTURE').type = 'ShaderNodeTexWave'
        pie.operator("node.add_node", text="Sky Texture", icon='LIGHT_SUN').type = 'ShaderNodeTexSky'
        pie.operator("node.add_node", text="Checker Texture", icon='TEXTURE').type = 'ShaderNodeTexChecker'
        pie.operator("node.add_node", text="Magic Texture", icon='TEXTURE').type = 'ShaderNodeTexMagic'

class SUBPIE_MT_sh_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'ShaderNodeValToRGB'
        pie.operator("node.add_node", text="Mix Color", icon='COLOR').type = 'ShaderNodeMix'
        pie.operator("node.add_node", text="RGB Curves", icon='CURVE_DATA').type = 'ShaderNodeRGBCurve'
        pie.operator("node.add_node", text="Hue/Saturation", icon='COLOR').type = 'ShaderNodeHueSaturation'
        pie.operator("node.add_node", text="Invert Color", icon='COLOR').type = 'ShaderNodeInvert'
        pie.operator("node.add_node", text="Bright/Contrast", icon='COLORSET_10_VEC').type = 'ShaderNodeBrightContrast'
        pie.operator("node.add_node", text="Gamma", icon='COLOR').type = 'ShaderNodeGamma'
        pie.operator("node.add_node", text="Light Falloff", icon='LIGHT').type = 'ShaderNodeLightFalloff'

class SUBPIE_MT_sh_vector(Menu):
    bl_label = "Vector"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Mapping", icon='ORIENTATION_GLOBAL').type = 'ShaderNodeMapping'
        pie.operator("node.add_node", text="Bump", icon='FORCE_TEXTURE').type = 'ShaderNodeBump'
        pie.operator("node.add_node", text="Displacement", icon='FORCE_TEXTURE').type = 'ShaderNodeDisplacement'
        pie.operator("node.add_node", text="Normal Map", icon='NORMALS_FACE').type = 'ShaderNodeNormalMap'
        pie.operator("node.add_node", text="Vector Math", icon='CON_KINEMATIC').type = 'ShaderNodeVectorMath'
        pie.operator("node.add_node", text="Vector Displacement", icon='FORCE_TEXTURE').type = 'ShaderNodeVectorDisplacement'
        pie.operator("node.add_node", text="Vector Curves", icon='CURVE_DATA').type = 'ShaderNodeVectorCurve'
        pie.operator("node.add_node", text="Vector Transform", icon='ORIENTATION_GLOBAL').type = 'ShaderNodeVectorTransform'

class SUBPIE_MT_sh_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'ShaderNodeMath'
        pie.operator("node.add_node", text="Map Range", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeMapRange'
        pie.operator("node.add_node", text="Separate Color", icon='COLOR').type = 'ShaderNodeSeparateColor'
        pie.operator("node.add_node", text="Combine Color", icon='COLOR').type = 'ShaderNodeCombineColor'
        pie.operator("node.add_node", text="Separate XYZ", icon='AXIS_SIDE').type = 'ShaderNodeSeparateXYZ'
        pie.operator("node.add_node", text="Combine XYZ", icon='AXIS_SIDE').type = 'ShaderNodeCombineXYZ'
        pie.operator("node.add_node", text="Clamp", icon='ARROW_LEFTRIGHT').type = 'ShaderNodeClamp'
        pie.operator("node.add_node", text="Blackbody", icon='LIGHT').type = 'ShaderNodeBlackbody'


# ==============================================================================
# 3. COMPOSITOR NODES SUB-MENUS
# ==============================================================================

class SUBPIE_MT_co_input(Menu):
    bl_label = "Input"
    def draw(self, context):
        pie = self.layout.menu_pie()

        # WEST
        pie.operator("node.add_node", text="Image", icon='IMAGE_DATA').type = 'CompositorNodeImage'
        # EAST
        pie.operator("node.add_node", text="Render Layers", icon='RENDERLAYERS').type = 'CompositorNodeRLayers'
        # SOUTH
        pie.operator("node.add_node", text="Value", icon='PROPERTIES').type = 'CompositorNodeValue'
        # NORTH
        pie.operator("node.add_node", text="Time", icon='TIME').type = 'CompositorNodeTime'
        # NORTH-WEST
        pie.operator("node.add_node", text="Movie Clip", icon='TRACKER').type = 'CompositorNodeMovieClip'
        # NORTH-EAST
        pie.operator("node.add_node", text="RGB", icon='COLOR').type = 'CompositorNodeRGB'
        # SOUTH-WEST
        pie.operator("node.add_node", text="Mask", icon='MOD_MASK').type = 'CompositorNodeMask'
        # SOUTH-EAST
        pie.operator("node.add_node", text="Track Position", icon='TRACKER').type = 'CompositorNodeTrackPos'

class SUBPIE_MT_co_output(Menu):
    bl_label = "Output"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Composite", icon='RENDER_RESULT').type = 'CompositorNodeComposite'
        pie.operator("node.add_node", text="Viewer", icon='HIDE_ON').type = 'CompositorNodeViewer'
        pie.operator("node.add_node", text="File Output", icon='FILE_IMAGE').type = 'CompositorNodeOutputFile'
        pie.operator("node.add_node", text="Split Viewer", icon='HIDE_ON').type = 'CompositorNodeSplitViewer'
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()

class SUBPIE_MT_co_color(Menu):
    bl_label = "Color"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Mix", icon='COLOR').type = 'CompositorNodeMixRGB'
        pie.operator("node.add_node", text="Alpha Over", icon='IMAGE_ALPHA').type = 'CompositorNodeAlphaOver'
        pie.operator("node.add_node", text="Color Balance", icon='COLOR').type = 'CompositorNodeColorBalance'
        pie.operator("node.add_node", text="Color Ramp", icon='COLOR').type = 'CompositorNodeValToRGB'
        pie.operator("node.add_node", text="Hue Saturation Value", icon='COLOR').type = 'CompositorNodeHueSat'
        pie.operator("node.add_node", text="RGB Curves", icon='CURVE_DATA').type = 'CompositorNodeCurveRGB'
        pie.operator("node.add_node", text="Bright/Contrast", icon='COLORSET_10_VEC').type = 'CompositorNodeBrightContrast'
        pie.operator("node.add_node", text="Gamma", icon='COLOR').type = 'CompositorNodeGamma'

class SUBPIE_MT_co_filter(Menu):
    bl_label = "Filter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Blur", icon='MOD_SMOOTH').type = 'CompositorNodeBlur'
        pie.operator("node.add_node", text="Glare", icon='LIGHT_SUN').type = 'CompositorNodeGlare'
        pie.operator("node.add_node", text="Directional Blur", icon='MOD_SMOOTH').type = 'CompositorNodeDBlur'
        pie.operator("node.add_node", text="Sun Beams", icon='LIGHT_SUN').type = 'CompositorNodeSunBeams'
        pie.operator("node.add_node", text="Pixelate", icon='TEXTURE').type = 'CompositorNodePixelate'
        pie.operator("node.add_node", text="Despeckle", icon='MOD_SMOOTH').type = 'CompositorNodeDespeckle'
        pie.operator("node.add_node", text="Filter", icon='FILTER').type = 'CompositorNodeFilter'
        pie.operator("node.add_node", text="Bokeh Blur", icon='IMAGE_DATA').type = 'CompositorNodeBokehBlur'

class SUBPIE_MT_co_transform(Menu):
    bl_label = "Transform"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Transform", icon='ORIENTATION_GLOBAL').type = 'CompositorNodeTransform'
        pie.operator("node.add_node", text="Translate", icon='NODE').type = 'CompositorNodeTranslate'
        pie.operator("node.add_node", text="Scale", icon='NODE').type = 'CompositorNodeScale'
        pie.operator("node.add_node", text="Rotate", icon='NODE').type = 'CompositorNodeRotate'
        pie.operator("node.add_node", text="Flip", icon='NODE').type = 'CompositorNodeFlip'
        pie.operator("node.add_node", text="Crop", icon='FULLSCREEN_EXIT').type = 'CompositorNodeCrop'
        pie.operator("node.add_node", text="Movie Distortion", icon='TRACKER').type = 'CompositorNodeMovieDistortion'
        pie.operator("node.add_node", text="Corner Pin", icon='NODE').type = 'CompositorNodeCornerPin'

class SUBPIE_MT_co_matte(Menu):
    bl_label = "Matte & Mask"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Cryptomatte", icon='RESTRICT_COLOR_OFF').type = 'CompositorNodeCryptomatteV2'
        pie.operator("node.add_node", text="Keying", icon='IMAGE_ALPHA').type = 'CompositorNodeKeying'
        pie.operator("node.add_node", text="Color Key", icon='IMAGE_ALPHA').type = 'CompositorNodeColorMatte'
        pie.operator("node.add_node", text="Box Mask", icon='MOD_MASK').type = 'CompositorNodeBoxMask'
        pie.operator("node.add_node", text="Ellipse Mask", icon='MOD_MASK').type = 'CompositorNodeEllipseMask'
        pie.operator("node.add_node", text="Luminance Key", icon='IMAGE_ALPHA').type = 'CompositorNodeLumaMatte'
        pie.operator("node.add_node", text="Chroma Key", icon='IMAGE_ALPHA').type = 'CompositorNodeChromaMatte'
        pie.operator("node.add_node", text="Difference Key", icon='IMAGE_ALPHA').type = 'CompositorNodeDiffMatte'

class SUBPIE_MT_co_converter(Menu):
    bl_label = "Converter"
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("node.add_node", text="Math", icon='CON_KINEMATIC').type = 'CompositorNodeMath'
        pie.operator("node.add_node", text="Set Alpha", icon='IMAGE_ALPHA').type = 'CompositorNodeSetAlpha'
        pie.operator("node.add_node", text="ID Mask", icon='MOD_MASK').type = 'CompositorNodeIDMask'
        pie.operator("node.add_node", text="RGB to BW", icon='COLOR').type = 'CompositorNodeRGBToBW'
        pie.operator("node.add_node", text="Separate Color", icon='COLOR').type = 'CompositorNodeSeparateColor'
        pie.operator("node.add_node", text="Combine Color", icon='COLOR').type = 'CompositorNodeCombineColor'
        pie.operator("node.add_node", text="Alpha Convert", icon='IMAGE_ALPHA').type = 'CompositorNodePremulKey'
        pie.operator("node.add_node", text="Normalize", icon='NORMALIZE_FCURVES').type = 'CompositorNodeNormalize'


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

class SUBPIE_MT_node_group(Menu):
    bl_label = "Group"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Opened from SE: cluster at SE/E, separators elsewhere.
        # WEST
        pie.separator()
        # EAST - adjacent to SE
        pie.operator("node.add_node", text="Group Input", icon='FORWARD').type = 'NodeGroupInput'
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
        # SOUTH-EAST - primary
        pie.operator("node.add_node", text="Group Output", icon='BACK').type = 'NodeGroupOutput'


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
        pie.separator()


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
# 7. MAIN CONTEXT MENU
# ==============================================================================

class NODE_PIE_MT_context(Menu):
    bl_idname = "NODE_PIE_MT_context_pie"
    bl_label = "Node Context Pie"

    def draw(self, context):
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
        # WEST
        pie.operator("wm.call_menu_pie", text="Mesh Nodes...", icon='MESH_DATA').name = "SUBPIE_MT_gn_mesh"
        # EAST
        pie.operator("wm.call_menu_pie", text="Curve Nodes...", icon='CURVE_DATA').name = "SUBPIE_MT_gn_curve"
        # SOUTH
        pie.operator("wm.call_menu_pie", text="Utilities & Math...", icon='CON_KINEMATIC').name = "SUBPIE_MT_gn_utilities"
        # NORTH
        pie.operator("wm.call_menu_pie", text="Input & Output...", icon='NODETREE').name = "SUBPIE_MT_gn_io"
        # NORTH-WEST
        pie.operator("wm.call_menu_pie", text="Geometry & Instances...", icon='GROUP_VERTEX').name = "SUBPIE_MT_gn_geometry_instances"
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text="Attributes & Textures...", icon='SPREADSHEET').name = "SUBPIE_MT_gn_attributes"
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text="Points & Volumes...", icon='PARTICLE_DATA').name = "SUBPIE_MT_gn_points_volumes"
        # SOUTH-EAST
        pie.operator("wm.call_menu_pie", text="Materials & UV...", icon='MATERIAL').name = "SUBPIE_MT_gn_materials"

    def draw_no_nodes_shader(self, pie, context):
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
        pie.operator("wm.call_menu_pie", text="Group...", icon='NODETREE').name = "SUBPIE_MT_node_group"

    def draw_no_nodes_comp(self, pie, context):
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
        pie.operator("wm.call_menu_pie", text="Group...", icon='NODETREE').name = "SUBPIE_MT_node_group"

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
        # NORTH - link to viewer (geo/comp only)
        tree_type = context.space_data.tree_type if context.space_data.node_tree else None
        if tree_type in ('GeometryNodeTree', 'CompositorNodeTree'):
            pie.operator("node.link_viewer", text="Link to Viewer", icon='HIDE_OFF')
        else:
            pie.separator()
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
# 8. REGISTRATION
# ==============================================================================

registry = [
    CONTEXTPIE_OT_combine_selected,
    NODE_OT_cpie_link_active_replace_parent,
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
    SUBPIE_MT_gn_geometry_instances,
    SUBPIE_MT_gn_attributes,
    SUBPIE_MT_gn_points_volumes,
    SUBPIE_MT_gn_materials,
    SUBPIE_MT_sh_input,
    SUBPIE_MT_sh_output,
    SUBPIE_MT_sh_shader,
    SUBPIE_MT_sh_texture,
    SUBPIE_MT_sh_color,
    SUBPIE_MT_sh_vector,
    SUBPIE_MT_sh_converter,
    SUBPIE_MT_co_input,
    SUBPIE_MT_co_output,
    SUBPIE_MT_co_color,
    SUBPIE_MT_co_filter,
    SUBPIE_MT_co_transform,
    SUBPIE_MT_co_matte,
    SUBPIE_MT_co_converter,
    SUBPIE_MT_nw_batch_blend,
    SUBPIE_MT_nw_batch_math,
    SUBPIE_MT_node_group,
    SUBPIE_MT_node_delete,
    SUBPIE_MT_node_duplicate,
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
