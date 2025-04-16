# Import the Blender Python module
import bpy

# A function to add the operator to a menu (optional)
# This example adds it to the 3D Viewport's "View" menu
def menu_func(self, context):
    layout = self.layout
    pie = layout.menu_pie()
    view = context.space_data
    pie.prop(view.overlay, "show_wireframes", text="Overlay Wireframe", icon='MESH_GRID')
    pie.prop(view.overlay, "show_face_orientation", icon='FACE_MAPS')

# List of classes to register
registry = ()

# Function to register the operator and add the menu item
def register():
    # Add the menu item to the VIEW3D_MT_view menu
    bpy.types.VIEW3D_MT_shading_ex_pie.append(menu_func)

# Function to unregister the operator and remove the menu item
def unregister():
    # Remove the menu item first
    bpy.types.VIEW3D_MT_view.remove(menu_func)


# --- Script Execution ---

# This allows the script to be run directly in Blender's Text Editor
# to test the registration.
if __name__ == "__main__":
    # Attempt to unregister first in case the script was run before
    try:
        unregister()
    except Exception:
        pass
    # Register the operator
    register()

    # You can optionally print a confirmation message to the system console
    # print(f"Operator '{VIEW3D_OT_toggle_face_orientation.bl_idname}' registered.")
