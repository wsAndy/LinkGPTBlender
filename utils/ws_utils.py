
# 目前在scene、data中删除数据，保证直接从data中删除

# 初始化(删除物体、删除场景)
# 创建场景 
# 添加物体
# 选择物体（激活物体先不考虑）
# object切换模式
# 执行操作

# 切换场景
# 显示/隐藏物体

# 所有mesh回到object模式
# 初始化(删除物体、删除场景)

# 对mesh整体pose操作-ok


# 获取mesh属性
#  vertex
#  edge
#  uv .... 这个我自己还不明确
#  高级函数：在当前mesh中搜素两个点之间最短路径、

# mesh edit部分
#  加点、减点 无意义
#  加边、减边 无意义
#  高级函数：在当前mesh中搜素两个边之间最短路径、

# 高级功能，目前由bmesh来提供
# This API gives access the Blender’s internal mesh editing API, featuring geometry connectivity data and access to editing operations such as split, separate, collapse and dissolve. The features exposed closely follow the C API, giving Python access to the functions used by Blender’s own mesh editing tools.

# 物体材质、UV
#  ...

# bmesh.ops 和 bpy.ops的异同：https://blender.stackexchange.com/questions/134867/how-bpy-ops-mesh-differs-from-bmesh-ops
# 简言之，bmesh为脚本而生，bpy.ops则更多与UI交互，所以这两个之间存在很多的重复功能，但是设计的想法不同；
# 由于ops与UI交互，因此有些操作ops和bmesh会不同，比如bmesh在操作是不care object当前状态，ops则需要物体在Edit模式
# bmesh操作时，往往隐藏了中间过程，定义了所有数据、处理所有数据之后，最终再渲染出来。

# TODO：
# 物体材质操作的功能性函数
# 现有插件交互
# 


import bpy
import bmesh
from math import radians
import os
import math
from mathutils import Vector
from pathlib import Path

'''
bpy.data - all data in your blend file.
bpy.context - data in the current active view.  context belongs to data
bpy.ops - tools which typically operate on bpy.context

Example:
    
>>> bpy.context.scene.objects
bpy.data.scenes['Scene'].objects

>>> bpy.context.scene.objects[0]
bpy.data.objects['Cube']

>>> bpy.context.scene.objects[1]
bpy.data.objects['Cube.001']

'''

