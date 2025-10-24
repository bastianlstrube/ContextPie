# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math

def create_geo_joiner_group():
    """
    Creates a standardized "GeoJoiner" node group for joining individual objects.
    """
    node_group = bpy.data.node_groups.new(name="GeoJoiner", type='GeometryNodeTree')
    nodes = node_group.nodes
    links = node_group.links
    nodes.clear()
    
    # --- 1. DEFINE THE MODIFIER INTERFACE ---
    node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    
    total_sockets = 40
    # Create panels and sockets for object inputs
    for i in range(4):
        panel_name = f"Objects {(i*10)+1:02d}-{(i+1)*10}"
        panel = node_group.interface.new_panel(name=panel_name, default_closed=True)
        for j in range(10):
            socket_index = (i * 10) + j + 1
            socket_name = f"Object {socket_index:02d}"
            node_group.interface.new_socket(name=socket_name, in_out="INPUT", socket_type='NodeSocketObject', parent=panel)

    # --- 2. CREATE AND ARRANGE THE NODES ---
    input_node = nodes.new(type='NodeGroupInput')
    output_node = nodes.new(type='NodeGroupOutput')
    join_node = nodes.new(type='GeometryNodeJoinGeometry')
    self_node = nodes.new(type='GeometryNodeSelfObject')
    info_node = nodes.new(type='GeometryNodeObjectInfo')
    trans_node = nodes.new(type='GeometryNodeTransform')

    info_node.name = 'Self Object Info'

    # Position nodes for clarity
    input_node.location = (-350, 0)
    join_node.location = (140, 0)
    self_node.location = (140, -276)
    info_node.location = (340, -140)
    trans_node.location = (560, 0)
    output_node.location = (760, 0)
    
    # Connect nodes
    links.new(join_node.outputs['Geometry'], trans_node.inputs['Geometry'])
    links.new(trans_node.outputs['Geometry'], output_node.inputs['Geometry'])
    links.new(self_node.outputs['Self Object'], info_node.inputs['Object'])
    links.new(info_node.outputs['Location'], trans_node.inputs['Translation'])
    links.new(info_node.outputs['Rotation'], trans_node.inputs['Rotation'])
    links.new(info_node.outputs['Scale'], trans_node.inputs['Scale'])

    # --- 3. CREATE OBJECT INFO NODES AND LINK THEM ---
    node_y_pos_start = (total_sockets - 1) * 40
    for i in range(total_sockets):
        socket_name = f"Object {i+1:02d}"
        obj_info_node = nodes.new(type='GeometryNodeObjectInfo')
        obj_info_node.location = (-150, node_y_pos_start - (i * 230))
        links.new(input_node.outputs[socket_name], obj_info_node.inputs['Object'])
        links.new(obj_info_node.outputs['Geometry'], join_node.inputs['Geometry'])
        
    return node_group

def create_collection_joiner_group():
    """
    Creates a "CollectionJoiner" node group for instancing up to 8 collections.
    """
    node_group = bpy.data.node_groups.new(name="CollectionJoiner", type='GeometryNodeTree')
    nodes = node_group.nodes
    links = node_group.links
    nodes.clear()

    total_sockets = 6

    # --- 1. DEFINE THE MODIFIER INTERFACE ---
    node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    for i in range(total_sockets):
        socket_name = f"Collection {i+1:02d}"
        node_group.interface.new_socket(name=socket_name, in_out="INPUT", socket_type='NodeSocketCollection')

    # --- 2. CREATE AND ARRANGE THE NODES ---
    input_node = nodes.new(type='NodeGroupInput')
    output_node = nodes.new(type='NodeGroupOutput')
    join_node = nodes.new(type='GeometryNodeJoinGeometry')
    self_node = nodes.new(type='GeometryNodeSelfObject')
    info_node = nodes.new(type='GeometryNodeObjectInfo')
    trans_node = nodes.new(type='GeometryNodeTransform')

    info_node.name = 'Self Object Info'

    input_node.location = (-450, 0)
    join_node.location = (200, 0)
    self_node.location = (140, -276)
    info_node.location = (340, -140)
    trans_node.location = (560, 0)
    output_node.location = (760, 0)

    # --- 3. CREATE INFO NODES AND LINK THEM ---
    node_y_pos_start = (total_sockets - 1) * 80
    for i in range(total_sockets):
        socket_name = f"Collection {i+1:02d}"
        
        y_pos = node_y_pos_start - (i * 200)
        
        collection_info_node = nodes.new(type='GeometryNodeCollectionInfo')
        collection_info_node.location = (-200, y_pos)
        
        realize_instances_node = nodes.new(type='GeometryNodeRealizeInstances')
        realize_instances_node.location = (0, y_pos)
        
        links.new(input_node.outputs[socket_name], collection_info_node.inputs['Collection'])
        links.new(collection_info_node.outputs['Instances'], realize_instances_node.inputs['Geometry'])
        links.new(realize_instances_node.outputs['Geometry'], join_node.inputs['Geometry'])

    links.new(join_node.outputs['Geometry'], trans_node.inputs['Geometry'])
    links.new(trans_node.outputs['Geometry'], output_node.inputs['Geometry'])
    links.new(self_node.outputs['Self Object'], info_node.inputs['Object'])
    links.new(info_node.outputs['Location'], trans_node.inputs['Translation'])
    links.new(info_node.outputs['Rotation'], trans_node.inputs['Rotation'])
    links.new(info_node.outputs['Scale'], trans_node.inputs['Scale'])
    
    return node_group

