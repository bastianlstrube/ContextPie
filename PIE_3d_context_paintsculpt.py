# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Menu
from bl_ui.properties_paint_common import BrushAssetShelf
from . import PIE_3d_context as _ctx


###-----------------------------------------------------------------------------###
###                          SCULPT BRUSH SUB MENUS                             ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_sculpt_brush_select_contrast(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_contrast"
    bl_label = "Contrast Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _ctx.draw_brush_operator(pie, 'Flatten/Contrast', 'flatten')
        _ctx.draw_brush_operator(pie, 'Scrape/Fill', 'scrape')
        _ctx.draw_brush_operator(pie, 'Fill/Deepen', 'fill')
        _ctx.draw_brush_operator(pie, 'Scrape Multiplane', 'multiplane_scrape')
        pie.separator()
        pie.separator()
        _ctx.draw_brush_operator(pie, 'Smooth', 'smooth')


class SUBPIE_MT_sculpt_brush_select_transform(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_transform"
    bl_label = "Transform Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _ctx.draw_brush_operator(pie, 'Elastic Grab', 'elastic_deform')
        _ctx.draw_brush_operator(pie, 'Nudge', 'nudge')
        _ctx.draw_brush_operator(pie, 'Relax Slide', 'topology')
        _ctx.draw_brush_operator(pie, 'Snake Hook', 'snake_hook')
        _ctx.draw_brush_operator(pie, 'Twist', 'rotate')
        _ctx.draw_brush_operator(pie, 'Pose', 'pose')
        _ctx.draw_brush_operator(pie, 'Pinch/Magnify', 'pinch')
        _ctx.draw_brush_operator(pie, 'Thumb', 'thumb')


class SUBPIE_MT_sculpt_brush_select_volume(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_volume"
    bl_label = "Volume Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _ctx.draw_brush_operator(pie, 'Blob', 'blob')
        _ctx.draw_brush_operator(pie, 'Clay', 'clay')
        _ctx.draw_brush_operator(pie, 'Inflate/Deflate', 'inflate')
        _ctx.draw_brush_operator(pie, 'Draw Sharp', 'draw_sharp')
        _ctx.draw_brush_operator(pie, 'Clay Strips', 'clay_strips')
        _ctx.draw_brush_operator(pie, 'Crease', 'crease')
        _ctx.draw_brush_operator(pie, 'Clay Thumb', 'clay_thumb')
        _ctx.draw_brush_operator(pie, 'Layer', 'layer')


class SUBPIE_MT_sculpt_brush_select_special(Menu):
    bl_idname = "SUBPIE_MT_sculpt_brush_select_special"
    bl_label = "Special Brushes"

    def draw(self, context):
        pie = self.layout.menu_pie()
        _ctx.draw_brush_operator(pie, 'Cloth', 'cloth')
        _ctx.draw_brush_operator(pie, 'Erase Multires Displacement', 'displacement_eraser')
        _ctx.draw_brush_operator(pie, 'Density', 'simplify')
        _ctx.draw_brush_operator(pie, 'Paint', 'paint')
        _ctx.draw_brush_operator(pie, 'Smear', 'smear')
        _ctx.draw_brush_operator(pie, 'Face Set Paint', 'draw_face_sets')
        _ctx.draw_brush_operator(pie, 'Boundary', 'boundary')
        _ctx.draw_brush_operator(pie, 'Smear Multires Displacement', 'displacement_smear')


###-----------------------------------------------------------------------------###
###                      PAINT TEXTURE BRUSH SUB MENUS                          ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_painttex_brush_select_eraser(Menu):
    bl_idname = "SUBPIE_MT_painttex_brush_select_eraser"
    bl_label = "Erasers"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # WEST
        pie.separator()
        # EAST
        _ctx.draw_brush_operator(pie, 'Erase Soft', 'erase')
        # SOUTH
        pie.separator()
        # NORTH
        _ctx.draw_brush_operator(pie, 'Erase Hard Pressure', 'erase')
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        _ctx.draw_brush_operator(pie, 'Erase Hard', 'erase')
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        _ctx.draw_brush_operator(pie, 'Erase Pixel Art', 'erase')


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

    # WEST
    pie.operator('wm.call_menu_pie', text="    Transform Brushes...",
                 icon_value=_ctx.brush_icons.get('snake_hook', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_transform.bl_idname
    # EAST
    pie.operator('wm.call_menu_pie', text="    Volume Brushes...",
                 icon_value=_ctx.brush_icons.get('blob', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_volume.bl_idname

    # SOUTH — brush asset shelf or fallback
    if _ctx.blender_uses_brush_assets():
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

    # NORTH
    _ctx.draw_brush_operator(pie, 'Mask', 'mask')
    # NORTH-WEST
    _ctx.draw_brush_operator(pie, 'Grab', 'grab')
    # NORTH-EAST
    _ctx.draw_brush_operator(pie, 'Draw', 'draw')
    # SOUTH-WEST
    pie.operator('wm.call_menu_pie', text="    Contrast Brushes...",
                 icon_value=_ctx.brush_icons.get('flatten', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_contrast.bl_idname
    # SOUTH-EAST
    pie.operator('wm.call_menu_pie', text="    Special Brushes...",
                 icon_value=_ctx.brush_icons.get('draw_face_sets', 0),
                 ).name = SUBPIE_MT_sculpt_brush_select_special.bl_idname


def draw_context_paint_vertex(pie, context):
    pie.scale_y = 1.2

    # WEST
    _ctx.draw_brush_operator(pie, 'Paint Hard', 'paint hard')
    # EAST
    _ctx.draw_brush_operator(pie, 'Paint Soft', 'paint soft')
    # SOUTH
    pie.separator()
    # NORTH
    pie.separator()
    # NORTH-WEST
    pie.separator()
    # NORTH-EAST
    pie.separator()
    # SOUTH-WEST
    _ctx.draw_brush_operator(pie, 'Paint Hard Pressure', 'paint hard pressure')
    # SOUTH-EAST
    pie.separator()


def draw_context_paint_texture(pie, context):
    pie.scale_y = 1.2

    # WEST
    _ctx.draw_brush_operator(pie, 'Paint Soft', 'paint')
    # EAST
    _ctx.draw_brush_operator(pie, 'Paint Hard', 'paint')

    # SOUTH — brush asset shelf or fallback
    if _ctx.blender_uses_brush_assets():
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

    # NORTH
    _ctx.draw_brush_operator(pie, 'Mask', 'mask')
    # NORTH-WEST
    _ctx.draw_brush_operator(pie, 'Airbrush', 'paint')
    # NORTH-EAST
    pie.operator("wm.call_menu_pie", text='Erasers...').name = "SUBPIE_MT_painttex_brush_select_eraser"
    # SOUTH-WEST
    _ctx.draw_brush_operator(pie, 'Fill', 'fill')
    # SOUTH-EAST
    _ctx.draw_brush_operator(pie, 'Clone', '')
