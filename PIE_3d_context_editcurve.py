# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu


###-----------------------------------------------------------------------------###
###                             CUSTOM OPERATORS                                ###
###-----------------------------------------------------------------------------###

class CURVE_OT_clear_radius(bpy.types.Operator):
    """Reset the radius of selected control points to 1.0"""
    bl_idname = "curve.clear_radius"
    bl_label = "Clear Radius"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.mode == 'EDIT_CURVE' and
                context.active_object.type == 'CURVE')

    def execute(self, context):
        selected_curves = [obj for obj in context.selected_editable_objects if obj.type == 'CURVE']
        points_changed = 0

        if not selected_curves:
            self.report({'WARNING'}, "No curve objects selected in Edit Mode.")
            return {'CANCELLED'}

        for obj in selected_curves:
            curve_data = obj.data
            if curve_data and hasattr(curve_data, 'splines'):
                for spline in curve_data.splines:
                    if spline.type == 'BEZIER':
                        for point in spline.bezier_points:
                            if point.select_control_point or point.select_left_handle or point.select_right_handle:
                                point.radius = 1.0
                                points_changed += 1
                    elif spline.type in ['NURBS', 'POLY']:
                        for point in spline.points:
                            if point.select:
                                point.radius = 1.0
                                points_changed += 1

        if points_changed > 0:
            self.report({'INFO'}, f"Reset radius for {points_changed} selected control point(s).")
        else:
            self.report({'INFO'}, "No control points were selected.")
        return {'FINISHED'}


###-----------------------------------------------------------------------------###
###                          CURVE SUB PIE MENUS                                ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_smoothCurve(Menu):
    bl_label = "Smooth"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("curve.normals_make_consistent")
        # EAST
        pie.operator("curve.smooth")
        # SOUTH
        pie.operator("curve.smooth_radius")
        # NORTH
        pie.operator("curve.smooth_tilt")
        # NORTH-WEST
        pie.operator("curve.smooth_weight")
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_curveDelete(Menu):
    bl_label = "Delete/Clear"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("curve.dissolve_verts")
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("curve.delete", text="Delete Segment").type = 'SEGMENT'
        # NORTH
        pie.operator("curve.tilt_clear")
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.operator("curve.clear_radius")
        # SOUTH-WEST
        pie.operator("curve.delete", text="Delete Vert").type = 'VERT'
        # SOUTH-EAST
        pie.separator()


###-----------------------------------------------------------------------------###
###                              REGISTRY                                       ###
###-----------------------------------------------------------------------------###

registry = [
    CURVE_OT_clear_radius,
    SUBPIE_MT_smoothCurve,
    SUBPIE_MT_curveDelete,
]


###-----------------------------------------------------------------------------###
###                              DRAW FUNCTIONS                                 ###
###-----------------------------------------------------------------------------###

def draw_context_editcurve(pie, context):
    # WEST
    pie.operator("transform.transform", text='Radius').mode = 'CURVE_SHRINKFATTEN'
    # EAST
    pie.operator("wm.call_menu_pie", text='Smooth...').name = "SUBPIE_MT_smoothCurve"
    # SOUTH
    pie.operator("curve.extrude_move")
    # NORTH
    pie.operator("curve.make_segment")
    # NORTH-WEST
    pie.operator("transform.tilt")
    # NORTH-EAST
    pie.operator("curve.subdivide")
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text='Delete/Clear...').name = "SUBPIE_MT_curveDelete"
    # SOUTH-EAST
    pie.operator("curve.separate")
