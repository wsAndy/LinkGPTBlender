# <pep8-80 compliant>

import bpy
from ..utils.bl_class_registry import BlClassRegistry
from ..utils import compatibility as compat

from ..op import op_center_panel

# 一个UI面板
@BlClassRegistry()
@compat.ChangeRegionType(region_type='TOOLS')
class ui_center_panel(bpy.types.Panel):
    bl_idname = "ui.ui_center_panel"
    bl_label = "PoseChange"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LinkGPT"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, _):
        layout = self.layout
        row = layout.row(align=True)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text="Input Message:")
        row = layout.row(align=True)
        row.scale_y = 4
        row.prop(context.scene, "linkgptMessage", text="")
        
        row.enabled = True

        row = layout.row(align=True)
        row.scale_y = 2
        row.operator(op_center_panel.poll_step.bl_idname, text="Ask GPT")
        