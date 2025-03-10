# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Context Pie: Proportional Sub Pie Menu",
    "blender": (4, 2, 0),
    "category": "Interface",
    "description": "Context sensitive pie menu for a simple, fast workflow",
    "author": "Bastian L Strube",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}

from bpy.types import (
    Menu,
    Operator,
)

"""
# Proportional Edit Object
class SUBPIE_OT_ProportionalEditObj(Operator):
    bl_idname = "pie_snap_obj.active"
    bl_label = "Proportional Edit Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings

        if ts.use_snap is True:
            ts.use_snap = False

        elif ts.use_snap is False:
            ts.use_snap = True

        return {'FINISHED'}

class SUBPIE_OT_ProportionalConstantObj(Operator):
    bl_idname = "pie_proportional_obj.constant"
    bl_label = "Proportional Constant Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.proportional_edit_falloff = 'CONSTANT'

        if ts.proportional_edit_falloff != 'CONSTANT':
            ts.proportional_edit_falloff = 'CONSTANT'
        return {'FINISHED'}

# Proportional Edit Edit Mode
class SUBPIE_OT_ProportionalEditEdt(Operator):
    bl_idname = "pie_snap_edt.active"
    bl_label = "Proportional Edit EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit ^= 1
        return {'FINISHED'}

class SUBPIE_OT_SwapSnapElementsBase(Operator):
    bl_idname = "pie_snap.elements"
    bl_label = "Proportional Connected EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    elementsbase = ({'INCREMENT'}, {'VERTEX'}, {'EDGE'}, {'FACE'}, {'VOLUME'}, {'EDGE_MIDPOINT'}, {'EDGE_PERPENDICULAR'})

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_connected ^= 1
        return {'FINISHED'}
"""
#    elementsbase = ({'INCREMENT'}, {'VERTEX'}, {'EDGE'}, {'FACE'}, {'VOLUME'}, {'EDGE_MIDPOINT'}, {'EDGE_PERPENDICULAR'})

class SUBPIE_OT_SnapIncrement(Operator):
    bl_idname = "pie_snap.increment"
    bl_label = "Snap Increment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'INCREMENT'}

        if not ts.snap_elements_base == {'INCREMENT'}:
            ts.snap_elements_base = {'INCREMENT'}
        return {'FINISHED'}

class SUBPIE_OT_SnapGrid(Operator):
    bl_idname = "pie_snap.grid"
    bl_label = "Snap Grid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'GRID'}

        if not ts.snap_elements_base == {'GRID'}:
            ts.snap_elements_base = {'GRID'}
        return {'FINISHED'}

class SUBPIE_OT_SnapVertex(Operator):
    bl_idname = "pie_snap.vertex"
    bl_label = "Snap Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'VERTEX'}

        if not ts.snap_elements_base == {'VERTEX'}:
            ts.snap_elements_base = {'VERTEX'}
        return {'FINISHED'}

class SUBPIE_OT_SnapEdge(Operator):
    bl_idname = "pie_snap.edge"
    bl_label = "Snap Edge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'EDGE'}

        if not ts.snap_elements_base == {'EDGE'}:
            ts.snap_elements_base = {'EDGE'}
        return {'FINISHED'}

class SUBPIE_OT_SnapFace(Operator):
    bl_idname = "pie_snap.face"
    bl_label = "Snap Face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'FACE'}

        if not ts.snap_elements_base == {'FACE'}:
            ts.snap_elements_base = {'FACE'}
        return {'FINISHED'}

class SUBPIE_OT_SnapVolume(Operator):
    bl_idname = "pie_snap.volume"
    bl_label = "Snap Volume"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'VOLUME'}

        if not ts.snap_elements_base == {'VOLUME'}:
            ts.snap_elements_base = {'VOLUME'}
        return {'FINISHED'}

class SUBPIE_OT_SnapEdgeMidpoint(Operator):
    bl_idname = "pie_snap.edgemidpoint"
    bl_label = "Snap Edge Midpoint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'EDGE_MIDPOINT'}

        if not ts.snap_elements_base == {'EDGE_MIDPOINT'}:
            ts.snap_elements_base = {'EDGE_MIDPOINT'}
        return {'FINISHED'}

class SUBPIE_OT_SnapEdgePerpendicular(Operator):
    bl_idname = "pie_snap.edgeperpendicular"
    bl_label = "Snap Edge Perpendicular"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_snap is False:
            ts.use_snap = True
            ts.snap_elements_base = {'EDGE_PERPENDICULAR'}

        if not ts.snap_elements_base == {'EDGE_PERPENDICULAR'}:
            ts.snap_elements_base = {'EDGE_PERPENDICULAR'}
        return {'FINISHED'}

# Sub Pie SnapEditObj
class SUBPIE_MT_Snap(Menu):
    bl_idname = "SUBPIE_MT_snap"
    bl_label = "Snap"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        ts = context.tool_settings
        # 4 - LEFT
        pie.operator("pie_snap.volume", text="Volume", icon='SNAP_VOLUME')
        # 6 - RIGHT
        pie.operator("pie_snap.vertex", text="Vertex", icon='SNAP_VERTEX')
        # 2 - BOTTOM
        pie.prop(ts, "use_snap", text="Snap On/Off")
        # 8 - TOP
        pie.operator("pie_snap.edge", text="Edge", icon='SNAP_EDGE')
        # 7 - TOP - LEFT
        pie.operator("pie_snap.edgemidpoint", text="Edge Midpoint", icon='SNAP_MIDPOINT')
        # 9 - TOP - RIGHT
        pie.operator("pie_snap.grid", text="Grid", icon='SNAP_GRID')
        # 1 - BOTTOM - LEFT
        pie.operator("pie_snap.increment", text="Increment", icon='SNAP_INCREMENT')
        # 3 - BOTTOM - RIGHT
        pie.operator("pie_snap.face", text="Face", icon='SNAP_FACE')


registry = (
    SUBPIE_OT_SnapIncrement,
    SUBPIE_OT_SnapGrid,
    SUBPIE_OT_SnapVertex,
    SUBPIE_OT_SnapEdge,
    SUBPIE_OT_SnapFace,
    SUBPIE_OT_SnapVolume,
    SUBPIE_OT_SnapEdgeMidpoint,
    SUBPIE_OT_SnapEdgePerpendicular,
    SUBPIE_MT_Snap,
)
