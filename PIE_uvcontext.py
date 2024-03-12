# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "UV Context Pie: 'Shift + Right Mouse'",
    "description": "UV Context Pie Menu",
    "author": "Bastian L Strube, Frederik Storm",
    "blender": (4, 0, 0),
    "location": "UV Editor",
    "category": "Interface"}

import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)
from bpy.app.translations import contexts as i18n_contexts

# Sub Pie Menu for UV Unwrap
class SUBPIE_MT_uvUnwrap(Menu):
    bl_label = "Unwrap"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("uv.smart_project")
        # EAST
        pie.operator("uv.follow_active_quads")
        # SOUTH
        pie.operator("uv.cylinder_project")
        # NORTH
        pie.operator("uv.unwrap")
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        o = pie.operator('wm.context_toggle', text="Live Unwrap")
        o.data_path = 'tool_settings.use_live_unwrap'
        # SOUTH-WEST
        pie.operator("uv.sphere_project")
        # SOUTH-EAST
        pie.operator("uv.cube_project")

# Reference context menu: IMAGE_MT_uvs_context_menu
class IMAGE_PIE_MT_uvContext(Menu):
    bl_label    = ""

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        
        # WEST
        pie.operator("uv.pin").clear = False
        # EAST
        pie.operator("uv.pin", text='Unpin').clear = True
        # SOUTH
        pie.operator("uv.minimize_stretch")
        # NORTH
        pie.operator("wm.call_menu_pie", text='Unwrap...').name = "SUBPIE_MT_uvUnwrap"
        # NORTH-WEST
        pie.operator("uv.pack_islands")
        # NORTH-EAST
        pie.operator("uv.average_islands_scale")
        # SOUTH-WEST
        pie.operator("mesh.mark_seam", text='Mark Seam').clear = False
        # SOUTH-EAST
        pie.operator("mesh.mark_seam", text='Clear Seam').clear = True

        # Static face menu
        pie.separator()
        pie.separator()

        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8

        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y=1

        dropdown_menu.operator("uv.stitch")
        dropdown_menu.operator("uv.weld")
        dropdown_menu.operator("uv.remove_doubles")


classes = [
    SUBPIE_MT_uvUnwrap,
    IMAGE_PIE_MT_uvContext,
]

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='UV Editor')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "IMAGE_PIE_MT_uvContext"
        addon_keymaps.append((km, kmi))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()