# <pep8-80 compliant>

import bpy
from ..utils.bl_class_registry import BlClassRegistry
from ..utils import compatibility as compat

from ..op import op_center_panel

@BlClassRegistry()
@compat.ChangeRegionType(region_type='TOOLS')
class UI_Center_Panel(bpy.types.Panel):
    bl_idname = "ui.center_panel"
    bl_label = "CenterPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LinkGPT" 

    def draw_header(self, _):
        layout = self.layout
        row = layout.row(align=True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column()
        title_size = 0.4
        row = col.split(factor=title_size, align=True)
        row.label(text='Input Message')
        row.prop(context.scene.GlobalParam, "inputMessage", text="23")

        # 添加一个输入框
        layout.label(text="Enter text:")
        layout.prop(context.scene, "my_string_property", text="Enter Text" )  # 添加

        # 添加一个显示框
        layout.label(text="Result:")
        # 显示字符串属性的值 
        row_button = layout.row(align=True)
        row_button.scale_y = 1.5
        row_button.operator(op_center_panel.poll_step.bl_idname, text="Ask GPT")