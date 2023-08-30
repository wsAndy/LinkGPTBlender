

__status__ = "production"
__version__ = "0.1"
__date__ = "2023/08/29"

bl_info = {
    "name": "LinkGPT",
    "author": "ws",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > LinkGPT",
    "description": "Add on",
    "warning": "",
    "support": "COMMUNITY",
    "category": "3D View",
}


import bpy
# from . import auto_load
from . import utils
utils.bl_class_registry.BlClassRegistry.cleanup()


from . import ui
from . import op
from . import global_param
 

def register(): 
    utils.bl_class_registry.BlClassRegistry.register()

    global_param.init()

def unregister(): 
    utils.bl_class_registry.BlClassRegistry.unregister()

    global_param.release()


if __name__ == "__main__":
    register()    