class BLENDER_UTILS:
        
    def _INFO(type, msg):
        print(type + ': ' + msg)

    def console_print(*args, clear=False):
        s = " ".join([str(arg) for arg in args])
        print(s)
        for a in bpy.context.screen.areas:
            if a.type == 'CONSOLE':
                c = {}
                c['area'] = a
                c['space_data'] = a.spaces.active
                c['region'] = a.regions[-1]
                c['window'] = bpy.context.window
                c['screen'] = bpy.context.screen

                if clear:
                    bpy.ops.console.clear(c)

                for line in s.split("\n"):
                    bpy.ops.console.scrollback_append(c, text=line)

        
    def isString(input_data):
        if isinstance(input_data, str):
            return True
        else:
            return False

    def isNumber(input_data):
        if isinstance(input_data, float) or isinstance(input_data, int):
            return True
        else:
            return False

    def initBlender():
        BLENDER_UTILS.deleteScene()
        BLENDER_UTILS.deleteAllObject()
        BLENDER_UTILS.deleteMeshInProject()

    def deleteMeshInProject():
        '''
        delete all mesh in this blend file
        '''    
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)

    def deleteAllObject():
        '''
        delete all object in this blend file
        '''
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)

    #region mesh

    def importMesh(file, name):
        '''
        输入obj
        修改名字时，object的名字修改会导致scene sollection中的名字改变
        修改mesh名字则不会变
        '''
        old_obj = set(bpy.data.objects)
        old_mesh = set(bpy.data.meshes)
        if not BLENDER_UTILS.isString(file):
            BLENDER_UTILS._INFO('error', 'input a string!')
            return 
        filetype = file[file.rfind('.')+1:].lower()
        BLENDER_UTILS.selectNoMesh()
        if filetype == 'obj':
            bpy.ops.import_scene.obj(filepath=file)
        if filetype == 'glb' or filetype == 'gltf':
            bpy.ops.import_scene.gltf(filepath=file)
        if filetype == 'x3d':
            bpy.ops.import_scene.x3d(filepath=file)
        if filetype == 'fbx':
            bpy.ops.import_scene.fbx(filepath=file)
        if filetype == 'ply':
            bpy.ops.import_mesh.fbx(filepath=file)
            
        new_obj = set(bpy.data.objects)
        new_mesh = set(bpy.data.meshes)

        if len(list(new_obj - old_obj)) != 0:
            BLENDER_UTILS.renameMesh( list(new_mesh - old_mesh)[0].name, name)
            BLENDER_UTILS.renameObject(list(new_obj - old_obj)[0].name, name)


    def exportMeshByName(file, name):
        if not BLENDER_UTILS.isString(file):
            BLENDER_UTILS._INFO('error', 'input a string!')
            return 
        if not BLENDER_UTILS.isObjectExists(name):
            BLENDER_UTILS._INFO('error', '[ '+ name + ' ] not exists!')
            return 
        BLENDER_UTILS.selectMesh(name)
        BLENDER_UTILS.activeMesh(name)
        filetype = file[file.rfind('.')+1:].lower()
        if filetype == 'obj':
            bpy.ops.export_scene.obj(filepath=file, use_selection=True)
        if filetype == 'glb' or filetype == 'gltf':
            bpy.ops.export_scene.gltf(filepath=file, use_selection=True)
        if filetype == 'x3d':
            bpy.ops.export_scene.x3d(filepath=file, use_selection=True)
        if filetype == 'fbx':
            bpy.ops.export_scene.fbx(filepath=file, use_selection=True)
        if filetype == 'ply':
            bpy.ops.export_mesh.ply(filepath=file, use_selection=True)
        
    def exportMeshBySelect(file):
        if not BLENDER_UTILS.isString(file):
            BLENDER_UTILS._INFO('error', 'input a string!')
            return 
        if len( BLENDER_UTILS.getSelectMesh() ) == 0:
            BLENDER_UTILS._INFO('error', 'select at least one object!')
            return 
        filetype = file[file.rfind('.')+1:].lower()
        if filetype == 'obj':
            bpy.ops.export_scene.obj(filepath=file, use_selection=True)
        if filetype == 'glb' or filetype == 'gltf':
            bpy.ops.export_scene.gltf(filepath=file, use_selection=True)
        if filetype == 'x3d':
            bpy.ops.export_scene.x3d(filepath=file, use_selection=True)
        if filetype == 'fbx':
            bpy.ops.export_scene.fbx(filepath=file, use_selection=True)
        if filetype == 'ply':
            bpy.ops.export_mesh.ply(filepath=file, use_selection=True)
        
    
    def isObjectExists(ref):
        '''# from https://github.com/curtisjamesholt/EasyBPY
        '''
        if BLENDER_UTILS.isString(ref):
            if ref in bpy.data.objects:
                return True
            else:
                return False
        # redundant but for safety
        else:
            if ref.name in bpy.data.objects:
                return True
            else:
                return False

    def getMesh(ref):
        if not BLENDER_UTILS.isString(ref):
            BLENDER_UTILS._INFO('error','input a string!')
            return False
        if BLENDER_UTILS.isObjectExists(ref):
            return bpy.data.meshes[ref]
        else :
            BLENDER_UTILS._INFO('error','cannot find [ ' + ref + ' ]')
            return False
    def getObject(ref):
        if not BLENDER_UTILS.isString(ref):
            BLENDER_UTILS._INFO('error','input a string!')
            return False
        if BLENDER_UTILS.isObjectExists(ref):
            return bpy.data.objects[ref]
        else :
            BLENDER_UTILS._INFO('error','cannot find [ ' + ref + ' ]')
            return False
        
    def visualMesh(mesh_name = []):
        '''
        visual input mesh
        visualMesh(['Cube', 'Cube.001'])
        '''
        if len(mesh_name) == 0:
            pass
        else:
            objs = [x for x in bpy.context.scene.objects if x.type == 'MESH' ]
            if len(objs) == 0:
                print('not mesh in current scene')
            else:
                for o in objs: 
                    if o.name in mesh_name:
                        o.hide_set(False)

    def hideMesh(mesh_name = []):
        '''
        hide input mesh
        hideMesh(['Cube', 'Cube.001'])
        '''
        if len(mesh_name) == 0:
            pass
        else:
            objs = [x for x in bpy.context.scene.objects if x.type == 'MESH' ]
            if len(objs) == 0:
                print('not mesh in current scene')
            else:
                for o in objs: 
                    if o.name in mesh_name:
                        o.hide_set(True)

    def getSelectMesh():
        return bpy.context.selected_objects

    def getSelectMeshName():
        mesh = BLENDER_UTILS.getSelectMesh()
        return [x.name for x in mesh if x.type == 'MESH']

    def getActiveMesh():
        return bpy.context.view_layer.objects.active

    def selectMesh(mesh_name = []):
        '''
        select special mesh
        example:
            objs = selectMesh()
            objs = selectMesh(['Cube','Cube.001'])
        '''    
        if len(mesh_name) == 0:
            '''
            default select the whole mesh in the current scene
            '''
            for o in bpy.context.scene.objects:
                if o.type == 'MESH':
                    o.select_set(True)
                else:
                    pass
        else:
            '''
            select special mesh
            '''
            if BLENDER_UTILS.isString(mesh_name):
                print('>selectMesh mesh_name = ' + mesh_name)
                mesh_name = [mesh_name]
            else:
                for i in mesh_name:
                    pass
                    print('>selectMesh mesh_name list = ' + i)

            objs = [x for x in bpy.context.scene.objects if x.type == 'MESH']
            if len(objs) == 0:
                print('not find '+ mesh_name + ' in current scene')
                return {'CANCELLED'}
            else:
                for o in objs: 
                    if o.name in mesh_name:
                        o.select_set(True)
                        o.hide_set(False) # 不可以隐藏
                        print('> selectMesh Select ' + o.name)
                    else:
                        o.select_set(False)
                        o.hide_set(False)  # 不可以隐藏
                        print('> selectMesh Not Select ' + o.name)
                BLENDER_UTILS.activeMesh(mesh_name[0])
        return bpy.context.selected_objects

    def selectNoMesh():
        '''
        not select any mesh
        example:
            objs = selectNoMesh() 
        ''' 
        objs = [x for x in bpy.context.scene.objects if x.type == 'MESH']
        for o in objs:
            o.select_set(False) 
        return {'FINISHED'}

    def activeMesh(mesh_name):
        '''
        In Object Mode the last (de)selected item is called the “Active Object” and is outlined in yellow.
        There is at most one active object at any time.
        '''    
        if not BLENDER_UTILS.isString(mesh_name):
            BLENDER_UTILS._INFO('error', mesh_name+' is not a string')
            return 
        obj = [x for x in bpy.context.scene.objects if x.type == 'MESH' if x.name == mesh_name]
        if len(obj) == 0:
            BLENDER_UTILS._INFO('error', 'not find ['+ mesh_name + '], in current scene')
            return 
        bpy.context.view_layer.objects.active = obj[0]
        return obj[0]

    def renameMesh(mesh, new_name):
        if BLENDER_UTILS.isString(mesh):
            so = BLENDER_UTILS.getMesh(mesh)
            if so != False:
                BLENDER_UTILS._INFO('success', ' mesh find [ ' + mesh +' ]')
                so.name = new_name
            else:
                BLENDER_UTILS._INFO('error', ' mesh cannot find [ ' + mesh +' ]')
        else:
            BLENDER_UTILS._INFO('error', 'input a string!')
    def renameObject(mesh, new_name):
        if BLENDER_UTILS.isString(mesh):
            so = BLENDER_UTILS.getObject(mesh)
            if so != False:
                BLENDER_UTILS._INFO('success', ' object find [ ' + mesh +' ]')
                so.name = new_name
            else:
                BLENDER_UTILS._INFO('error', ' object cannot find [ ' + mesh +' ]')
        else:
            BLENDER_UTILS._INFO('error', 'input a string!')


    def deleteMeshInScene(scene_name = 'Scene', mesh_name = 'ALL_OBJECT'):
        '''
        delete all meshes (or special mesh_name object) in special scene
        删除特定场景中特定mesh，默认删除所有mesh
        '''
        x = [x.name for x in bpy.data.scenes]
        meshnames = BLENDER_UTILS.getAllMeshNameInScene(scene_name)
        if scene_name in x:
            # load scene firstly.
            bpy.context.window.scene = bpy.data.scenes.get(scene_name)
            if mesh_name != 'ALL_OBJECT':
                if BLENDER_UTILS.isString(mesh_name):
                    mesh_name = [mesh_name]
                for name in mesh_name:
                    if name in meshnames:
                        bpy.data.objects.remove( bpy.data.scenes[scene_name].objects[name] )
            else:
                BLENDER_UTILS.deleteAll()
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def getAllMeshInScene(scene_name = 'Scene'):
        '''
        get all mesh in target scene.
        获取特定场景中所有mesh，返回一个存储object的数组
        '''
        if BLENDER_UTILS.isString(scene_name):
            x = [x for x in bpy.data.scenes if x.name == scene_name]
            if len(x) == 1:
                return [x for x in bpy.data.scenes[scene_name].objects if x.type == 'MESH']
            else:
                BLENDER_UTILS._INFO('warn', 'not find scene : ' + scene_name + ', or your add too much scene')

    def getAllMeshNameInScene(scene_name = 'Scene'):
        '''
        get all meshes' name in target scene.
        获取特定场景中所有mesh的名字，返回一个存储object名字的数组
        '''
        return [x.name for x in BLENDER_UTILS.getAllMeshInScene(scene_name) ]

    def getAllMeshNameInCurrentScene():
        return BLENDER_UTILS.getAllMeshNameInScene(bpy.context.scene.name)

         
    def getAllImageName():
        '''
        get all Images' name in target scene.
        获取特定场景中所有Image的名字，返回一个存储object名字的数组
        '''
        return [x.name for x in bpy.data.images ]



    def getBlenderProjPath():
        fullpath = bpy.data.filepath
        pathelements = os.path.split(fullpath)
        workingdir = Path(pathelements[0])
        return workingdir
    

    def norm(x1,y1,z1,x2,y2,z2 ):
        return math.sqrt( math.pow(x1-x2, 2) + math.pow(y1-y2, 2) + math.pow(z1-z2, 2) )

    #region mesh Attributes
    # 这块过于具体，API见 https://docs.blender.org/api/current/bpy.types.Mesh.html#bpy.types.Mesh.polygons
    def getMeshVertex(mesh_name):
        '''
        https://docs.blender.org/api/current/bpy.types.MeshVertex.html#bpy.types.MeshVertex
        vertices的属性很多，常用如
        co: xyz坐标
        normal：法向量值
        可以直接修改值
        '''
        if not BLENDER_UTILS.isString(mesh_name):
            BLENDER_UTILS._INFO('error', 'input a string!')
            return 
        so = BLENDER_UTILS.getMesh(mesh_name)
        if so != False:
            return so.vertices
        else:
            return []
    def getMeshEdge(mesh_name):
        '''
        https://docs.blender.org/api/current/bpy.types.Mesh.html#bpy.types.Mesh.edges
        '''
        if not BLENDER_UTILS.isString(mesh_name):
            BLENDER_UTILS._INFO('error', 'input a string!')
            return 
        so = BLENDER_UTILS.getMesh(mesh_name)
        if so != False:
            return so.edges
        else:
            return []
    def getMeshFace(mesh_name):
        '''
        https://docs.blender.org/api/current/bpy.types.Mesh.html#bpy.types.Mesh.polygons
        '''
        if not BLENDER_UTILS.isString(mesh_name):
            BLENDER_UTILS._INFO('error', 'input a string!')
            return 
        so = BLENDER_UTILS.getMesh(mesh_name)
        if so != False:
            return so.polygons
        else:
            return []
    #endregion

    def getObjectVertexNumber(name):
        if BLENDER_UTILS.isObjectExists(name):
            return len(bpy.data.objects[name].data.vertices)

    #region mesh translation
    def getMeshCoords(objName, space = 'GLOBAL'):
        obj = BLENDER_UTILS.getObject(objName)
        if obj is False:
            return 
        if obj.mode == 'EDIT':
            v = bmesh.from_edit_mesh(obj.data).verts
        elif obj.mode == 'OBJECT':
            v = obj.data.vertices
        if space == 'GLOBAL':
            return [(obj.matrix_world @ v.co).to_tuple() for v in v]
        elif space == 'LOCAL':
            return [v.co.to_tuple() for v in v]

    # trans 以下变换，均为增量
    def _delta_translate(mesh_name, dv_x, dv_y, dv_z):
        if not BLENDER_UTILS.isNumber(dv_x) or  not BLENDER_UTILS.isNumber(dv_y)  or not BLENDER_UTILS.isNumber(dv_z):
            BLENDER_UTILS._INFO('error', 'input [ '+dv_x+','+ dv_y +',' + dv_z+' ] is not a number')
            return 
        so = BLENDER_UTILS.selectMesh(mesh_name)
        for o in so:
            BLENDER_UTILS.setMode(o.name, 'OBJECT')
            bpy.ops.transform.translate(value=(dv_x, dv_y, dv_z))
    def transXYZ_delta(mesh_name, dv):
        BLENDER_UTILS._delta_translate(mesh_name, dv, dv, dv)
    def transX_delta(mesh_name, dv):
        BLENDER_UTILS._delta_translate(mesh_name, dv, 0, 0)
    def transY_delta(mesh_name, dv):
        BLENDER_UTILS._delta_translate(mesh_name, 0, dv, 0)
    def transZ_delta(mesh_name, dv):
        BLENDER_UTILS._delta_translate(mesh_name, 0, 0, dv)
    # trans 以下变换，均为最终量，而非增量
    def _translation(mesh_name, dim, value):
        if not BLENDER_UTILS.isNumber(value):
            BLENDER_UTILS._INFO('error', 'input [ '+value+' ] is not a number')
            return 
        so = BLENDER_UTILS.selectMesh(mesh_name)
        for o in so:
            o.location[dim] = value
    def translationXYZ(mesh_name, value):
        BLENDER_UTILS.translationX(mesh_name, value)
        BLENDER_UTILS.translationY(mesh_name, value)
        BLENDER_UTILS.translationZ(mesh_name, value)
    def translationX(mesh_name, value):
        BLENDER_UTILS._translation(mesh_name, 0, value)
    def translationY(mesh_name, value):
        BLENDER_UTILS._translation(mesh_name, 1, value)
    def translationZ(mesh_name, value):
        BLENDER_UTILS._translation(mesh_name, 2, value)
    def getPosition(mesh_name):
        so = BLENDER_UTILS.selectMesh(mesh_name)
        eu = []
        for o in so:
            eu.append( [o.location[0],o.location[1],o.location[2]])
        return eu
    def setPosition(mesh_name, target_xyz = ()):
        if target_xyz == ():
            target_xyz = (0,0,0)
        so = BLENDER_UTILS.selectMesh(mesh_name)
        for o in so:
            o.location = target_xyz
    # rot 以下变换，均为最终量，而非增量
    def _rotation(mesh_name, dim, value):
        if not BLENDER_UTILS.isNumber(value):
            BLENDER_UTILS._INFO('error', 'input [ '+value+' ] is not a number')
            return 
        so = BLENDER_UTILS.selectMesh(mesh_name)
        for o in so:
            o.rotation_euler[dim] = value
    def rotationXYZ(mesh_name, vx, vy, vz):
        BLENDER_UTILS.rotationX(mesh_name, vx)
        BLENDER_UTILS.rotationY(mesh_name, vy)
        BLENDER_UTILS.rotationZ(mesh_name, vz)
    def rotationX(mesh_name, value):
        BLENDER_UTILS._rotation(mesh_name, 0, value)
    def rotationY(mesh_name, value):
        BLENDER_UTILS._rotation(mesh_name, 1, value)
    def rotationZ(mesh_name, value):
        BLENDER_UTILS._rotation(mesh_name, 2, value)   
    def getRotEuler(mesh_name):
        so = BLENDER_UTILS.selectMesh(mesh_name)
        eu = []
        for o in so:
            eu.append( [o.rotation_euler[0],o.rotation_euler[1],o.rotation_euler[2]])
        return eu
    # 以下为增量    
    def _delta_scale(mesh_name, dv_x, dv_y, dv_z):
        if not BLENDER_UTILS.isNumber(dv_x) or  not BLENDER_UTILS.isNumber(dv_y)  or not BLENDER_UTILS.isNumber(dv_z):
            BLENDER_UTILS._INFO('error', 'input [ '+dv_x+','+ dv_y +',' + dv_z+' ] is not a number')
            return 
        so = BLENDER_UTILS.selectMesh(mesh_name)
        for o in so:
            BLENDER_UTILS.setMode(o.name, 'OBJECT')
            bpy.ops.transform.resize(value=(dv_x, dv_y, dv_z))
    def scaleXYZ_delta(mesh_name, dv_x, dv_y, dv_z):
        BLENDER_UTILS._delta_scale(mesh_name, dv_x, dv_y, dv_z)
    def scaleX_delta(mesh_name, dv):
        BLENDER_UTILS._delta_scale(mesh_name, dv, 0, 0)
    def scaleY_delta(mesh_name, dv):
        BLENDER_UTILS._delta_scale(mesh_name, 0, dv, 0)
    def scaleZ_delta(mesh_name, dv):
        BLENDER_UTILS._delta_scale(mesh_name, 0, 0, dv)    
    # scale  以下变换，均为最终量，而非增量 
    def _scale(mesh_name, dim, value):
        if not BLENDER_UTILS.isNumber(value):
            BLENDER_UTILS._INFO('error', 'input [ '+value+' ] is not a number')
            return 
        so = BLENDER_UTILS.selectMesh(mesh_name)
        for o in so:
            o.scale[dim] = value
    def scaleXYZ(mesh_name, value):
        BLENDER_UTILS.scaleX(mesh_name, value)
        BLENDER_UTILS.scaleY(mesh_name, value)
        BLENDER_UTILS.scaleZ(mesh_name, value)
    def scaleX(mesh_name, value):
        BLENDER_UTILS._scale(mesh_name, 0, value)
    def scaleY(mesh_name, value):
        BLENDER_UTILS._scale(mesh_name, 1, value)
    def scaleZ(mesh_name, value):
        BLENDER_UTILS._scale(mesh_name, 2, value)   
    def getScale(mesh_name):
        so = BLENDER_UTILS.selectMesh(mesh_name)
        eu = []
        for o in so:
            eu.append( [o.scale[0],o.scale[1],o.scale[2]])
        return eu    

    #endregion

    #region scene
    def deleteScene(scene=None):
        """
        Delete scenes and all its objects.
        
        if scene includes all scenes, delete every scene and finally left a scene named 'Scene'
        
        Example:
        deleteScene()
        deleteScene(['Scene','Scene.001','Scene.002','Scene12'])
        """
        #
        # Sort out the scene object.
        ## at least keep one scene
        if len(bpy.data.scenes) <= 1:
            return 
        scene_list = []
        if scene is None:
            # Not specified: the whole scene.
            scene_list = [x for x in bpy.data.scenes]
        else:
            for _scene in scene:
                if BLENDER_UTILS.isString(_scene):
                    x = [x for x in bpy.data.scenes if x.name == _scene]
                    if len(x) > 0:
                        scene_list.append( bpy.data.scenes[_scene] )
                    else:
                        BLENDER_UTILS._INFO('warn', 'not find scene : ' + _scene)
        left_scene = None
        # if scene_list includes the whole scene, then keep the last scene
        if len( scene_list ) >= len( bpy.data.scenes ):
            left_scene = scene_list.pop()
        for _scene in scene_list:
            bpy.context.window.scene = _scene
            ## delete all objects
            BLENDER_UTILS.deleteAll()
            # Remove scene.
            bpy.data.scenes.remove( _scene )
        if left_scene != None:
            BLENDER_UTILS.deleteAll()
            bpy.context.scene.name  = 'Scene'
            
        
    def createScene(scene='Scene'):
        '''
        create scene
        '''
        new_scene = bpy.data.scenes.new(name=scene)
        #Make "My New Scene" the active one
        bpy.context.window.scene = new_scene    
        
        
    def loadScene(scene=None):
        '''
        load scene
        '''
        if scene is None:
            return 
        if BLENDER_UTILS.isString(scene):
            x = [x for x in bpy.data.scenes if x.name == scene]
            if len(x) > 0:
                bpy.context.window.scene = x[0]
    

    #endregion
    
    def getMode(obj_name):
        if BLENDER_UTILS.isString(obj_name):
            return bpy.data.objects[obj_name].mode
        else:
            print('ERROR. Get mode, need input string.')
            return {'CANCELLED'}

    #region mode
    def setMode(obj_name, mode_name):
        '''
        set object mode
        '''
        if mode_name not in ['OBJECT', 'EDIT', 'POSE', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'PARTICLE_EDIT', 'EDIT_GPENCIL', 'SCULPT_GPENCIL', 'PAINT_GPENCIL', 'VERTEX_GPENCIL', 'WEIGHT_GPENCIL']:
            BLENDER_UTILS._INFO('error', 'not find mode name = '+mode_name)
            return
        if not BLENDER_UTILS.isString(obj_name):
            BLENDER_UTILS._INFO('error', 'input: [ '+obj_name + ' ] is not string')
            return
        BLENDER_UTILS.selectMesh(obj_name)
        BLENDER_UTILS.activeMesh(obj_name)
        bpy.ops.object.mode_set(mode=mode_name)

    #region select mode 
    def setVertexSelect():
        bpy.context.tool_settings.mesh_select_mode = (True,False,False)
    def setEdgeSelect():
        bpy.context.tool_settings.mesh_select_mode = (False,True,False)
    def setFaceSelect():
        bpy.context.tool_settings.mesh_select_mode = (False,False,True)
    #endregion


    def setSoftEdge():
        # 修改为软边
        bpy.context.object.data.use_auto_smooth = False
        bpy.ops.object.shade_smooth()


    def bmesh_init(mesh_name):
        # 同一个对象的mesh\object两种访问方式
        me_object = BLENDER_UTILS.getObject(mesh_name)
        me_mesh = BLENDER_UTILS.getMesh(mesh_name)
        if me_object == False or me_mesh == False:
            BLENDER_UTILS._INFO('error', 'cannot find [ '+mesh_name+' ]')
            return False
        if me_object.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(me_mesh)
        elif me_object.mode == 'OBJECT':
            # New bmesh
            bm = bmesh.new()
            # load the mesh
            bm.from_mesh(me_mesh)
        return bm

    def bmesh_finish(bm, mesh_name):
        # 同一个对象的mesh\object两种访问方式
        me_object = BLENDER_UTILS.getObject(mesh_name)
        me_mesh = BLENDER_UTILS.getMesh(mesh_name)
        if me_object == False or me_mesh == False:
            BLENDER_UTILS._INFO('error', 'cannot find [ '+mesh_name+' ]')
            return False
        # write back
        if me_object.mode == 'EDIT':
            bmesh.update_edit_mesh(me_mesh)
        elif me_object.mode == 'OBJECT':
            bm.to_mesh(me_mesh)
            me_mesh.update() 

    def _bmesh_ops(bm):
        if bm == False:
            BLENDER_UTILS._INFO('error', 'bm is False')
            return False
        # subdivide
        bmesh.ops.subdivide_edges(bm,edges=bm.edges,cuts=1,use_grid_fill=True)


    def getBoundBox(object_name):
        """
        returns the corners of the bounding box of an object in world coordinates
        #  ________ 
        # |\       |\
        # |_\______|_\
        # \ |      \ |
        #  \|_______\|
        # 
        """
        ob = bpy.context.scene.objects[object_name]
        bbox_corners = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]

        return bbox_corners
    def checkCollision(box1, box2):
        """
        Check Collision of 2 Bounding Boxes
        box1 & box2 muss Liste mit Vector sein,
        welche die Eckpunkte der Bounding Box
        enthält
        #  ________ 
        # |\       |\
        # |_\______|_\
        # \ |      \ |
        #  \|_______\|
        # 
        #
        """
        # print('\nKollisionscheck mit:')

        x_max = max([e[0] for e in box1])
        x_min = min([e[0] for e in box1])
        y_max = max([e[1] for e in box1])
        y_min = min([e[1] for e in box1])
        z_max = max([e[2] for e in box1])
        z_min = min([e[2] for e in box1])
        # print('Box1 min %.2f, %.2f, %.2f' % (x_min, y_min, z_min))
        # print('Box1 max %.2f, %.2f, %.2f' % (x_max, y_max, z_max))

        x_max2 = max([e[0] for e in box2])
        x_min2 = min([e[0] for e in box2])
        y_max2 = max([e[1] for e in box2])
        y_min2 = min([e[1] for e in box2])
        z_max2 = max([e[2] for e in box2])
        z_min2 = min([e[2] for e in box2])
        # print('Box2 min %.2f, %.2f, %.2f' % (x_min2, y_min2, z_min2))
        # print('Box2 max %.2f, %.2f, %.2f' % (x_max2, y_max2, z_max2))

        isColliding = ((x_max >= x_min2 and x_max <= x_max2)
                    or (x_min <= x_max2 and x_min >= x_min2)) \
            and ((y_max >= y_min2 and y_max <= y_max2)
                or (y_min <= y_max2 and y_min >= y_min2)) \
            and ((z_max >= z_min2 and z_max <= z_max2)
                or (z_min <= z_max2 and z_min >= z_min2))

        # if isColliding:
            # print('Kollision!')
        return isColliding



