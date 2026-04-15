# -*- coding: utf-8 -*-

import os
import bpy

from bpy.props import StringProperty, FloatProperty, IntProperty, CollectionProperty, EnumProperty

def get_objects_origin(context, target=None):
    """获取对象的原点坐标
    
    Args:
        context: Blender上下文
        target: 目标模型对象，如果为None则使用选中的对象
        
    Returns:
        tuple: 原点坐标 (x, y, z)
    """
    if target and target.type == 'MESH':
        # 如果指定了目标模型，则使用该模型的位置
        return (target.location.x, target.location.y, target.location.z)
    else:
        # 否则使用选中的对象
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            return (0, 0, 0)
        
        # 计算所有选中对象的平均位置作为原点
        total_x, total_y, total_z = 0, 0, 0
        for obj in selected_objects:
            total_x += obj.location.x
            total_y += obj.location.y
            total_z += obj.location.z
        
        count = len(selected_objects)
        return (total_x / count, total_y / count, total_z / count)

def validate_selection(context, operator):
    """验证选中的对象是否有效
    
    Args:
        context: Blender上下文
        operator: 操作符实例
        
    Returns:
        tuple: (bool, list, object, tuple) - (是否有效, 选中的对象, 目标模型, 原点坐标)
    """
    # 检查是否选中了模型
    if not context.selected_objects:
        operator.report({'ERROR'}, "请先选中至少一个模型")
        return (False, None, None, None)
    
    # 检查选中的对象是否包含可渲染的模型
    has_mesh = False
    for obj in context.selected_objects:
        if obj.type == 'MESH':
            has_mesh = True
            break
    
    if not has_mesh:
        operator.report({'ERROR'}, "请选中至少一个网格模型")
        return (False, None, None, None)
    
    # 保存当前选中的对象
    selected_objects = context.selected_objects.copy()
    
    # 获取选中的模型
    selected_meshes = [obj for obj in selected_objects if obj.type == 'MESH']
    target = selected_meshes[0] if selected_meshes else None
    
    # 获取模型原点坐标
    origin = get_objects_origin(context, target)
    
    return (True, selected_objects, target, origin)

def add_view(context, name, view_type, target, origin):
    """添加一个新的视角
    
    Args:
        context: Blender上下文
        name: 视角名称
        view_type: 视角类型
        target: 目标模型
        origin: 原点坐标
        
    Returns:
        object: 新创建的视角项
    """
    scene = context.scene
    view_item = scene.multi_view_views.add()
    
    # 设置视角属性
    view_item.name = name
    view_item.view_type = view_type
    view_item.target = target
    
    # 创建相机，基于模型原点
    origin_x, origin_y, origin_z = origin
    
    # 根据视角类型设置相机位置和旋转
    if view_type == "FRONT":
        camera_location = (origin_x, origin_y - 5, origin_z)
        camera_rotation = (1.5708, 0, 0)
    elif view_type == "BACK":
        camera_location = (origin_x, origin_y + 5, origin_z)
        camera_rotation = (1.5708, 0, 3.1416)
    elif view_type == "LEFT":
        camera_location = (origin_x - 5, origin_y, origin_z)
        camera_rotation = (1.5708, 0, -1.5708)
    elif view_type == "RIGHT":
        camera_location = (origin_x + 5, origin_y, origin_z)
        camera_rotation = (1.5708, 0, 1.5708)
    elif view_type == "TOP":
        camera_location = (origin_x, origin_y, origin_z + 5)
        camera_rotation = (0, 0, 0)
    elif view_type == "BOTTOM":
        camera_location = (origin_x, origin_y, origin_z - 5)
        camera_rotation = (3.1416, 0, 3.1416)
    elif view_type == "TOP-DOWN":
        camera_location = (origin_x, origin_y - 5, origin_z + 5)
        camera_rotation = (0.7854, 0, 0)
    elif view_type == "BOTTOM-UP":
        camera_location = (origin_x, origin_y - 5, origin_z - 5)
        camera_rotation = (2.3562, 0, 0)
    else:
        camera_location = (origin_x, origin_y - 5, origin_z)
        camera_rotation = (1.5708, 0, 0)
    
    bpy.ops.object.camera_add(location=camera_location, rotation=camera_rotation)
    camera = bpy.context.active_object
    camera.name = "Camera_{0}".format(len(scene.multi_view_views))
    view_item.camera_name = camera.name
    
    # 设置默认值
    view_item.pos_x, view_item.pos_y, view_item.pos_z = camera.location
    view_item.rot_x, view_item.rot_y, view_item.rot_z = camera.rotation_euler
    
    # 设置默认分辨率
    if view_type in ["FRONT", "BACK", "LEFT", "RIGHT"]:
        view_item.resolution_x = 1080
        view_item.resolution_y = 1920
    elif view_type in ["TOP", "BOTTOM"]:
        view_item.resolution_x = 1024
        view_item.resolution_y = 1024
    else:
        view_item.resolution_x = 1920
        view_item.resolution_y = 1080
    
    return view_item

