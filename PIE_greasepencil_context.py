# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import bpy
from bpy.types import Menu
from bl_ui.properties_paint_common import BrushAssetShelf


###-----------------------------------------------------------------------------###
###                     GREASE PENCIL SUB PIE MENUS                             ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_gp_paint_brush_select_eraser(Menu):
    bl_idname = "SUBPIE_MT_gp_paint_brush_select_eraser"
    bl_label = "Erasers"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # WEST
        pie.separator()
        # EAST
        draw_gp_brush_op(pie, 'Eraser Soft')
        # SOUTH
        pie.separator()
        # NORTH
        draw_gp_brush_op(pie, 'Eraser Stroke')
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        draw_gp_brush_op(pie, 'Eraser Hard')
        # SOUTH-WEST / SOUTH-EAST
        pie.separator()
        pie.separator()


class SUBPIE_MT_gp_edit_delete(Menu):
    bl_idname = "SUBPIE_MT_gp_edit_delete"
    bl_label = "Delete / Dissolve"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        # WEST
        pie.operator("grease_pencil.dissolve", text="Dissolve Points").type = 'POINTS'
        # EAST
        pie.operator("grease_pencil.dissolve", text="Dissolve Between").type = 'BETWEEN'
        # SOUTH
        pie.operator("grease_pencil.delete", text="Delete Only Fills").mode = 'FILLS'
        # NORTH
        pie.operator("grease_pencil.delete", text="Delete All").mode = 'ALL'
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("grease_pencil.delete", text="Delete Only Strokes").mode = 'STROKES'
        # SOUTH-EAST
        pie.separator()


class VIEW3D_PIE_MT_gp_context(Menu):
    bl_idname = "PIE_MT_gp_context_pie"
    bl_label = "Grease Pencil Context Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()
        draw_gp_context_pie(pie, context)


###-----------------------------------------------------------------------------###
###          MODULE-LEVEL DRAW FUNCTIONS — called from main context pie         ###
###-----------------------------------------------------------------------------###

def draw_gp_context_pie(pie, context):
    mode_actions = {
        'PAINT_GREASE_PENCIL': draw_paint_gp,
        'PAINT_GPENCIL': draw_paint_gp,
        'SCULPT_GREASE_PENCIL': draw_sculpt_gp,
        'SCULPT_GPENCIL': draw_sculpt_gp,
        'EDIT_GREASE_PENCIL': draw_edit_gp,
        'EDIT_GPENCIL': draw_edit_gp,
    }
    if context.mode in mode_actions:
        mode_actions[context.mode](pie, context)


def draw_paint_gp(pie, context):
    pie.scale_y = 1.2
    # WEST
    draw_gp_brush_op(pie, 'Pencil')
    # EAST
    draw_gp_brush_op(pie, 'Ink Pen')
    # SOUTH
    if 'asset_activate' in dir(bpy.ops.brush):
        brush = context.tool_settings.gpencil_paint.brush
        col = pie.column()
        row = col.row()
        row.scale_y, row.scale_x = 0.75, 0.15
        BrushAssetShelf.draw_popup_selector(row, context, brush, show_name=False)
        if brush:
            col.row().box().label(text=brush.name)
    else:
        pie.separator()
    # NORTH
    draw_gp_brush_op(pie, 'Marker')
    # NORTH-WEST
    draw_gp_brush_op(pie, 'Chisel')
    # NORTH-EAST
    pie.operator("wm.call_menu_pie", text='Erasers...').name = "SUBPIE_MT_gp_paint_brush_select_eraser"
    # SOUTH-WEST
    draw_gp_brush_op(pie, 'Fill')
    # SOUTH-EAST
    draw_gp_brush_op(pie, 'Airbrush')


def draw_sculpt_gp(pie, context):
    pie.scale_y = 1.2
    # WEST
    draw_gp_brush_op(pie, 'Smooth')
    # EAST
    draw_gp_brush_op(pie, 'Thickness')
    # SOUTH
    pie.separator()
    # NORTH
    draw_gp_brush_op(pie, 'Grab')
    # NORTH-WEST
    draw_gp_brush_op(pie, 'Push')
    # NORTH-EAST
    draw_gp_brush_op(pie, 'Pinch')
    # SOUTH-WEST
    draw_gp_brush_op(pie, 'Strength')
    # SOUTH-EAST
    draw_gp_brush_op(pie, 'Twist')


