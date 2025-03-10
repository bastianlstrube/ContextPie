# SPDX-FileCopyrightText: 2016-2022 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

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


# Proportional Edit Object
class SUBPIE_OT_ProportionalSmoothObj(Operator):
    bl_idname = "pie_proportional_obj.smooth"
    bl_label = "Proportional Smooth Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'SMOOTH'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalSphereObj(Operator):
    bl_idname = "pie_proportional_obj.sphere"
    bl_label = "Proportional Sphere Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'SPHERE'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalRootObj(Operator):
    bl_idname = "pie_proportional_obj.root"
    bl_label = "Proportional Root Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'ROOT'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalSharpObj(Operator):
    bl_idname = "pie_proportional_obj.sharp"
    bl_label = "Proportional Sharp Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'SHARP'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalLinearObj(Operator):
    bl_idname = "pie_proportional_obj.linear"
    bl_label = "Proportional Linear Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'LINEAR'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalConstantObj(Operator):
    bl_idname = "pie_proportional_obj.constant"
    bl_label = "Proportional Constant Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'CONSTANT'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalRandomObj(Operator):
    bl_idname = "pie_proportional_obj.random"
    bl_label = "Proportional Random Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'RANDOM'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalInverseSquareObj(Operator):
    bl_idname = "pie_proportional_obj.inversesquare"
    bl_label = "Proportional Random Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit_objects = True
        ts.proportional_edit_falloff = 'INVERSE_SQUARE'
        return {'FINISHED'}


# Proportional Edit Edit Mode
class SUBPIE_OT_ProportionalSmoothEdt(Operator):
    bl_idname = "pie_proportional_edt.smooth"
    bl_label = "Proportional Smooth EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'SMOOTH'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalSphereEdt(Operator):
    bl_idname = "pie_proportional_edt.sphere"
    bl_label = "Proportional Sphere EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'SPHERE'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalRootEdt(Operator):
    bl_idname = "pie_proportional_edt.root"
    bl_label = "Proportional Root EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'ROOT'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalSharpEdt(Operator):
    bl_idname = "pie_proportional_edt.sharp"
    bl_label = "Proportional Sharp EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'SHARP'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalLinearEdt(Operator):
    bl_idname = "pie_proportional_edt.linear"
    bl_label = "Proportional Linear EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'LINEAR'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalConstantEdt(Operator):
    bl_idname = "pie_proportional_edt.constant"
    bl_label = "Proportional Constant EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'CONSTANT'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalRandomEdt(Operator):
    bl_idname = "pie_proportional_edt.random"
    bl_label = "Proportional Random EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'RANDOM'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalInverseSquareEdt(Operator):
    bl_idname = "pie_proportional_edt.inversesquare"
    bl_label = "Proportional Inverese Square EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit = True
        ts.proportional_edit_falloff = 'INVERSE_SQUARE'
        return {'FINISHED'}


# Pie ProportionalEditObj - O
class SUBPIE_MT_ProportionalObj(Menu):
    bl_idname = "SUBPIE_MT_proportional_obj"
    bl_label = "Proportional Object"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("pie_proportional_obj.smooth", text="Smooth", icon='SMOOTHCURVE')
        # 6 - RIGHT
        pie.operator("pie_proportional_obj.sphere", text="Linear", icon='LINCURVE')
        # 2 - BOTTOM
        pie.operator("pie_proportional_obj.root", text="Sharp", icon='SHARPCURVE')
        # 8 - TOP
        pie.prop(context.tool_settings, "use_proportional_edit_objects", text="Proportional On/Off")
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.operator("pie_proportional_obj.inversesquare", text="Sphere", icon='SPHERECURVE')
        # 3 - BOTTOM - RIGHT
        pie.menu("SUBPIE_MT_proportional_moreob", text="More...", icon='ROOTCURVE')

# Pie ProportionalEditEdt2
class SUBPIE_MT_proportionalmoreob(Menu):
    bl_idname = "SUBPIE_MT_proportional_moreob"
    bl_label = "Proportional More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        box = pie.split().column()
        box.operator("pie_proportional_obj.root", text="Root", icon='ROOTCURVE')
        box.operator("pie_proportional_obj.inversesquare", text="Inverse Square", icon='INVERSESQUARECURVE')
        box.operator("pie_proportional_obj.constant", text="Constant", icon='NOCURVE')
        box.operator("pie_proportional_obj.random", text="Random", icon='RNDCURVE')

# Pie ProportionalEditEdt - O
class SUBPIE_MT_ProportionalEdt(Menu):
    bl_idname = "SUBPIE_MT_proportional_edt"
    bl_label = "Proportional Edit"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        tool_settings = context.tool_settings
        # 4 - LEFT
        pie.operator("pie_proportional_edt.smooth", text="Smooth", icon='SMOOTHCURVE')
        # 6 - RIGHT
        pie.operator("pie_proportional_edt.linear", text="Linear", icon='LINCURVE')
        # 2 - BOTTOM
        pie.operator("pie_proportional_edt.sharp", text="Sharp", icon='SHARPCURVE')
        # 8 - TOP
        pie.prop(tool_settings, "use_proportional_edit", text="Proportional On/Off")
        # 7 - TOP - LEFT
        pie.prop(tool_settings, "use_proportional_connected")
        # 9 - TOP - RIGHT
        pie.prop(tool_settings, "use_proportional_projected")
        # 1 - BOTTOM - LEFT
        pie.operator("pie_proportional_edt.sphere", text="Sphere", icon='SPHERECURVE')
        # 3 - BOTTOM - RIGHT
        pie.menu("SUBPIE_MT_proportional_more", text="More...", icon='ROOTCURVE')


# Pie ProportionalEditEdt - O
class SUBPIE_MT_ProportionalMore(Menu):
    bl_idname = "SUBPIE_MT_proportional_more"
    bl_label = "Proportional More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        box = pie.split().column()
        box.operator("pie_proportional_edt.root", text="Root", icon='ROOTCURVE')
        box.operator("pie_proportional_edt.inversesquare", text="Inverse Square", icon='INVERSESQUARECURVE')
        box.operator("pie_proportional_edt.constant", text="Constant", icon='NOCURVE')
        box.operator("pie_proportional_edt.random", text="Random", icon='RNDCURVE')


registry = (
    SUBPIE_OT_ProportionalSmoothObj,
    SUBPIE_OT_ProportionalSphereObj,
    SUBPIE_OT_ProportionalRootObj,
    SUBPIE_OT_ProportionalSharpObj,
    SUBPIE_OT_ProportionalLinearObj,
    SUBPIE_OT_ProportionalConstantObj,
    SUBPIE_OT_ProportionalRandomObj,
    SUBPIE_OT_ProportionalInverseSquareObj,
    SUBPIE_OT_ProportionalSmoothEdt,
    SUBPIE_OT_ProportionalSphereEdt,
    SUBPIE_OT_ProportionalRootEdt,
    SUBPIE_OT_ProportionalSharpEdt,
    SUBPIE_OT_ProportionalLinearEdt,
    SUBPIE_OT_ProportionalConstantEdt,
    SUBPIE_OT_ProportionalRandomEdt,
    SUBPIE_OT_ProportionalInverseSquareEdt,
    SUBPIE_MT_ProportionalObj,
    SUBPIE_MT_ProportionalEdt,
    SUBPIE_MT_ProportionalMore,
    SUBPIE_MT_proportionalmoreob
)