# if __name__ == '__main__':
#     ut = BLENDER_UTILS
#     # initialize
#     ut.initBlender()

#     # create scene
#     ut.loadScene('Scene')

#     # add mesh into scene
#     # bpy.ops.mesh.primitive_cube_add( size= 1, location=(0,0,0) )
#     bpy.ops.mesh.primitive_cube_add( size= 1.5, location=(-1,0,0) )
#     # bpy.ops.mesh.primitive_cube_add( size= 0.5, location=(1,0,0) ) 

#     # 注意，创建object之后，会默认给最后创建的物体已active状态哦

#     # 注意，selectMesh获得的是mesh的object属性，object属性和mesh属性区别在于，mesh属性针对网格的一些属性，object则针对物体特性
#     # activeMesh('Cube.001') 
#     ut.selectMesh(['Cube'])
#     ut.activeMesh('Cube')

#     # 编辑模式前，激活并选择 
#     # setMode('Cube.001','EDIT')


#     # 对Object整体操作时，Object / Edit模式都可以
#     so = ut.selectMesh(['Cube','Cube.001'])
#     for o in so:
#         for i in range(0,3): 
#             o.location[2] += 1 

#     # 对一个顶点操作时，需要将mesh切回到Object模式
#     ut.setMode('Cube','OBJECT')
#     so = ut.getMeshVertex('Cube')
#     for i in so:
#         i.co.z += 2


#     # 加载obj模型
#     ut.importMesh("D:\\project\\tmp_proj\\shiki_proj\\blender_utils_py\\box_join.obj", "box_join_obj")
#     ut.importMesh("D:\\project\\tmp_proj\\shiki_proj\\blender_utils_py\\cone_join.fbx", "cone_join_fbx")

#     # 设置放置的xyz坐标
#     ut.translationXYZ(['box_join_obj','cone_join_fbx'], 0)

#     # 设置每步移动量
#     for i in range(0,10):
#         ut.transX_delta(['box_join_obj','cone_join_fbx'], 1)
#         ut.transX_delta('cone_join_fbx', 1)


#     # 一系列的bmesh操作，包裹在 bmesh_init 和 bmesh_finish 之间
#     bm = ut.bmesh_init('box_join_obj')
#     ut._bmesh_ops(bm)
#     ut.bmesh_finish(bm, 'box_join_obj')
    
#     # 保存两个mesh
#     ut.exportMeshByName("D:\\project\\tmp_proj\\shiki_proj\\blender_utils_py\\box_join_move.obj", "box_join_obj")
#     ut.exportMeshByName("D:\\project\\tmp_proj\\shiki_proj\\blender_utils_py\\cone_join_move.obj", "cone_join_fbx")


