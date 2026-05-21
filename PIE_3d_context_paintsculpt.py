# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path
import bpy
from bpy.types import Menu
from bl_ui.properties_paint_common import BrushAssetShelf

# Look Ma, no circular imports!

###-----------------------------------------------------------------------------###
###                          BRUSH & ICON UTILITIES                             ###
###-----------------------------------------------------------------------------###

brush_icons = {}

def blender_uses_brush_assets():
    return 'asset_activate' in dir(bpy.ops.brush)


def draw_brush_operator(layout, brush_name: str, brush_icon: str = ""):
    """Draw a brush select operator with pre-4.3 icon support."""
    if blender_uses_brush_assets():
        op = layout.operator('brush.asset_activate', text="     " + brush_name,
                             icon_value=brush_icons.get(brush_icon, 0))
        op.asset_library_type = 'ESSENTIALS'
        if bpy.context.mode == 'SCULPT':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_sculpt.blend", "Brush", brush_name)
        elif bpy.context.mode == 'PAINT_VERTEX':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_vertex.blend", "Brush", brush_name)
        elif bpy.context.mode == 'PAINT_TEXTURE':
            op.relative_asset_identifier = os.path.join(
                "brushes", "essentials_brushes-mesh_texture.blend", "Brush", brush_name)
    else:
        if brush_icon:
            op = layout.operator("paint.brush_select", text="     " + brush_name,
                                 icon_value=brush_icons.get(brush_icon, 0))
            op.sculpt_tool = brush_icon.upper()
        else:
            layout.separator()


def create_icons():
    global brush_icons
    # Point directly to the parent folder's icon stash
    icons_directory = Path(__file__).parent / "icons"
    if not icons_directory.exists():
        return
    for icon_path in icons_directory.iterdir():
        if icon_path.is_file():
            icon_value = bpy.app.icons.new_triangles_from_file(icon_path.as_posix())
            brush_name = icon_path.stem.split(".")[-1]
            brush_icons[brush_name] = icon_value


def release_icons():
    global brush_icons
    for value in brush_icons.values():
        bpy.app.icons.release(value)
    brush_icons = {}


###-----------------------------------------------------------------------------###
###                          SCULPT BRUSH SUB MENUS                             ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_sculpt_brush_select_contrast(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_contrast"
    bl_label = "Contrast Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Flatten/Contrast', 'flatten')
        draw_brush_operator(pie, 'Scrape/Fill', 'scrape')
        draw_brush_operator(pie, 'Fill/Deepen', 'fill')
        draw_brush_operator(pie, 'Scrape Multiplane', 'multiplane_scrape')
        pie.separator()
        pie.separator()
        draw_brush_operator(pie, 'Smooth', 'smooth')


