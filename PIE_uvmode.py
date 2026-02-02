# SPDX-FileCopyrightText: 2016-2024 Bastian L. Strube
#
# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Menu

from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only_cpie


class SUBPIE_MT_uvSelect(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.separator()
        pie.operator("uv.select_pinned", text="Pinned")
        pie.operator("uv.select_overlap", text="Overlap")
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.operator("uv.select_linked", text="Island")


class SUBPIE_MT_uvSticky(Menu):
    bl_label = "Sticky"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        op = pie.operator('wm.context_set_string', text="Location", icon="STICKY_UVS_LOC")
        op.data_path = 'tool_settings.uv_sticky_select_mode'
        op.value = 'SHARED_LOCATION'
        pie.separator()
        op = pie.operator('wm.context_set_string', text="Vertex", icon="STICKY_UVS_VERT")
        op.data_path = 'tool_settings.uv_sticky_select_mode'
        op.value = 'SHARED_VERTEX'
        pie.separator()
        pie.separator()
        pie.separator()
        op = pie.operator('wm.context_set_string', text="Disabled", icon="STICKY_UVS_DISABLE")
        op.data_path = 'tool_settings.uv_sticky_select_mode'
        op.value = 'DISABLED'
        pie.separator()


class SUBPIE_MT_uvTools(Menu):
    bl_label = "UV Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        pie.operator('wm.tool_set_by_id', text="Pinch").name = 'sculpt.uv_sculpt_pinch'
        pie.operator('wm.tool_set_by_id', text="Select Box").name = 'builtin.select_box'
        pie.separator()
        pie.operator('wm.tool_set_by_id', text="Grab").name = 'sculpt.uv_sculpt_grab'
        pie.operator('wm.tool_set_by_id', text="Relax").name = 'sculpt.uv_sculpt_relax'
        pie.operator('wm.tool_set_by_id', text="Rip Region").name = 'builtin.rip_region'
        pie.separator()
        pie.separator()


class IMAGE_PIE_MT_uvMode(Menu):
    bl_idname = "PIE_MT_context_uvmode"
    bl_label = "UV Mode Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        pie = layout.menu_pie()

        use_sync = context.tool_settings.use_uv_select_sync

        if use_sync:
            self.draw_sync_mode(pie, context)
        else:
            self.draw_uv_mode(pie, context)

        self.draw_common(pie, context)

    def draw_uv_mode(self, pie, context):
        pie.prop(context.tool_settings, "use_uv_select_sync", text="Sync Selection", icon="UV_SYNC_SELECT")
        op = pie.operator('wm.context_set_string', text="Vertex", icon="UV_VERTEXSEL")
        op.data_path = 'tool_settings.uv_select_mode'
        op.value = 'VERTEX'
        op = pie.operator('wm.context_set_string', text="Face", icon="UV_FACESEL")
        op.data_path = 'tool_settings.uv_select_mode'
        op.value = 'FACE'
        op = pie.operator('wm.context_set_string', text="Edge", icon="UV_EDGESEL")
        op.data_path = 'tool_settings.uv_select_mode'
        op.value = 'EDGE'

    def draw_sync_mode(self, pie, context):
        pie.prop(context.tool_settings, "use_uv_select_sync", text="Sync Selection", icon="UV_SYNC_SELECT")
        pie.operator('mesh.select_mode', text="Vertex", icon="VERTEXSEL").type = 'VERT'
        pie.operator('mesh.select_mode', text="Face", icon="FACESEL").type = 'FACE'
        pie.operator('mesh.select_mode', text="Edge", icon="EDGESEL").type = 'EDGE'

    def draw_common(self, pie, context):
        pie.operator("wm.call_menu_pie", text='Tools...').name = "SUBPIE_MT_uvTools"
        pie.prop(context.tool_settings, "use_uv_select_island", text="Islands", icon="UV_ISLANDSEL")
        pie.operator("wm.call_menu_pie", text='Sticky...').name = "SUBPIE_MT_uvSticky"
        pie.operator("wm.call_menu_pie", text='Select...').name = "SUBPIE_MT_uvSelect"

        # Static dropdown menu
        pie.separator()
        pie.separator()
        dropdown = pie.column()
        gap = dropdown.column()
        gap.separator()
        gap.scale_y = 8
        dropdown_menu = dropdown.box().column()
        dropdown_menu.scale_y = 1
        dropdown_menu.scale_x = 1.2
        dropdown_menu.menu("IMAGE_MT_uvs", text="UV menu", icon="COLLAPSEMENU")


registry = [
    SUBPIE_MT_uvSelect,
    SUBPIE_MT_uvSticky,
    SUBPIE_MT_uvTools,
    IMAGE_PIE_MT_uvMode,
]


def register():
    WM_OT_call_menu_pie_drag_only_cpie.register_drag_hotkey(
        pie_name=IMAGE_PIE_MT_uvMode.bl_idname,
        hotkey_kwargs={'type': "RIGHTMOUSE", 'value': "PRESS", 'shift': False},
        keymap_name="UV Editor",
    )
