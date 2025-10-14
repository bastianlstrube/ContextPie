import bpy
from mathutils import Vector
import numpy as np # We'll use numpy for min/max on arrays

class OBJECT_OT_add_remesh_modifier_to_selected(bpy.types.Operator):
    bl_idname = "object.add_remesh_modifier_to_selected"
    bl_label = "Add Smart Remesh Modifier (Fast Mesh Data Dimensions)"
    bl_description = "Adds a Remesh modifier to selected mesh objects with voxel size based on the raw mesh data dimensions (no object/parent scale), optimized for large meshes."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected. Please select one or more mesh objects.")
            return {'CANCEL'}

        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh_data = obj.data

                # Check if mesh has vertices
                if not mesh_data.vertices:
                    self.report({'WARNING'}, f"Object '{obj.name}' has no vertices. Skipping.")
                    continue

                # --- Optimized Bounding Box Calculation ---
                # Get vertex coordinates into a numpy array directly
                # Allocate a flat array for the coordinates (x, y, z for each vertex)
                num_vertices = len(mesh_data.vertices)
                coords = np.empty(num_vertices * 3, dtype=np.float32)

                # Efficiently copy all vertex coordinates
                # This uses bpy's internal C-level optimization
                mesh_data.vertices.foreach_get("co", coords)

                # Reshape the flat array into a (N, 3) array for easier manipulation
                coords = coords.reshape(num_vertices, 3)

                # Calculate min and max for each axis using numpy
                min_coords = coords.min(axis=0) # [min_x, min_y, min_z]
                max_coords = coords.max(axis=0) # [max_x, max_y, max_z]

                # Calculate dimensions
                dim_x = max_coords[0] - min_coords[0]
                dim_y = max_coords[1] - min_coords[1]
                dim_z = max_coords[2] - min_coords[2]

                # Find the largest side of the mesh's intrinsic bounding box
                largest_side = max(dim_x, dim_y, dim_z)

                if largest_side == 0:
                    self.report({'WARNING'}, f"Object '{obj.name}' has zero intrinsic mesh dimensions. Cannot apply Remesh modifier.")
                    continue

                voxel_size = largest_side / 40.0

                # Add Remesh Modifier
                remesh_modifier = obj.modifiers.new(name="SmartRemesh", type='REMESH')
                remesh_modifier.mode = 'VOXEL'
                remesh_modifier.voxel_size = voxel_size
                remesh_modifier.use_smooth_shade = True # Often desired with remesh

                self.report({'INFO'}, f"Added Remesh modifier to '{obj.name}' with Voxel Size: {voxel_size:.4f} (based on mesh data)")
            else:
                self.report({'WARNING'}, f"Object '{obj.name}' is not a mesh. Skipping.")

        return {'FINISHED'}

registry = (
    OBJECT_OT_add_remesh_modifier_to_selected,
)