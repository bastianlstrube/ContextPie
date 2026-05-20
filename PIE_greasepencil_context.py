# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path
import bpy
from bpy.types import Menu
from bl_ui.properties_paint_common import BrushAssetShelf

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


'''
The Elegant Fix: Centralized Routing

Instead of having your regular files and your Grease Pencil files constantly fighting over who owns the hotkey, let the regular menus own the hotkeys exclusively.

You treat your main menus (VIEW3D_PIE_MT_context, VIEW3D_PIE_MT_mode, and VIEW3D_PIE_MT_pivots) as traffic controllers:

    Remove hotkey registration from the GP files entirely: Clean out the register() loops from your new Grease Pencil scripts so they aren't trying to inject duplicate hotkeys into the same keymap space.

    Turn your main menus into switchboards: Inside the draw() method of your main menus, right at the very top before it evaluates anything else, look at the active object type or mode (e.g., checking if context.object.type == 'GREASEPENCIL').

    Redirect the drawing layout: If Blender detects that a Grease Pencil object is active, instead of running its own drawing logic, you instruct the main menu to instantly hand over the reins to your new GP menus using a simple menu redirect line.

Why this works beautifully

    Zero Keymap Bloat: Your addon configuration remains incredibly clean. You only register a single master shortcut for Context, Mode, and Pivots across the entire 3D Viewport.

    Bulletproof Priorities: Because there is only one hotkey listener, there is absolutely zero ambiguity for Blender's input system.

    Maintain File Separation: You still get to keep your code perfectly organized. The main file just needs to import the GP menus and point to them dynamically when the context is right.
'''


###-----------------------------------------------------------------------------###
###                     GREASE PENCIL SUB PIE MENUS                        ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_gp_paint_brush_select_eraser(Menu):
    bl_idname = "SUBPIE_MT_gp_paint_brush_select_eraser"
    bl_label = "Erasers"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # WEST / EAST
        pie.separator()
        draw_gp_brush_op(pie, 'Eraser Soft')
        # SOUTH / NORTH
        pie.separator()
        draw_gp_brush_op(pie, 'Eraser Stroke')
        # NW / NE
        pie.separator()
        draw_gp_brush_op(pie, 'Eraser Hard')
        # SW / SE
        pie.separator()
        pie.separator()

class SUBPIE_MT_gp_edit_delete(Menu):
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
        # SOUTH-WEST (Directionally consistent delete)
        pie.operator("grease_pencil.delete", text="Delete Only Strokes").mode = 'STROKES'
        # SOUTH-EAST
        pie.separator()

###-----------------------------------------------------------------------------###
###                          MAIN CONTEXT PIE MENU                              ###
###-----------------------------------------------------------------------------###

