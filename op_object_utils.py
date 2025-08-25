# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

# Join selected objects non-destructively to a object with geo nodes
class OBJECT_OT_compound_object(bpy.types.Operator):
    """
    Joins selected objects with a non-destructive Geo Nodes modifier.
    Exposes object inputs and provides options for location and transform space.
    """
    bl_idname = "object.compound_object"
    bl_label = "Compound Object"
    bl_options = {'REGISTER', 'UNDO'}

    # --- NEW PROPERTY FOR INITIAL LOCATION ---
    initial_location: bpy.props.EnumProperty(
        name="Initial Location",
        description="Where to place the newly created object",
        items=[
            ('CURSOR', "3D Cursor", "Place the new object at the 3D Cursor"),
            ('ACTIVE', "Active Object", "Place the new object at the active object's location")
        ],
        default='CURSOR'
    )
    
    # Property for the transform space
    transform_space: bpy.props.EnumProperty(
        name="Transform Space",
        description="Choose how object coordinates are imported",
        items=[
            ('RELATIVE', "Relative", "Import geometry relative to the modifier object's transform"),
            ('ORIGINAL', "Original", "Import geometry in its original world space location")
        ],
        default='RELATIVE'
    )

    @classmethod
    def poll(cls, context):
        # Operator can run if at least one object is selected
        return len(context.selected_objects) >= 1

    def execute(self, context):
        selected_objects = context.selected_objects[:]
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected to join.")
            return {'CANCELLED'}
            
        # --- USE THE NEW PROPERTY TO DETERMINE LOCATION ---
        if self.initial_location == 'CURSOR':
            new_obj_location = context.scene.cursor.location.copy()
        else:  # 'ACTIVE'
            active_obj = context.active_object
            if active_obj:
                new_obj_location = active_obj.location.copy()
            else:
                # Fallback in case there is no active object
                self.report({'WARNING'}, "No active object; defaulting to 3D Cursor location")
                new_obj_location = context.scene.cursor.location.copy()

        # Create the new object that will host the modifier
        mesh = bpy.data.meshes.new(name="GeoJoinerMesh")
        joiner_obj = bpy.data.objects.new("GeoJoiner", mesh)
        joiner_obj.location = new_obj_location
        context.collection.objects.link(joiner_obj)

        # Add and configure the Geometry Nodes modifier
        geo_mod = joiner_obj.modifiers.new(name="GeoJoiner", type='NODES')
        node_group = bpy.data.node_groups.new(name=f"{joiner_obj.name} Nodes", type='GeometryNodeTree')
        geo_mod.node_group = node_group
        
        nodes = node_group.nodes
        links = node_group.links
        nodes.clear()

        # Create core nodes and position them
        input_node = nodes.new(type='NodeGroupInput')
        output_node = nodes.new(type='NodeGroupOutput')
        join_node = nodes.new(type='GeometryNodeJoinGeometry')
        
        input_node.location = (-400, 0)
        join_node.location = (0, 0)
        output_node.location = (400, 0)

        # Declare the 'Geometry' output socket for the node group
        node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        links.new(join_node.outputs['Geometry'], output_node.inputs['Geometry'])

        # Create interface inputs and corresponding nodes
        objects_to_add = selected_objects + [None] * 4
        node_y_pos_start = (len(objects_to_add) - 1) * 120

        for i, obj in enumerate(objects_to_add):
            socket_name = f"Object {i+1}"
            node_group.interface.new_socket(name=socket_name, in_out="INPUT", socket_type='NodeSocketObject')
            
            if obj:
                socket_identifier = node_group.interface.items_tree[-1].identifier
                geo_mod[socket_identifier] = obj

            obj_info_node = nodes.new(type='GeometryNodeObjectInfo')
            obj_info_node.location = (-50, node_y_pos_start - (i * 260))
            obj_info_node.transform_space = self.transform_space 
            
            links.new(input_node.outputs[socket_name], obj_info_node.inputs['Object'])
            links.new(obj_info_node.outputs['Geometry'], join_node.inputs['Geometry'])

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
    OBJECT_OT_compound_object,
    OBJECT_OT_edit_display_type,
    OBJECT_OT_edit_obj_color,
    OBJECT_OT_add_pie_boolean,
]
