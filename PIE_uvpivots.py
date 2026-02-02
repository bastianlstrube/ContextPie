# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class IMAGE_PIE_MT_uvPivots(Menu):
    bl_idname = "PIE_MT_context_uvpivots"
    bl_label = "UV Pivots"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.separator()
        pie.operator("wm.call_menu_pie", text='Pivot...', icon="RIGHTARROW_THIN").name = "IMAGE_MT_pivot_pie"
        pie.separator()
        pie.operator("wm.call_menu_pie", text='Proportional...', icon="RIGHTARROW_THIN").name = "SUBPIE_MT_proportional_edt"
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()


registry = [
    IMAGE_PIE_MT_uvPivots,
]


def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=IMAGE_PIE_MT_uvPivots.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'ctrl': True},
        keymap_name="UV Editor",
    )
