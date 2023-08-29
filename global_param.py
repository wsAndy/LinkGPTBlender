

import bpy
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

@BlClassRegistry()
class GlobalParam(bpy.types.PropertyGroup):
    bl_label = "GlobalParam"
    bl_space_type = ''
    bl_region_type = ''
    bl_category = ""

    inputMessage = bpy.props.StringProperty(
        name="Message",
        description="Enter your message",
        default="",)
        

def init():
    bpy.types.Scene.GlobalParam = bpy.props.PointerProperty(type=GlobalParam)
