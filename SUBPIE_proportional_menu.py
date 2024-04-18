# SPDX-FileCopyrightText: 2016-2022 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Context Pie: Proportional Sub Pie Menu",
    "blender": (4, 1, 0),
    "category": "Interface",
    "description": "Context Sensitive Pie Menu, following an ancient Mayan pie recipe",
    "author": "Bastian L Strube, Frederik Storm",
    "location": "View3D (Object, Mesh, Curve, Lattice), UV Editor",
}


import bpy
from bpy.types import (
    Menu,
    Operator,
)


# Proportional Edit Object
class SUBPIE_OT_ProportionalEditObj(Operator):
    bl_idname = "pie_proportional_obj.active"
    bl_label = "Proportional Edit Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings

        if ts.use_proportional_edit_objects is True:
            ts.use_proportional_edit_objects = False

        elif ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True

        return {'FINISHED'}


class SUBPIE_OT_ProportionalSmoothObj(Operator):
    bl_idname = "pie_proportional_obj.smooth"
    bl_label = "Proportional Smooth Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'SMOOTH'

        if ts.proportional_edit_falloff != 'SMOOTH':
            ts.proportional_edit_falloff = 'SMOOTH'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalSphereObj(Operator):
    bl_idname = "pie_proportional_obj.sphere"
    bl_label = "Proportional Sphere Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'SPHERE'

        if ts.proportional_edit_falloff != 'SPHERE':
            ts.proportional_edit_falloff = 'SPHERE'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalRootObj(Operator):
    bl_idname = "pie_proportional_obj.root"
    bl_label = "Proportional Root Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'ROOT'

        if ts.proportional_edit_falloff != 'ROOT':
            ts.proportional_edit_falloff = 'ROOT'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalSharpObj(Operator):
    bl_idname = "pie_proportional_obj.sharp"
    bl_label = "Proportional Sharp Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'SHARP'

        if ts.proportional_edit_falloff != 'SHARP':
            ts.proportional_edit_falloff = 'SHARP'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalLinearObj(Operator):
    bl_idname = "pie_proportional_obj.linear"
    bl_label = "Proportional Linear Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'LINEAR'

        if ts.proportional_edit_falloff != 'LINEAR':
            ts.proportional_edit_falloff = 'LINEAR'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalConstantObj(Operator):
    bl_idname = "pie_proportional_obj.constant"
    bl_label = "Proportional Constant Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'CONSTANT'

        if ts.proportional_edit_falloff != 'CONSTANT':
            ts.proportional_edit_falloff = 'CONSTANT'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalRandomObj(Operator):
    bl_idname = "pie_proportional_obj.random"
    bl_label = "Proportional Random Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'RANDOM'

        if ts.proportional_edit_falloff != 'RANDOM':
            ts.proportional_edit_falloff = 'RANDOM'
        return {'FINISHED'}


class SUBPIE_OT_ProportionalInverseSquareObj(Operator):
    bl_idname = "pie_proportional_obj.inversesquare"
    bl_label = "Proportional Random Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        if ts.use_proportional_edit_objects is False:
            ts.use_proportional_edit_objects = True
            ts.proportional_edit_falloff = 'INVERSE_SQUARE'

        if ts.proportional_edit_falloff != 'INVERSE_SQUARE':
            ts.proportional_edit_falloff = 'INVERSE_SQUARE'
        return {'FINISHED'}


# Proportional Edit Edit Mode
class SUBPIE_OT_ProportionalEditEdt(Operator):
    bl_idname = "pie_proportional_edt.active"
    bl_label = "Proportional Edit EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_edit ^= 1
        return {'FINISHED'}


class SUBPIE_OT_ProportionalConnectedEdt(Operator):
    bl_idname = "pie_proportional_edt.connected"
    bl_label = "Proportional Connected EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_connected ^= 1
        return {'FINISHED'}


