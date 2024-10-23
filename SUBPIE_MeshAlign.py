# SPDX-FileCopyrightText: 2016-2024 Blender Foundation
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu, Operator
from bpy.props import EnumProperty
from .hotkeys import register_hotkey


class SUBPIE_MT_mesh_align(Menu):
    bl_idname = "SUBPIE_MT_mesh_align"
    bl_label = "Mesh Align"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        box = pie.split().box().column()

        row = box.row(align=True)
        row.label(text="X")
        align_1 = row.operator("transform.flat_local_minmax", text="Neg")
        align_1.axis = '0'
        align_1.side = 'NEGATIVE'

        row = box.row(align=True)
        row.label(text="Y")
        align_3 = row.operator("transform.flat_local_minmax", text="Neg")
        align_3.axis = '1'
        align_3.side = 'NEGATIVE'

        row = box.row(align=True)
        row.label(text="Z")
        align_5 = row.operator("transform.flat_local_minmax", text="Neg")
        align_5.axis = '2'
        align_5.side = 'NEGATIVE'
        # 6 - RIGHT
        box = pie.split().box().column()

        row = box.row(align=True)
        row.label(text="X")
        align_2 = row.operator("transform.flat_local_minmax", text="Pos")
        align_2.axis = '0'
        align_2.side = 'POSITIVE'

        row = box.row(align=True)
        row.label(text="Y")
        align_4 = row.operator("transform.flat_local_minmax", text="Pos")
        align_4.axis = '1'
        align_4.side = 'POSITIVE'

        row = box.row(align=True)
        row.label(text="Z")
        align_6 = row.operator("transform.flat_local_minmax", text="Pos")
        align_6.axis = '2'
        align_6.side = 'POSITIVE'
        # 2 - BOTTOM
        pie.operator("transform.flat_local_axis", text="Align To Y-0").axis = '1'
        # 8 - TOP
        pie.operator("transform.flat_global_axis", text="Align Y").axis = 'Y'
        # 7 - TOP - LEFT
        pie.operator("transform.flat_global_axis", text="Align X").axis = 'X'
        # 9 - TOP - RIGHT
        pie.operator("transform.flat_global_axis", text="Align Z").axis = 'Z'
        # 1 - BOTTOM - LEFT
        pie.operator("transform.flat_local_axis", text="Align To X-0").axis = '0'
        # 3 - BOTTOM - RIGHT
        pie.operator("transform.flat_local_axis", text="Align To Z-0").axis = '2'


class TRANSFORM_OT_flat_global_axis(Operator):
    """Flatten selection along a global axis"""

    bl_idname = "transform.flat_global_axis"
    bl_label = "Flatten To Global Axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name="Axis",
        items=(
            ('X', "X", "X Axis"),
            ('Y', "Y", "Y Axis"),
            ('Z', "Z", "Z Axis"),
        ),
        description="Choose an axis for alignment",
        default='X',
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH"

    def execute(self, context):
        values = {
            'X': [(0, 1, 1), (True, False, False)],
            'Y': [(1, 0, 1), (False, True, False)],
            'Z': [(1, 1, 0), (False, False, True)],
        }
        chosen_value = values[self.axis][0]
        constraint_value = values[self.axis][1]
        bpy.ops.transform.resize(
            value=chosen_value,
            constraint_axis=constraint_value,
            orient_type='GLOBAL',
            mirror=False,
            use_proportional_edit=False,
        )
        return {'FINISHED'}


class TRANSFORM_OT_flat_local_axis(Operator):
    """Flatten selection along a local axis"""

    bl_idname = "transform.flat_local_axis"
    bl_label = "Align To X, Y or Z = 0"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name="Axis",
        items=(
            ('0', "X", "X Axis"),
            ('1', "Y", "Y Axis"),
            ('2', "Z", "Z Axis"),
        ),
        description="Choose an axis for alignment",
        default='0',
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        align = int(self.axis)
        for vert in bpy.context.object.data.vertices:
            if vert.select:
                vert.co[align] = 0
        bpy.ops.object.editmode_toggle()

        return {'FINISHED'}


class TRANSFORM_OT_flat_local_minmax(Operator):
    """Align to a Front or Back along the chosen Axis"""

    bl_idname = "transform.flat_local_minmax"
    bl_label = "Align to Front/Back Axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name="Axis",
        items=(
            ('0', "X", "X Axis"),
            ('1', "Y", "Y Axis"),
            ('2', "Z", "Z Axis"),
        ),
        description="Choose an axis for alignment",
        default='0',
    )
    side: EnumProperty(
        name="Side",
        items=[
            ('POSITIVE', "Front", "Align on the positive chosen axis"),
            ('NEGATIVE', "Back", "Align acriss the negative chosen axis"),
        ],
        description="Choose a side for alignment",
        default='POSITIVE',
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        count = 0
        axis = int(self.axis)
        for vert in bpy.context.object.data.vertices:
            if vert.select:
                if count == 0:
                    maxv = vert.co[axis]
                    count += 1
                    continue
                count += 1
                if self.side == 'POSITIVE':
                    if vert.co[axis] > maxv:
                        maxv = vert.co[axis]
                else:
                    if vert.co[axis] < maxv:
                        maxv = vert.co[axis]

        bpy.ops.object.mode_set(mode='OBJECT')

        for vert in bpy.context.object.data.vertices:
            if vert.select:
                vert.co[axis] = maxv
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


registry = [
    SUBPIE_MT_mesh_align,
    TRANSFORM_OT_flat_global_axis,
    TRANSFORM_OT_flat_local_axis,
    TRANSFORM_OT_flat_local_minmax,
]