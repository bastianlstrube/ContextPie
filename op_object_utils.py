# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math

def create_joiner_node_group(name, slot_count):
    """
    Creates a new Geometry Node group with a specified number of object inputs
    organized into a collapsible panel. Designed for Blender 4.2+.
    """
    node_group = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
    nodes = node_group.nodes
    links = node_group.links
    
    # Clear any default nodes FIRST to ensure a clean slate
    nodes.clear()
    
    # --- 1. DEFINE THE MODIFIER INTERFACE ---
    
    # Create the final 'Geometry' output socket
    node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    
    # Create a collapsible panel for all the object inputs
    panel = node_group.interface.new_panel("Object Inputs")
    
    # Create all the object input sockets and assign them to the panel
    for i in range(slot_count):
        socket_name = f"Object {i+1}"
        socket = node_group.interface.new_socket(name=socket_name, in_out="INPUT", socket_type='NodeSocketObject', parent=panel)

    # --- 2. CREATE AND ARRANGE THE NODES ---

    # Core nodes
    input_node = nodes.new(type='NodeGroupInput')
    output_node = nodes.new(type='NodeGroupOutput')
    join_node = nodes.new(type='GeometryNodeJoinGeometry')
    
    input_node.location = (-400, 0)
    join_node.location = (150, 0)
    output_node.location = (400, 0)
    
    links.new(join_node.outputs['Geometry'], output_node.inputs['Geometry'])

    # --- 3. CREATE OBJECT INFO NODES AND LINK THEM ---
    
    node_y_pos_start = (slot_count - 1) * 120

    for i in range(slot_count):
        socket_name = f"Object {i+1}"
        obj_info_node = nodes.new(type='GeometryNodeObjectInfo')
        obj_info_node.location = (-150, node_y_pos_start - (i * 230))
        links.new(input_node.outputs[socket_name], obj_info_node.inputs['Object'])
        links.new(obj_info_node.outputs['Geometry'], join_node.inputs['Geometry'])
        
    return node_group


class OBJECT_OT_join_modifier(bpy.types.Operator):
    """
    Join selection non-destructively to a new object with a Geo Nodes modifier.
    """
    bl_idname = "object.join_modifier"
    bl_label = "Join with Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    # Operator properties for the Redo Panel
    initial_location: bpy.props.EnumProperty(
        name="Initial Location",
        description="Where to place the newly created object",
        items=[('CURSOR', "3D Cursor", "Place at 3D Cursor"), ('ACTIVE', "Active Object", "Place at Active Object")],
        default='CURSOR'
    )
    
    transform_space: bpy.props.EnumProperty(
        name="Transform Space",
        description="Choose how object coordinates are imported",
        items=[('RELATIVE', "Relative", "Relative to modifier object"), ('ORIGINAL', "Original", "Original world space")],
        default='RELATIVE'
    )

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) >= 1

    def execute(self, context):
        selected_objects = context.selected_objects[:]
        
        # --- 1. DETERMINE NODE GROUP NAME AND SIZE ---
        num_selected = len(selected_objects) + 2
        slot_count = max(6, math.ceil(num_selected / 6.0) * 6)
        node_group_name = f"GeoJoiner_{slot_count}"
        
        # --- 2. FIND OR CREATE THE NODE GROUP ---
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            self.report({'INFO'}, f"Creating new node group: {node_group_name}")
            node_group = create_joiner_node_group(node_group_name, slot_count)
        else:
            self.report({'INFO'}, f"Reusing existing node group: {node_group_name}")

        # Determine location for the new object based on user choice
        if self.initial_location == 'CURSOR':
            new_obj_location = context.scene.cursor.location.copy()
        else:
            active_obj = context.active_object
            new_obj_location = active_obj.location.copy() if active_obj else context.scene.cursor.location.copy()

        # Create the new object and add the modifier
        mesh = bpy.data.meshes.new(name="JoinedMesh")
        joiner_obj = bpy.data.objects.new("JoinedObject", mesh)
        joiner_obj.location = new_obj_location
        context.collection.objects.link(joiner_obj)
        geo_mod = joiner_obj.modifiers.new(name="Joiner", type='NODES')
        geo_mod.node_group = node_group

        # --- 3. POPULATE MODIFIER INPUTS AND SETTINGS ---
        
        # Find the panel by its name to access its child sockets
        panel = node_group.interface.items_tree.get("Object Inputs")
        if panel:
            # Assign selected objects to the sockets inside the panel
            for i, obj in enumerate(selected_objects):
                if i < len(panel.interface_items):
                    socket_identifier = panel.interface_items[i].identifier
                    geo_mod[socket_identifier] = obj
        
        # Update the transform space on ALL Object Info nodes inside the group
        for node in node_group.nodes:
            if node.type == 'OBJECT_INFO':
                node.transform_space = self.transform_space

        # Final scene cleanup
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = joiner_obj
        joiner_obj.select_set(True)

        self.report({'INFO'}, f"Created '{joiner_obj.name}' with {len(selected_objects)} objects")
        return {'FINISHED'}

