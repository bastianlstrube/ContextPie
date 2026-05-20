# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu


###-----------------------------------------------------------------------------###
###                          POSE MODE SUB MENUS                                ###
###-----------------------------------------------------------------------------###

class SUBPIE_MT_inbetweens(Menu):
    bl_label = "Inbetweens"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("pose.push_rest")
        # EAST
        pie.operator("pose.relax_rest")
        # SOUTH
        pie.operator("pose.blend_to_neighbor")
        # NORTH
        pie.operator("pose.breakdown")
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.operator("pose.push")
        # SOUTH-EAST
        pie.operator("pose.relax")


class SUBPIE_MT_propagate(Menu):
    bl_label = "Propagate"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.operator("pose.propagate", text="Selected Markers").mode = 'SELECTED_MARKERS'
        # EAST
        pie.operator("pose.propagate", text="Selected Keys").mode = 'SELECTED_KEYS'
        # SOUTH
        pie.operator("pose.propagate", text="Last Key").mode = 'LAST_KEY'
        # NORTH
        pie.operator("pose.propagate", text="Next Key").mode = 'NEXT_KEY'
        # NORTH-WEST
        pie.operator("pose.propagate", text="Before Frame").mode = 'BEFORE_FRAME'
        # NORTH-EAST
        pie.operator("pose.propagate", text="Before End").mode = 'BEFORE_END'
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_constraints(Menu):
    bl_label = "Constraints"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.separator()
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("pose.constraints_clear", text="Clear Constraints")
        # NORTH
        pie.operator("pose.constraint_add_with_targets", text="Constraint with targets")
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_ik(Menu):
    bl_label = "IK"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.separator()
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("pose.ik_clear", text="Clear IK")
        # NORTH
        pie.operator("pose.ik_add", text="Add IK")
        # NORTH-WEST
        pie.separator()
        # NORTH-EAST
        pie.separator()
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


class SUBPIE_MT_motionpaths(Menu):
    bl_label = "Motion Paths"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        # WEST
        pie.separator()
        # EAST
        pie.separator()
        # SOUTH
        pie.operator("pose.paths_clear")
        # NORTH
        calc = pie.operator("pose.paths_calculate")
        calc.start_frame = context.scene.frame_start
        calc.end_frame = context.scene.frame_end
        calc.bake_location = 'HEADS'
        # NORTH-WEST
        pie.operator("pose.paths_update_visible")
        # NORTH-EAST
        pie.operator("pose.paths_update")
        # SOUTH-WEST
        pie.separator()
        # SOUTH-EAST
        pie.separator()


###-----------------------------------------------------------------------------###
###                              REGISTRY                                       ###
###-----------------------------------------------------------------------------###

registry = [
    SUBPIE_MT_inbetweens,
    SUBPIE_MT_propagate,
    SUBPIE_MT_constraints,
    SUBPIE_MT_ik,
    SUBPIE_MT_motionpaths,
]


###-----------------------------------------------------------------------------###
###                              DRAW FUNCTIONS                                 ###
###-----------------------------------------------------------------------------###

def draw_context_editarmature(pie, context):
    # WEST
    pie.operator("armature.parent_set", text="Make Parent")
    # EAST
    pie.operator("armature.parent_clear", text="Clear Parent")
    # SOUTH
    pie.operator("armature.extrude_move")
    # NORTH
    pie.operator("armature.fill")
    # NORTH-WEST
    pie.operator("armature.symmetrize")
    # NORTH-EAST
    pie.operator("armature.subdivide", text="Subdivide")
    # SOUTH-WEST
    pie.operator("armature.dissolve", text="Dissolve")
    # SOUTH-EAST
    pie.operator("armature.split")


def draw_context_pose(pie, context):
    # WEST
    pie.operator("wm.call_menu_pie", text='Copy...').name = "SUBPIE_MT_pose_copy"
    # EAST
    pie.operator("pose.paste").flipped = False
    # SOUTH
    pie.operator("wm.call_menu_pie", text='Inbetweens...').name = "SUBPIE_MT_inbetweens"
    # NORTH
    pie.operator("wm.call_menu_pie", text='Motion Paths...').name = "SUBPIE_MT_motionpaths"
    # NORTH-WEST
    pie.operator("wm.call_menu_pie", text='Constraints...').name = "SUBPIE_MT_constraints"
    # NORTH-EAST
    pie.operator("pose.paste", text='Paste Flipped').flipped = True
    # SOUTH-WEST
    pie.operator("wm.call_menu_pie", text='Propagate...').name = "SUBPIE_MT_propagate"
    # SOUTH-EAST
    pie.operator("wm.call_menu_pie", text='IK...').name = "SUBPIE_MT_ik"
