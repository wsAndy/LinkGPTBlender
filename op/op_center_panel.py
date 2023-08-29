import bpy
import os
from ..utils.bl_class_registry import BlClassRegistry
from ..utils import compatibility as compat
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)
import time
from ..utils import ws_utils
import platform
import math

@BlClassRegistry()
@compat.make_annotations
class poll_step(bpy.types.Operator):
    bl_idname = "op.askgpt"
    bl_label = ""
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # class variables
    IsLooping = False

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        print('poll_step execute')
        self.IsLooping = True

        if (self.IsLooping):
            wm = context.window_manager
            # add timer,每间0.3秒执行下面的modal函数
            self.timer = wm.event_timer_add(0.3, window=context.window)
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            print('poll_step out')
            return {'FINISHED'}

    # reset things (for FINISHED or CANCELLED)
    def onEndingOperator(self, context, isSuccess):
        wm = context.window_manager
        if self.timer != None:
            wm.event_timer_remove(self.timer)
            self.timer = None
        self.IsLooping = False

    def modal(self, context, event):
        #console_print("modal called.   event.type="+str(event.type))
        if event.type in {'ESC'}:
            self.report({'INFO'}, "CANCELLED !")
            self.onEndingOperator(context, False)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # 添加一定的判断逻辑，比如本地文件是否存在?
            # 是否完成了写入?
            # 对于没有完成的，始终要等待，对于已经完成的，则直接展示；
            self.IsLooping = True 
            return {'FINISHED'}
            return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        #console_print("invoke called!!!")

        self.execute(context)
        if self.IsLooping:
            return {'RUNNING_MODAL'}
        else:
            return {'FINISHED'}

    def cancel(self, context):
        return {'CANCELLED'}