class VIEW3D_PIE_MT_gp_context(Menu):
    bl_idname = "PIE_MT_gp_context_pie"
    bl_label = "Grease Pencil Context Pie"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        mode_actions = {
            'PAINT_GREASE_PENCIL': self.draw_paint_gp,
            'PAINT_GPENCIL': self.draw_paint_gp,
            'SCULPT_GREASE_PENCIL': self.draw_sculpt_gp,
            'SCULPT_GPENCIL': self.draw_sculpt_gp,
            'EDIT_GREASE_PENCIL': self.draw_edit_gp,
            'EDIT_GPENCIL': self.draw_edit_gp,
        }

        if context.mode in mode_actions:
            mode_actions[context.mode](pie, context)

    def draw_paint_gp(self, pie, context):
        pie.scale_y = 1.2
        # WEST / EAST
        draw_gp_brush_op(pie, 'Pencil')
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
        # NORTH / NORTH-WEST
        draw_gp_brush_op(pie, 'Marker')
        draw_gp_brush_op(pie, 'Chisel')
        # NORTH-EAST
        pie.operator("wm.call_menu_pie", text='Erasers...').name = "SUBPIE_MT_gp_paint_brush_select_eraser"
        # SOUTH-WEST / SOUTH-EAST
        draw_gp_brush_op(pie, 'Fill')
        draw_gp_brush_op(pie, 'Airbrush')

    def draw_sculpt_gp(self, pie, context):
        pie.scale_y = 1.2
        # WEST / EAST
        draw_gp_brush_op(pie, 'Smooth')
        draw_gp_brush_op(pie, 'Thickness')
        # SOUTH
        pie.separator()
        # NORTH / NORTH-WEST
        draw_gp_brush_op(pie, 'Grab')
        draw_gp_brush_op(pie, 'Push')
        # NORTH-EAST
        draw_gp_brush_op(pie, 'Pinch')
        # SOUTH-WEST / SOUTH-EAST
        draw_gp_brush_op(pie, 'Strength')
        draw_gp_brush_op(pie, 'Twist')

    def draw_edit_gp(self, pie, context):
        select_mode = getattr(context.tool_settings, "gpencil_selectmode", 'POINT')

        if select_mode == 'POINT':
            self.draw_edit_gp_point(pie, context)
        elif select_mode == 'SEGMENT':
            self.draw_edit_gp_segment(pie, context)
        elif select_mode == 'STROKE':
            self.draw_edit_gp_stroke(pie, context)

    def draw_edit_gp_point(self, pie, context):
        # WEST / EAST
        pie.operator("grease_pencil.duplicate", text="Duplicate")
        pie.operator("grease_pencil.stroke_smooth", text="Smooth Points")
        # SOUTH / NORTH
        pie.operator("grease_pencil.extrude_move", text="Extrude Points")
        pie.operator("grease_pencil.join_selection", text="Join Points/Strokes")
        # NORTH-WEST / NORTH-EAST
        pie.operator("grease_pencil.subdivide", text="Subdivide")
        pie.operator("grease_pencil.clean_loose", text="Clean Loose")
        # SOUTH-WEST (Strictly structural delete slot)
        pie.operator("wm.call_menu_pie", text='Delete/Dissolve...').name = "SUBPIE_MT_gp_edit_delete"
        # SOUTH-EAST
        pie.operator("grease_pencil.separate", text="Separate")

    def draw_edit_gp_segment(self, pie, context):
        # WEST / EAST
        pie.operator("grease_pencil.duplicate", text="Duplicate")
        pie.operator("grease_pencil.stroke_smooth", text="Smooth Segment")
        # SOUTH / NORTH
        pie.operator("grease_pencil.extrude_move", text="Extrude")
        pie.operator("grease_pencil.join_selection", text="Join Strokes")
        # NORTH-WEST / NORTH-EAST
        pie.operator("grease_pencil.subdivide", text="Subdivide")
        pie.operator("grease_pencil.clean_loose", text="Clean Loose")
        # SOUTH-WEST 
        pie.operator("wm.call_menu_pie", text='Delete/Dissolve...').name = "SUBPIE_MT_gp_edit_delete"
        # SOUTH-EAST
        pie.operator("grease_pencil.separate", text="Separate")

    def draw_edit_gp_stroke(self, pie, context):
        # WEST / EAST
        pie.operator("grease_pencil.stroke_switch_direction", text="Switch Direction")
        pie.operator("grease_pencil.stroke_smooth", text="Smooth Strokes")
        # SOUTH / NORTH
        pie.separator()
        pie.operator("grease_pencil.join_selection", text="Join Strokes")
        # NORTH-WEST / NORTH-EAST
        pie.operator("grease_pencil.stroke_simplify", text="Simplify Stroke")
        pie.operator("grease_pencil.clean_loose", text="Clean Loose")
        # SOUTH-WEST
        pie.operator("wm.call_menu_pie", text='Delete/Dissolve...').name = "SUBPIE_MT_gp_edit_delete"
        # SOUTH-EAST
        pie.operator("grease_pencil.separate", text="Separate")


def draw_gp_brush_op(layout, brush_name: str):
    """Activates modern GPv3 brush assets using the core library identifier."""
    if 'asset_activate' in dir(bpy.ops.brush):
        op = layout.operator('brush.asset_activate', text="     " + brush_name)
        op.asset_library_type = 'ESSENTIALS'
        sub_folder = "essentials_brushes-gp_sculpt.blend" if "SCULPT" in bpy.context.mode else "essentials_brushes-gp_draw.blend"
        op.relative_asset_identifier = os.path.join("brushes", sub_folder, "Brush", brush_name)
    else:
        layout.separator()

registry = [
    SUBPIE_MT_gp_paint_brush_select_eraser,
    SUBPIE_MT_gp_edit_delete,
    VIEW3D_PIE_MT_gp_context,
]

def register():
    for km in ("Grease Pencil Paint Mode", "Grease Pencil Sculpt Mode", "Grease Pencil Edit Mode", "Grease Pencil Stroke Paint Mode"):
        try:
            WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
                pie_name=VIEW3D_PIE_MT_gp_context.bl_idname,
                hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': True},
                keymap_name=km,
                on_drag=False,
            )
        except Exception:
            pass