# Custom Operator for change display type for multiple selected objects
class OBJECT_OT_edit_display_type(bpy.types.Operator):
    bl_idname = "object.edit_display_type"
    bl_label = "Set Display Type"
    bl_description = "Sets the display type for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    display_type: bpy.props.EnumProperty(
        name="Display Type",
        description="How to display the object",
        items=[
            ('SOLID', "Solid", "Rendered normally"),
            ('WIRE', "Wireframe", "Display as wireframe"),
            ('BOUNDS', "Bounding Box", "Display as bounding box"),
            ('TEXTURED', "Textured", "Display with textures (if available)"),
        ],
        default='SOLID',  # Set a default value
    )

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            obj.display_type = self.display_type

        return {'FINISHED'}

# Custom Operator for change object colour for multiple selected objects
class OBJECT_OT_edit_obj_color(bpy.types.Operator):
    bl_idname = "object.edit_obj_color"
    bl_label = "Set Object Colour"
    bl_description = "Sets the object colour for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        description="Object Color (RGBA)"
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            obj.color = self.color

        return {'FINISHED'}

# Add Boolean Operator with collection management
class OBJECT_OT_add_pie_boolean(bpy.types.Operator):
    bl_idname = "object.add_pie_boolean"
    bl_label = "Set Display Type"
    bl_description = "Sets the display type for selected objects"
    bl_options = {'REGISTER', 'UNDO'}           # Enable undo for the operation

    boolean_type: bpy.props.EnumProperty(
        name="Boolean Type",
        description="Which type of boolean modifier",
        items=[
            ('DIFFERENCE', "Difference", "Subtract active from selected"),
            ('UNION', "Union", "Union active to selected"),
            ('INTERSECT', "Intersect", "Intersect active with selected"),
            ('SPLIT', "Split", "Duplicate and split active from selected"),            
        ],
        default='DIFFERENCE',  # Set a default value
        )

    def link_sole_collection(self, obj, target_collection):
        "links object only to given collection"
        if not isinstance(target_collection, bpy.types.Collection):
            self.report({'WARNING'}, "Invalid collection object provided.")
            return {'CANCELLED'}

        collections_copy = list(obj.users_collection)
        for collection in collections_copy:
            collection.objects.unlink(obj)
        target_collection.objects.link(obj)

        self.report({'INFO'}, f"Objects linked to '{target_collection.name}'.")
        return {'FINISHED'}

    def addModifier(self, obj, selobj, modType):
        modname = "Modifier_" + modType.title()
        mod = selobj.modifiers.get(modname)
        if mod:
            if not mod.operand_type == 'COLLECTION':
                if obj.users_collection:
                    sCollection = obj.users_collection[0]
                else:
                    sCollection = bpy.context.scene.collection
                modCollection = bpy.data.collections.new(selobj.name + "_" + modname)
                sCollection.children.link(modCollection)
                olobj = mod.object
                self.link_sole_collection(olobj, modCollection)
                mod.operand_type = 'COLLECTION'
                mod.collection = modCollection
            else:
                modCollection = mod.collection

            self.link_sole_collection(obj, modCollection)
            mod.operation = modType
            obj.display_type = 'WIRE'
        else:
            mod = selobj.modifiers.new(modname, 'BOOLEAN')
            mod.operation = modType
            mod.object = obj
            obj.display_type = 'WIRE'

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        obj = bpy.context.object
        modType = self.boolean_type
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        # If split, create duplicate of selection and rename
        if modType == 'SPLIT':
            obj.select_set(False)
            bpy.ops.object.duplicate_move_linked()
            splitInstances = bpy.context.selected_objects
            for split in splitInstances:
                splitname = split.name.split('.')[0] + '_Inside'
                olsplit = bpy.data.objects.get(splitname)
                if olsplit:
                    bpy.data.objects.remove(split, do_unlink=True)
                    self.addModifier(obj, olsplit, 'INTERSECT')
                else:
                    split.name = splitname
                    self.addModifier(obj, split, 'INTERSECT')

        for selobj in selected_objects:
            if selobj == obj or selobj.type != 'MESH':
                continue

            if modType == 'SPLIT':
                self.addModifier(obj, selobj, 'DIFFERENCE')
            else:
                self.addModifier(obj, selobj, modType)


        return {'FINISHED'}


registry = [
    OBJECT_OT_join_modifier,
    OBJECT_OT_edit_display_type,
    OBJECT_OT_edit_obj_color,
    OBJECT_OT_add_pie_boolean,
]
