# Import the Blender Python module
import bpy

# A function to add the operator to a menu (optional)
# This adds it to the 3D Viewport's "Shading" menu
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
    bpy.types.VIEW3D_MT_shading_ex_pie.remove(menu_func)
