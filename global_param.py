

import bpy
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


def init():
    bpy.types.Scene.linkgptMessage = bpy.props.StringProperty(
        name="Message",
        description="Enter your message",
        default="",)
         
def release():
    del bpy.types.Scene.linkgptMessage 