def restore_selection(context, selected_objects):
    """恢复之前的选择状态
    
    Args:
        context: Blender上下文
        selected_objects: 之前选中的对象列表
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select_set(True)
    if selected_objects:
        context.view_layer.objects.active = selected_objects[0]

class MULTI_VIEW_ViewItem(bpy.types.PropertyGroup):
    name: StringProperty(name="名称")
    view_type: EnumProperty(
        name="视角类型",
        items=[
            ("FRONT", "正视图", "正面视角"), 
            ("BACK", "后视图", "背面视角"), 
            ("LEFT", "左视图", "左侧视角"), 
            ("RIGHT", "右视图", "右侧视角"), 
            ("TOP", "顶视图", "顶部视角"), 
            ("BOTTOM", "底视图", "底部视角"), 
            ("TOP-DOWN", "俯视图", "俯拍视角"), 
            ("BOTTOM-UP", "仰视图", "仰拍视角"), 
            ("CUSTOM", "自定义", "自定义视角")
        ],
        default="FRONT",
        update=lambda self, context: self.update_camera_position(context)
    )
    target: bpy.props.PointerProperty(name="目标模型", type=bpy.types.Object)
    pos_x: FloatProperty(name="位置X", default=0.0, update=lambda self, context: self.update_camera_location(context))
    pos_y: FloatProperty(name="位置Y", default=0.0, update=lambda self, context: self.update_camera_location(context))
    pos_z: FloatProperty(name="位置Z", default=0.0, update=lambda self, context: self.update_camera_location(context))
    rot_x: FloatProperty(name="旋转X", default=0.0, update=lambda self, context: self.update_camera_rotation(context))
    rot_y: FloatProperty(name="旋转Y", default=0.0, update=lambda self, context: self.update_camera_rotation(context))
    rot_z: FloatProperty(name="旋转Z", default=0.0, update=lambda self, context: self.update_camera_rotation(context))
    resolution_x: IntProperty(name="分辨率X", default=1920)
    resolution_y: IntProperty(name="分辨率Y", default=1080)
    camera_name: StringProperty(name="相机名称")
    
    def update_camera_position(self, context):
        if self.camera_name in bpy.data.objects:
            camera = bpy.data.objects[self.camera_name]
            # 获取模型原点坐标
            origin_x, origin_y, origin_z = get_objects_origin(context, self.target)
            # 根据视角类型设置相机位置和旋转
            if self.view_type == "FRONT":
                camera.location = (origin_x, origin_y - 5, origin_z)
                camera.rotation_euler = (1.5708, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "BACK":
                camera.location = (origin_x, origin_y + 5, origin_z)
                camera.rotation_euler = (1.5708, 0, 3.1416)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "LEFT":
                camera.location = (origin_x - 5, origin_y, origin_z)
                camera.rotation_euler = (1.5708, 0, -1.5708)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "RIGHT":
                camera.location = (origin_x + 5, origin_y, origin_z)
                camera.rotation_euler = (1.5708, 0, 1.5708)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "TOP":
                camera.location = (origin_x, origin_y, origin_z + 5)
                camera.rotation_euler = (0, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            elif self.view_type == "BOTTOM":
                camera.location = (origin_x, origin_y, origin_z - 5)
                camera.rotation_euler = (3.1416, 0, 3.1416)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            elif self.view_type == "TOP-DOWN":
                camera.location = (origin_x, origin_y - 5, origin_z + 5)
                camera.rotation_euler = (0.7854, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            elif self.view_type == "BOTTOM-UP":
                camera.location = (origin_x, origin_y - 5, origin_z - 5)
                camera.rotation_euler = (2.3562, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            else:
                camera.location = (origin_x, origin_y - 5, origin_z)
                camera.rotation_euler = (1.5708, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1920, 1080
    
    def update_camera_location(self, context):
        if self.camera_name in bpy.data.objects:
            camera = bpy.data.objects[self.camera_name]
            camera.location = (self.pos_x, self.pos_y, self.pos_z)
    
    def update_camera_rotation(self, context):
        if self.camera_name in bpy.data.objects:
            camera = bpy.data.objects[self.camera_name]
            camera.rotation_euler = (self.rot_x, self.rot_y, self.rot_z)

class MULTI_VIEW_OT_AddView(bpy.types.Operator):
    bl_idname = "multi_view.add_view"
    bl_label = "添加视角"
    bl_description = "添加一个新的视角"
    
    def execute(self, context):
        # 验证选择
        valid, selected_objects, target, origin = validate_selection(context, self)
        if not valid:
            return {'CANCELLED'}
        
        # 计算视角名称
        scene = context.scene
        view_name = "视角{0}".format(len(scene.multi_view_views) + 1)
        
        # 添加视角
        add_view(context, view_name, "FRONT", target, origin)
        
        # 恢复选择
        restore_selection(context, selected_objects)
        
        return {'FINISHED'}

class MULTI_VIEW_OT_RemoveView(bpy.types.Operator):
    bl_idname = "multi_view.remove_view"
    bl_label = "删除视角"
    bl_description = "删除选中的视角"

    def execute(self, context):
        scene = context.scene
        
        # 检查是否有视角可以删除
        if not scene.multi_view_views:
            self.report({'ERROR'}, "没有视角可以删除")
            return {'CANCELLED'}
        
        # 检查是否选中了视角
        index = scene.multi_view_active_index
        if index < 0 or index >= len(scene.multi_view_views):
            self.report({'ERROR'}, "请先选中一个视角")
            return {'CANCELLED'}
        
        # 删除对应的相机
        view_item = scene.multi_view_views[index]
        if view_item.camera_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[view_item.camera_name])
        # 删除视图项
        scene.multi_view_views.remove(index)
        if scene.multi_view_active_index >= len(scene.multi_view_views):
            scene.multi_view_active_index = max(0, len(scene.multi_view_views) - 1)
        
        return {'FINISHED'}

class MULTI_VIEW_OT_AddPresetThreeView(bpy.types.Operator):
    bl_idname = "multi_view.add_preset_three_view"
    bl_label = "添加三视图视角"
    bl_description = "添加三视图的视角"
    
    def execute(self, context):
        # 验证选择
        valid, selected_objects, target, origin = validate_selection(context, self)
        if not valid:
            return {'CANCELLED'}
        
        # 添加三视图视角
        add_view(context, "正面视角", "FRONT", target, origin)
        add_view(context, "左侧视角", "LEFT", target, origin)
        add_view(context, "顶部视角", "TOP", target, origin)
        
        # 恢复选择
        restore_selection(context, selected_objects)
        
        return {'FINISHED'}

class MULTI_VIEW_OT_AddPresetSixView(bpy.types.Operator):
    bl_idname = "multi_view.add_preset_six_view"
    bl_label = "添加六视图视角"
    bl_description = "添加六视图的视角"
    
    def execute(self, context):
        # 验证选择
        valid, selected_objects, target, origin = validate_selection(context, self)
        if not valid:
            return {'CANCELLED'}
        
        # 添加六视图视角
        add_view(context, "正面视角", "FRONT", target, origin)
        add_view(context, "背面视角", "BACK", target, origin)
        add_view(context, "左侧视角", "LEFT", target, origin)
        add_view(context, "右侧视角", "RIGHT", target, origin)
        add_view(context, "顶部视角", "TOP", target, origin)
        add_view(context, "底部视角", "BOTTOM", target, origin)
        
        # 恢复选择
        restore_selection(context, selected_objects)
        
        return {'FINISHED'}

class MULTI_VIEW_OT_ExportCurrentView(bpy.types.Operator):
    bl_idname = "multi_view.export_current_view"
    bl_label = "导出当前选中视图"
    bl_description = "导出当前选中的视图图片"
    
    def execute(self, context):
        scene = context.scene
        if not scene.multi_view_views:
            self.report({'ERROR'}, "至少需要一个视角才能导出")
            return {'CANCELLED'}
        
        if scene.multi_view_active_index < 0 or scene.multi_view_active_index >= len(scene.multi_view_views):
            self.report({'ERROR'}, "请先选择一个视角")
            return {'CANCELLED'}
        
        view_item = scene.multi_view_views[scene.multi_view_active_index]
        
        output_path = os.path.dirname(bpy.path.abspath(scene.render.filepath))
        if not output_path:
            output_path = bpy.path.abspath("//")  # 当前 .blend 文件所在目录
        
        # 保存原始设置
        original_camera = scene.camera
        original_transparent = scene.render.film_transparent
        original_resolution_x = scene.render.resolution_x
        original_resolution_y = scene.render.resolution_y
        original_world = scene.world
        
        # 设置背景透明
        scene.render.film_transparent = scene.multi_view_transparent
        
        # 设置场景世界
        if scene.multi_view_scene_world:
            if not scene.world:
                scene.world = bpy.data.worlds.new("MultiViewWorld")
            scene.world.use_nodes = True
            # nodes = scene.world.node_tree.nodes
            # links = scene.world.node_tree.links
            
            # # 找到背景节点
            # background_node = None
            # for node in nodes:
            #     if node.type == 'BACKGROUND':
            #         background_node = node
            #         break
            
            # if not background_node:
            #     background_node = nodes.new(type='ShaderNodeBackground')
            #     output_node = nodes.get('World Output')
            #     if output_node:
            #         links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
            
            # # 设置世界颜色和强度
            # background_node.inputs['Color'].default_value = scene.multi_view_world_color
            # background_node.inputs['Strength'].default_value = scene.multi_view_world_strength
        
        # 激活相机
        if view_item.camera_name in bpy.data.objects:
            camera = bpy.data.objects[view_item.camera_name]
            scene.camera = camera
            
            # # 更新相机位置和旋转
            # camera.location = (view_item.pos_x, view_item.pos_y, view_item.pos_z)
            # camera.rotation_euler = (view_item.rot_x, view_item.rot_y, view_item.rot_z)
            
            # 强制更新场景
            bpy.context.view_layer.update()
            
            # 设置分辨率
            scene.render.resolution_x = view_item.resolution_x
            scene.render.resolution_y = view_item.resolution_y
            
            # 渲染并保存
            filename = f"view_{view_item.name}_{view_item.view_type}.png"
            filepath = os.path.join(output_path, filename)
            bpy.ops.render.render()
            bpy.data.images['Render Result'].save_render(filepath=filepath)
            
            self.report({'INFO'}, f"已导出: {filename}")
        
        # 恢复原始设置
        scene.camera = original_camera
        scene.render.film_transparent = original_transparent
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.world = original_world
        
        return {'FINISHED'}

class MULTI_VIEW_OT_ExportAllViews(bpy.types.Operator):
    bl_idname = "multi_view.export_all_views"
    bl_label = "导出所有视图"
    bl_description = "导出所有视图的图片"

    def execute(self, context):
        scene = context.scene
        if not scene.multi_view_views:
            self.report({'ERROR'}, "至少需要一个视角才能导出")
            return {'CANCELLED'}
        
        output_path = os.path.dirname(bpy.path.abspath(scene.render.filepath))
        if not output_path:
            output_path = bpy.path.abspath("//")  # 当前 .blend 文件所在目录
        
        # 保存原始设置
        original_camera = scene.camera
        original_transparent = scene.render.film_transparent
        original_resolution_x = scene.render.resolution_x
        original_resolution_y = scene.render.resolution_y
        original_world = scene.world
        # 保存原始选中对象
        original_selected_objects = context.selected_objects.copy()
        original_active_object = context.view_layer.objects.active
        
        # 设置背景透明
        scene.render.film_transparent = scene.multi_view_transparent
        
        # 设置场景世界
        if scene.multi_view_scene_world:
            if not scene.world:
                scene.world = bpy.data.worlds.new("MultiViewWorld")
            scene.world.use_nodes = True
            # nodes = scene.world.node_tree.nodes
            # links = scene.world.node_tree.links
            
            # # 找到背景节点
            # background_node = None
            # for node in nodes:
            #     if node.type == 'BACKGROUND':
            #         background_node = node
            #         break
            
            # if not background_node:
            #     background_node = nodes.new(type='ShaderNodeBackground')
            #     output_node = nodes.get('World Output')
            #     if output_node:
            #         links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
            
            # # 设置世界颜色和强度
            # background_node.inputs['Color'].default_value = scene.multi_view_world_color
            # background_node.inputs['Strength'].default_value = scene.multi_view_world_strength
        
        # 清除选中对象，避免影响渲染
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = None
        
        # 导出每个视图
        total_views = len(scene.multi_view_views)
        for i, view_item in enumerate(scene.multi_view_views):
            # 激活相机
            if view_item.camera_name in bpy.data.objects:
                camera = bpy.data.objects[view_item.camera_name]
                scene.camera = camera
                
                # # 更新相机位置和旋转
                # camera.location = (view_item.pos_x, view_item.pos_y, view_item.pos_z)
                # camera.rotation_euler = (view_item.rot_x, view_item.rot_y, view_item.rot_z)
                
                # 强制更新场景
                bpy.context.view_layer.update()
                
                # 设置分辨率
                scene.render.resolution_x = view_item.resolution_x
                scene.render.resolution_y = view_item.resolution_y
                
                # 渲染并保存
                filename = f"view_{view_item.name}_{view_item.view_type}.png"
                filepath = os.path.join(output_path, filename)
                bpy.ops.render.render()
                bpy.data.images['Render Result'].save_render(filepath=filepath)
                
                # 显示进度
                progress = (i + 1) / total_views * 100
                self.report({'INFO'}, f"已导出: {filename} ({progress:.1f}%)")
        
        # 恢复原始设置
        scene.camera = original_camera
        scene.render.film_transparent = original_transparent
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.world = original_world
        # 恢复原始选中对象
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = original_active_object
        
        self.report({'INFO'}, "所有视图导出完成")
        return {'FINISHED'}

# ---------- 视角管理面板 ----------

class MULTI_VIEW_ExportPanel(bpy.types.Panel):
    bl_label = "多视角导出"
    bl_idname = "VIEW3D_PT_multi_view_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "多视角导出"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 视角管理
        box = layout.box()
        box.label(text="视角管理")
        
        row = box.row()
        row.template_list("UI_UL_list", "multi_view_views", scene, "multi_view_views", scene, "multi_view_active_index", type='DEFAULT', columns=2)
        
        # 当 align=True 时，列中的所有按钮（或布局元素）会被强制设置为相同的宽度（以该列中最宽的元素为准），使它们在水平方向上对齐。
        # 同时，元素之间的垂直间距会被移除，让它们紧密排列，没有额外的空白。
        btn_col = row.column()
        # 添加/删除按钮
        col = btn_col.column(align=True)
        col.operator("multi_view.add_view", icon="ADD", text="")
        col.operator("multi_view.remove_view", icon="REMOVE", text="")
        # 添加预设按钮
        col = btn_col.column(align=True)
        col.operator("multi_view.add_preset_three_view", icon="EVENT_THREEKEY", text="")
        col.operator("multi_view.add_preset_six_view", icon="EVENT_SIXKEY", text="")
        
        # 选中视角的设置
        if scene.multi_view_views and scene.multi_view_active_index < len(scene.multi_view_views):
            view_item = scene.multi_view_views[scene.multi_view_active_index]
            box = layout.box()
            box.label(text="视角设置")
            
            row = box.row()
            row.prop(view_item, "name", text="名称")
            
            row = box.row()
            row.prop(view_item, "view_type", text="视角类型")
            
            # 目标模型输入框（注释掉不显示）
            # row.prop(view_item, "target", text="目标模型")
            
            box.label(text="相机位置")
            row = box.row()
            row.prop(view_item, "pos_x", text="X")
            row.prop(view_item, "pos_y", text="Y")
            row.prop(view_item, "pos_z", text="Z")
            
            box.label(text="相机旋转")
            row = box.row()
            row.prop(view_item, "rot_x", text="X")
            row.prop(view_item, "rot_y", text="Y")
            row.prop(view_item, "rot_z", text="Z")
            
            box.label(text="分辨率（仅在导出时生效）")
            row = box.row()
            row.prop(view_item, "resolution_x", text="宽度")
            row.prop(view_item, "resolution_y", text="高度")
        
        # 渲染设置
        box = layout.box()
        box.label(text="渲染设置（仅在导出时生效）")
        
        row = box.row()
        row.prop(scene, "multi_view_transparent", text="背景透明")
        
        row = box.row()
        row.prop(scene, "multi_view_scene_world", text="场景世界（请在世界属性面板配置世界参数）")
        
        # if scene.multi_view_scene_world:
        #     row = box.row()
        #     row.prop(scene, "multi_view_world_color", text="世界颜色")
            
        #     row = box.row()
        #     row.prop(scene, "multi_view_world_strength", text="世界强度")
        
        # 导出
        box = layout.box()
        box.label(text="导出（请在输出属性面板配置保存参数）")
        
        col = box.column()
        col.operator("multi_view.export_current_view", text="导出选中视图")
        col.operator("multi_view.export_all_views", text="导出所有视图")