class SUBPIE_OT_ProportionalProjectedEdt(Operator):
    bl_idname = "pie_proportional_edt.projected"
    bl_label = "Proportional projected EditMode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = context.tool_settings
        ts.use_proportional_projected ^= 1
        return {'FINISHED'}


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
    bl_label = "Pie Proportional Obj"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("pie_proportional_obj.smooth", text="Smooth", icon='SMOOTHCURVE')
        # 6 - RIGHT
        pie.operator("pie_proportional_obj.sphere", text="Sphere", icon='SPHERECURVE')
        # 2 - BOTTOM
        pie.operator("pie_proportional_obj.linear", text="Linear", icon='LINCURVE')
        # 8 - TOP
        pie.prop(context.tool_settings, "use_proportional_edit_objects", text="Proportional On/Off")
        # 7 - TOP - LEFT
        pie.operator("pie_proportional_obj.root", text="Root", icon='ROOTCURVE')
        # 9 - TOP - RIGHT
        pie.operator("pie_proportional_obj.inversesquare", text="Inverse Square", icon='INVERSESQUARECURVE')
        # 1 - BOTTOM - LEFT
        pie.operator("pie_proportional_obj.sharp", text="Sharp", icon='SHARPCURVE')
        # 3 - BOTTOM - RIGHT
        pie.menu("SUBPIE_MT_proportional_moreob", text="More", icon='LINCURVE')


# Pie ProportionalEditEdt - O
class SUBPIE_MT_ProportionalEdt(Menu):
    bl_idname = "SUBPIE_MT_proportional_edt"
    bl_label = "Pie Proportional Edit"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        pie.operator("pie_proportional_edt.smooth", text="Smooth", icon='SMOOTHCURVE')
        # 6 - RIGHT
        pie.operator("pie_proportional_edt.sphere", text="Sphere", icon='SPHERECURVE')
        # 2 - BOTTOM
        pie.operator("pie_proportional_edt.inversesquare", text="Inverse Square", icon='INVERSESQUARECURVE')
        # 8 - TOP
        pie.operator("pie_proportional_edt.active", text="Proportional On/Off", icon='PROP_ON')
        # 7 - TOP - LEFT
        pie.operator("pie_proportional_edt.connected", text="Connected", icon='PROP_CON')
        # 9 - TOP - RIGHT
        pie.operator("pie_proportional_edt.projected", text="Projected", icon='PROP_PROJECTED')
        # 1 - BOTTOM - LEFT
        pie.operator("pie_proportional_edt.root", text="Root", icon='ROOTCURVE')
        # 3 - BOTTOM - RIGHT
        pie.menu("SUBPIE_MT_proportional_more", text="More", icon='LINCURVE')


# Pie ProportionalEditEdt - O
class SUBPIE_MT_ProportionalMore(Menu):
    bl_idname = "SUBPIE_MT_proportional_more"
    bl_label = "Pie Proportional More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        box = pie.split().column()
        box.operator("pie_proportional_edt.sharp", text="Sharp", icon='SHARPCURVE')
        box.operator("pie_proportional_edt.linear", text="Linear", icon='LINCURVE')
        box.operator("pie_proportional_edt.constant", text="Constant", icon='NOCURVE')
        box.operator("pie_proportional_edt.random", text="Random", icon='RNDCURVE')


# Pie ProportionalEditEdt2
class SUBPIE_MT_proportionalmoreob(Menu):
    bl_idname = "SUBPIE_MT_proportional_moreob"
    bl_label = "Pie Proportional More"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        box = pie.split().column()
        box.operator("pie_proportional_obj.constant", text="Constant", icon='NOCURVE')
        box.operator("pie_proportional_obj.random", text="Random", icon='RNDCURVE')


classes = (
    SUBPIE_OT_ProportionalEditObj,
    SUBPIE_OT_ProportionalSmoothObj,
    SUBPIE_OT_ProportionalSphereObj,
    SUBPIE_OT_ProportionalRootObj,
    SUBPIE_OT_ProportionalSharpObj,
    SUBPIE_OT_ProportionalLinearObj,
    SUBPIE_OT_ProportionalConstantObj,
    SUBPIE_OT_ProportionalRandomObj,
    SUBPIE_OT_ProportionalInverseSquareObj,
    SUBPIE_OT_ProportionalEditEdt,
    SUBPIE_OT_ProportionalConnectedEdt,
    SUBPIE_OT_ProportionalProjectedEdt,
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


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