# Adds modifier to join objects or collections into a new object
class OBJECT_OT_join_modifier(bpy.types.Operator):
    """
    Join selection non-destructively to a new object with a Geo Nodes modifier.
    Can join individual objects or parent collections.
    """
    bl_idname = "object.join_modifier"
    bl_label = "Join with Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    # --- Operator Properties (unchanged) ---
    use_collections: bpy.props.BoolProperty(
        name="Use Parent Collections",
        description="Create a modifier for each parent collection instead of each object",
        default=False
    )
    inherit_name: bpy.props.BoolProperty(name="Inherit Name", default=False)
    name_source: bpy.props.EnumProperty(
        name="Name Source",
        items=[('ACTIVE_OBJECT', "Active Object", "Use active object's name"), ('PARENT_COLLECTION', "Object's Collection", "Use collection name")],
        default='ACTIVE_OBJECT'
    )
    parent_destination: bpy.props.EnumProperty(
        name="Parent To",
        items=[('ACTIVE_COLLECTION', "Active Collection", "Parent to active collection"), ('PARENT_COLLECTION', "Object's Collection", "Parent to object's collection")],
        default='ACTIVE_COLLECTION'
    )
    initial_location: bpy.props.EnumProperty(
        name="Initial Location",
        items=[('CURSOR', "3D Cursor", "Place at 3D Cursor"), ('ACTIVE', "Active Object", "Place at Active Object")],
        default='CURSOR'
    )
    transform_space: bpy.props.EnumProperty(
        name="Transform Space",
        items=[('RELATIVE', "Relative", "Use relative coordinates"), ('ORIGINAL', "Original", "Use world coordinates")],
        default='RELATIVE',
    )

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) >= 1

    def execute(self, context):
        selected_objects = context.selected_objects[:]
        active_obj = context.active_object
        
        # This list will hold all the new objects we create
        new_objects = []

        if self.use_collections:
            # --- 1A. COLLECTION MODE ---
            # Find unique collections from the selection
            unique_collections = {obj.users_collection[0] for obj in selected_objects if obj.users_collection}

            if not unique_collections:
                self.report({'WARNING'}, "Selected objects are not in any collections.")
                return {'CANCELLED'}

            # The collection mode function will now create the objects and return them
            new_objects = self.execute_collection_mode(context, unique_collections, active_obj)
        
        else:
            # --- 1B. OBJECT MODE (Original Logic) ---
            # This logic is fine, as it's intended to create only one object
            
            # --- DETERMINE NAME, PARENT, AND LOCATION FOR THE NEW OBJECT ---
            base_name = "GeoJoiner"
            if self.inherit_name and active_obj:
                if self.name_source == 'ACTIVE_OBJECT':
                    base_name = f"{active_obj.name}_Joiner"
                elif active_obj.users_collection:
                    base_name = active_obj.users_collection[0].name
            final_obj_name = base_name

            target_collection = context.view_layer.active_layer_collection.collection
            if self.parent_destination == 'PARENT_COLLECTION' and active_obj and active_obj.users_collection:
                target_collection = active_obj.users_collection[0]

            if self.initial_location == 'ACTIVE' and active_obj:
                new_obj_location = active_obj.location.copy()
            else:
                new_obj_location = context.scene.cursor.location.copy()

            # --- 2. CREATE THE JOINER OBJECT ---
            mesh = bpy.data.meshes.new(name=f"{final_obj_name}_Mesh")
            joiner_obj = bpy.data.objects.new(final_obj_name, mesh)
            joiner_obj.location = new_obj_location
            target_collection.objects.link(joiner_obj)

            # --- 3. ADD MODIFIERS ---
            # The object mode function will add modifiers and return the object in a list
            new_objects = self.execute_object_mode(context, joiner_obj, selected_objects)
        
        # --- 4. FINALIZE ---
        if not new_objects:
            # Something went wrong, or no collections were found
            return {'CANCELLED'}
            
        bpy.ops.object.select_all(action='DESELECT')
        # Select all the new objects we created
        for obj in new_objects:
            obj.select_set(True)
        
        # Make the last created object the active one
        context.view_layer.objects.active = new_objects[-1]
        
        return {'FINISHED'}

    def execute_object_mode(self, context, joiner_obj, selected_objects):
        # Find or create the node group for joining objects
        node_group_name = "GeoJoiner"
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            self.report({'INFO'}, f"Creating new node group: {node_group_name}")
            node_group = create_geo_joiner_group()
        else:
            self.report({'INFO'}, f"Reusing existing node group: {node_group_name}")

        num_selected = len(selected_objects)
        num_modifiers = max(1, math.ceil(num_selected / 40.0))
        
        all_sockets = [item for panel in node_group.interface.items_tree if panel.item_type == 'PANEL' for item in panel.interface_items]

        for i in range(num_modifiers):
            mod_name = f"GeoJoiner.{i+1:03d}"
            geo_mod = joiner_obj.modifiers.new(name=mod_name, type='NODES')
            geo_mod.node_group = node_group
            
            start_index = i * 40
            end_index = start_index + 40
            object_chunk = selected_objects[start_index:end_index]
            
            for j, obj in enumerate(object_chunk):
                socket_identifier = all_sockets[j].identifier
                geo_mod[socket_identifier] = obj
        
        # Apply final transform settings to the node group
        for node in node_group.nodes:
            if node.type == 'OBJECT_INFO':
                if node.name == 'Self Object Info':
                    inverse_space = [p.identifier for p in node.bl_rna.properties['transform_space'].enum_items if p.identifier != self.transform_space][0]
                    node.transform_space = inverse_space
                else:
                    node.transform_space = self.transform_space

        self.report({'INFO'}, f"Created '{joiner_obj.name}' with {num_modifiers} object modifier(s)")
        
        # Return the created object in a list to match the new execute logic
        return [joiner_obj]

    def execute_collection_mode(self, context, unique_collections, active_obj):
        # Find or create the node group for instancing collections
        node_group_name = "CollectionJoiner"
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            self.report({'INFO'}, f"Creating new node group: {node_group_name}")
            node_group = create_collection_joiner_group()
        else:
            self.report({'INFO'}, f"Reusing existing node group: {node_group_name}")
            
        created_objects = []
        
        # Determine the location once; all new objects will share it
        if self.initial_location == 'ACTIVE' and active_obj:
            new_obj_location = active_obj.location.copy()
        else:
            new_obj_location = context.scene.cursor.location.copy()

        # Loop over each unique collection and create a new object for each
        for coll in unique_collections:
            
            # --- 1. DETERMINE NAME & PARENT FOR THIS OBJECT ---
            base_name = "GeoJoiner"
            if self.inherit_name:
                # Naming logic is modified to make sense for multiple collections
                if self.name_source == 'PARENT_COLLECTION':
                    base_name = f"{coll.name}_Joiner"
                elif self.name_source == 'ACTIVE_OBJECT' and active_obj:
                    base_name = f"{active_obj.name}_{coll.name}_Joiner"
                else:
                    # Fallback to collection name
                    base_name = f"{coll.name}_Joiner"
            final_obj_name = base_name

            target_collection = context.view_layer.active_layer_collection.collection
            if self.parent_destination == 'PARENT_COLLECTION':
                # Parent the new object to the collection it's referencing
                target_collection = coll

            # --- 2. CREATE THE JOINER OBJECT ---
            mesh = bpy.data.meshes.new(name=f"{final_obj_name}_Mesh")
            joiner_obj = bpy.data.objects.new(final_obj_name, mesh)
            joiner_obj.location = new_obj_location
            target_collection.objects.link(joiner_obj)

            # --- 3. ADD THE MODIFIER ---
            mod_name = f"Joiner_{coll.name}"
            mod = joiner_obj.modifiers.new(name=mod_name, type='NODES')
            mod.node_group = node_group
            
            # The collection input is the second item (index 1) in the interface
            # (Index 0 is the Geometry output)
            socket_identifier = node_group.interface.items_tree[1].identifier
            mod[socket_identifier] = coll
            
            # Add the new object to our list
            created_objects.append(joiner_obj)
        
        # Set the transform space on the Collection Info node within the group
        # This only needs to be done once, as it affects the shared node group
        for node in node_group.nodes:
            if node.type == 'COLLECTION_INFO':
                node.transform_space = self.transform_space

        self.report({'INFO'}, f"Created {len(created_objects)} collection joiner object(s)")
        
        # Return the list of all objects created
        return created_objects

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