class SUBPIE_MT_sculpt_brush_select_transform(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_transform"
    bl_label = "Transform Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Elastic Grab', 'elastic_deform')
        draw_brush_operator(pie, 'Nudge', 'nudge')
        draw_brush_operator(pie, 'Relax Slide', 'topology')
        draw_brush_operator(pie, 'Snake Hook', 'snake_hook')
        draw_brush_operator(pie, 'Twist', 'rotate')
        draw_brush_operator(pie, 'Pose', 'pose')
        draw_brush_operator(pie, 'Pinch/Magnify', 'pinch')
        draw_brush_operator(pie, 'Thumb', 'thumb')


class SUBPIE_MT_sculpt_brush_select_volume(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_volume"
    bl_label = "Volume Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Blob', 'blob')
        draw_brush_operator(pie, 'Clay', 'clay')
        draw_brush_operator(pie, 'Inflate/Deflate', 'inflate')
        draw_brush_operator(pie, 'Draw Sharp', 'draw_sharp')
        draw_brush_operator(pie, 'Clay Strips', 'clay_strips')
        draw_brush_operator(pie, 'Crease', 'crease')
        draw_brush_operator(pie, 'Clay Thumb', 'clay_thumb')
        draw_brush_operator(pie, 'Layer', 'layer')


class SUBPIE_MT_sculpt_brush_select_special(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_special"
    bl_label = "Special Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        draw_brush_operator(pie, 'Cloth', 'cloth')
        draw_brush_operator(pie, 'Erase Multires Displacement', 'displacement_eraser')
        draw_brush_operator(pie, 'Density', 'simplify')
        draw_brush_operator(pie, 'Paint', 'paint')
        draw_brush_operator(pie, 'Smear', 'smear')
        draw_brush_operator(pie, 'Face Set Paint', 'draw_face_sets')
        draw_brush_operator(pie, 'Boundary', 'boundary')
        draw_brush_operator(pie, 'Smear Multires Displacement', 'displacement_smear')


###-----------------------------------------------------------------------------###
###                      PAINT TEXTURE BRUSH SUB MENUS                          ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_painttex_brush_select_eraser(Menu):
    bl_idname = "SUBPIE_MT_painttex_brush_select_eraser"
    bl_label = "Erasers"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.separator()
        draw_brush_operator(pie, 'Erase Soft', 'erase')
        pie.separator()
        draw_brush_operator(pie, 'Erase Hard Pressure', 'erase')
        pie.separator()
        draw_brush_operator(pie, 'Erase Hard', 'erase')
        pie.separator()
        draw_brush_operator(pie, 'Erase Pixel Art', 'erase')


###-----------------------------------------------------------------------------###
###                              REGISTRY                                       ###
###-----------------------------------------------------------------------------###

registry = [
    SUBPIE_MT_sculpt_brush_select_contrast,
    SUBPIE_MT_sculpt_brush_select_transform,
    SUBPIE_MT_sculpt_brush_select_volume,
    SUBPIE_MT_sculpt_brush_select_special,
    SUBPIE_MT_painttex_brush_select_eraser,
]


###-----------------------------------------------------------------------------###
###                              DRAW FUNCTIONS                                 ###
###-----------------------------------------------------------------------------###

def draw_context_sculpt(pie, context):
    pie.scale_y = 1.2

    pie.operator('wm.call_menu_pie', text="    Transform Brushes...",
                 icon_value=brush_icons.get('snake_hook', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_transform.bl_idname
    
    pie.operator('wm.call_menu_pie', text="    Volume Brushes...",
                 icon_value=brush_icons.get('blob', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_volume.bl_idname

    if blender_uses_brush_assets():
        sculpt_settings = context.tool_settings.sculpt
        brush = sculpt_settings.brush
        col = pie.column()
        brush_row = col.row()
        brush_row.scale_y = 0.75
        brush_row.scale_x = 0.15
        BrushAssetShelf.draw_popup_selector(brush_row, context, brush, show_name=False)
        name_row = col.row().box()
        if brush:
            name_row.label(text=brush.name)
    else:
        pie.separator()

    draw_brush_operator(pie, 'Mask', 'mask')
    draw_brush_operator(pie, 'Grab', 'grab')
    draw_brush_operator(pie, 'Draw', 'draw')
    
    pie.operator('wm.call_menu_pie', text="    Contrast Brushes...",
                 icon_value=brush_icons.get('flatten', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_contrast.bl_idname
    
    pie.operator('wm.call_menu_pie', text="    Special Brushes...",
                 icon_value=brush_icons.get('draw_face_sets', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_special.bl_idname


def draw_context_paint_vertex(pie, context):
    pie.scale_y = 1.2
    draw_brush_operator(pie, 'Paint Hard', 'paint hard')
    draw_brush_operator(pie, 'Paint Soft', 'paint soft')
    pie.separator()
    pie.separator()
    pie.separator()
    pie.separator()
    draw_brush_operator(pie, 'Paint Hard Pressure', 'paint hard pressure')
    pie.separator()


def draw_context_paint_texture(pie, context):
    pie.scale_y = 1.2
    draw_brush_operator(pie, 'Paint Soft', 'paint')
    draw_brush_operator(pie, 'Paint Hard', 'paint')

    if blender_uses_brush_assets():
        paint_settings = context.tool_settings.image_paint
        brush = paint_settings.brush
        col = pie.column()
        brush_row = col.row()
        brush_row.scale_y = 0.75
        brush_row.scale_x = 0.15
        BrushAssetShelf.draw_popup_selector(brush_row, context, brush, show_name=False)
        name_row = col.row().box()
        if brush:
            name_row.label(text=brush.name)
    else:
        pie.separator()

    draw_brush_operator(pie, 'Mask', 'mask')
    draw_brush_operator(pie, 'Airbrush', 'paint')
    pie.operator("wm.call_menu_pie", text='Erasers...').name = "SUBPIE_MT_painttex_brush_select_eraser"
    draw_brush_operator(pie, 'Fill', 'fill')
    draw_brush_operator(pie, 'Clone', '')