def draw_edit_gp(pie, context):
    # gpencil_selectmode_edit is GPv3; fall back to gpencil_selectmode for GPv2
    select_mode = getattr(context.tool_settings, 'gpencil_selectmode_edit',
                  getattr(context.tool_settings, 'gpencil_selectmode', 'POINT'))
    if select_mode == 'POINT':
        draw_edit_gp_point(pie, context)
    elif select_mode == 'SEGMENT':
        draw_edit_gp_segment(pie, context)
    elif select_mode == 'STROKE':
        draw_edit_gp_stroke(pie, context)


def draw_edit_gp_point(pie, context):
    # WEST
    pie.operator("grease_pencil.duplicate", text="Duplicate")
    # EAST
    pie.operator("grease_pencil.stroke_smooth", text="Smooth Points")
    # SOUTH
    pie.operator("grease_pencil.extrude_move", text="Extrude Points")
    # NORTH
    pie.operator("grease_pencil.join_selection", text="Join Points/Strokes")
    # NORTH-WEST
    pie.operator("grease_pencil.subdivide", text="Subdivide")
    # NORTH-EAST
    pie.operator("grease_pencil.clean_loose", text="Clean Loose")
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text='Delete/Dissolve...').name = "SUBPIE_MT_gp_edit_delete"
    # SOUTH-EAST
    pie.operator("grease_pencil.separate", text="Separate")


def draw_edit_gp_segment(pie, context):
    # WEST
    pie.operator("grease_pencil.duplicate", text="Duplicate")
    # EAST
    pie.operator("grease_pencil.stroke_smooth", text="Smooth Segment")
    # SOUTH
    pie.operator("grease_pencil.extrude_move", text="Extrude")
    # NORTH
    pie.operator("grease_pencil.join_selection", text="Join Strokes")
    # NORTH-WEST
    pie.operator("grease_pencil.subdivide", text="Subdivide")
    # NORTH-EAST
    pie.operator("grease_pencil.clean_loose", text="Clean Loose")
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text='Delete/Dissolve...').name = "SUBPIE_MT_gp_edit_delete"
    # SOUTH-EAST
    pie.operator("grease_pencil.separate", text="Separate")


def draw_edit_gp_stroke(pie, context):
    # WEST
    pie.operator("grease_pencil.stroke_switch_direction", text="Switch Direction")
    # EAST
    pie.operator("grease_pencil.stroke_smooth", text="Smooth Strokes")
    # SOUTH
    pie.separator()
    # NORTH
    pie.operator("grease_pencil.join_selection", text="Join Strokes")
    # NORTH-WEST
    pie.operator("grease_pencil.stroke_simplify", text="Simplify Stroke")
    # NORTH-EAST
    pie.operator("grease_pencil.clean_loose", text="Clean Loose")
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text='Delete/Dissolve...').name = "SUBPIE_MT_gp_edit_delete"
    # SOUTH-EAST
    pie.operator("grease_pencil.separate", text="Separate")


def draw_gp_brush_op(layout, brush_name: str):
    """Activate a GPv3 brush asset from the essentials library."""
    if 'asset_activate' in dir(bpy.ops.brush):
        op = layout.operator('brush.asset_activate', text="     " + brush_name)
        op.asset_library_type = 'ESSENTIALS'
        sub_folder = ("essentials_brushes-gp_sculpt.blend" if "SCULPT" in bpy.context.mode
                      else "essentials_brushes-gp_draw.blend")
        op.relative_asset_identifier = os.path.join("brushes", sub_folder, "Brush", brush_name)
    else:
        layout.separator()


registry = [
    SUBPIE_MT_gp_paint_brush_select_eraser,
    SUBPIE_MT_gp_edit_delete,
    VIEW3D_PIE_MT_gp_context,
]
