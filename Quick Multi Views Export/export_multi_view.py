import bpy
import os
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty, CollectionProperty, EnumProperty

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
            # 根据视角类型设置相机位置和旋转
            if self.view_type == "FRONT":
                camera.location = (0, -5, 0)
                camera.rotation_euler = (1.5708, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "BACK":
                camera.location = (0, 5, 0)
                camera.rotation_euler = (1.5708, 0, 3.1416)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "LEFT":
                camera.location = (-5, 0, 0)
                camera.rotation_euler = (1.5708, 0, -1.5708)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "RIGHT":
                camera.location = (5, 0, 0)
                camera.rotation_euler = (1.5708, 0, 1.5708)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1080, 1920
            elif self.view_type == "TOP":
                camera.location = (0, 0, 5)
                camera.rotation_euler = (0, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            elif self.view_type == "BOTTOM":
                camera.location = (0, 0, -5)
                camera.rotation_euler = (3.1416, 0, 3.1416)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            elif self.view_type == "TOP-DOWN":
                camera.location = (0, -5, 5)
                camera.rotation_euler = (0.7854, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            elif self.view_type == "BOTTOM-UP":
                camera.location = (0, -5, -5)
                camera.rotation_euler = (2.3562, 0, 0)
                self.pos_x, self.pos_y, self.pos_z = camera.location
                self.rot_x, self.rot_y, self.rot_z = camera.rotation_euler
                self.resolution_x, self.resolution_y = 1024, 1024
            else:
                camera.location = (0, -5, 0)
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
        # 检查是否选中了模型
        if not context.selected_objects:
            self.report({'ERROR'}, "请先选中至少一个模型")
            return {'CANCELLED'}
        
        # 检查选中的对象是否包含可渲染的模型
        has_mesh = False
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                has_mesh = True
                break
        
        if not has_mesh:
            self.report({'ERROR'}, "请选中至少一个网格模型")
            return {'CANCELLED'}
        
        scene = context.scene
        view_item = scene.multi_view_views.add()
        
        # 设置视角名称
        view_item.name = f"视角{len(scene.multi_view_views)}"
        
        # 创建相机
        bpy.ops.object.camera_add(location=(0, -5, 0), rotation=(1.5708, 0, 0))
        camera = bpy.context.active_object
        camera.name = f"Camera_{len(scene.multi_view_views)}"
        view_item.camera_name = camera.name
        
        # 设置默认值
        view_item.pos_x, view_item.pos_y, view_item.pos_z = camera.location
        view_item.rot_x, view_item.rot_y, view_item.rot_z = camera.rotation_euler
        
        # 设置默认分辨率
        if view_item.view_type in ["FRONT", "BACK", "LEFT", "RIGHT"]:
            view_item.resolution_x = 1080
            view_item.resolution_y = 1920
        elif view_item.view_type in ["TOP", "BOTTOM"]:
            view_item.resolution_x = 1024
            view_item.resolution_y = 1024
        else:
            view_item.resolution_x = 1920
            view_item.resolution_y = 1080
        
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


class MULTI_VIEW_OT_AddPresetView(bpy.types.Operator):
    bl_idname = "multi_view.add_preset_view"
    bl_label = "添加三视图视角"
    bl_description = "添加三视图的视角"
    
    def execute(self, context):
        # 检查是否选中了模型
        if not context.selected_objects:
            self.report({'ERROR'}, "请先选中至少一个模型")
            return {'CANCELLED'}
        
        # 检查选中的对象是否包含可渲染的模型
        has_mesh = False
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                has_mesh = True
                break
        
        if not has_mesh:
            self.report({'ERROR'}, "请选中至少一个网格模型")
            return {'CANCELLED'}
        
        # -----
        
        scene = context.scene
        
        # -- 添加正面视角 --
        
        front_view_item = scene.multi_view_views.add()
        
        # 设置正面视角名称
        front_view_item.name = "正面视角"
        front_view_item.view_type = "FRONT"
        
        # 创建相机
        bpy.ops.object.camera_add(location=(0, -5, 0), rotation=(1.5708, 0, 0))
        camera = bpy.context.active_object
        camera.name = f"Camera_{len(scene.multi_view_views)}"
        front_view_item.camera_name = camera.name
        
        # 设置默认值
        front_view_item.pos_x, front_view_item.pos_y, front_view_item.pos_z = camera.location
        front_view_item.rot_x, front_view_item.rot_y, front_view_item.rot_z = camera.rotation_euler
        
        # 设置默认分辨率
        front_view_item.resolution_x = 1080
        front_view_item.resolution_y = 1920
        
        # -- 添加左侧视角 --
        
        left_view_item = scene.multi_view_views.add()
        
        # 设置左侧视角名称
        left_view_item.name = "左侧视角"
        left_view_item.view_type = "LEFT"
        
        # 创建相机
        bpy.ops.object.camera_add(location=(-5, 0, 0), rotation=(1.5708, 0, -1.5708))
        camera = bpy.context.active_object
        camera.name = f"Camera_{len(scene.multi_view_views)}"
        left_view_item.camera_name = camera.name
        
        # 设置默认值
        left_view_item.pos_x, left_view_item.pos_y, left_view_item.pos_z = camera.location
        left_view_item.rot_x, left_view_item.rot_y, left_view_item.rot_z = camera.rotation_euler
        
        # 设置默认分辨率
        left_view_item.resolution_x = 1080
        left_view_item.resolution_y = 1920
        
        # -- 添加顶部视角 --
        
        top_view_item = scene.multi_view_views.add()
        
        # 设置顶部视角名称
        top_view_item.name = "顶部视角"
        top_view_item.view_type = "TOP"
        
        # 创建相机
        bpy.ops.object.camera_add(location=(0, 0, 5), rotation=(0, 0, 0))
        camera = bpy.context.active_object
        camera.name = f"Camera_{len(scene.multi_view_views)}"
        top_view_item.camera_name = camera.name
        
        # 设置默认值
        top_view_item.pos_x, top_view_item.pos_y, top_view_item.pos_z = camera.location
        top_view_item.rot_x, top_view_item.rot_y, top_view_item.rot_z = camera.rotation_euler
        
        # 设置默认分辨率
        top_view_item.resolution_x = 1024
        top_view_item.resolution_y = 1024
        
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
            nodes = scene.world.node_tree.nodes
            links = scene.world.node_tree.links
            
            # 找到背景节点
            background_node = None
            for node in nodes:
                if node.type == 'BACKGROUND':
                    background_node = node
                    break
            
            if not background_node:
                background_node = nodes.new(type='ShaderNodeBackground')
                output_node = nodes.get('World Output')
                if output_node:
                    links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
            
            # 设置世界颜色和强度
            background_node.inputs['Color'].default_value = scene.multi_view_world_color
            background_node.inputs['Strength'].default_value = scene.multi_view_world_strength
        
        # 激活相机
        if view_item.camera_name in bpy.data.objects:
            camera = bpy.data.objects[view_item.camera_name]
            scene.camera = camera
            
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
        
        # 设置背景透明
        scene.render.film_transparent = scene.multi_view_transparent
        
        # 设置场景世界
        if scene.multi_view_scene_world:
            if not scene.world:
                scene.world = bpy.data.worlds.new("MultiViewWorld")
            scene.world.use_nodes = True
            nodes = scene.world.node_tree.nodes
            links = scene.world.node_tree.links
            
            # 找到背景节点
            background_node = None
            for node in nodes:
                if node.type == 'BACKGROUND':
                    background_node = node
                    break
            
            if not background_node:
                background_node = nodes.new(type='ShaderNodeBackground')
                output_node = nodes.get('World Output')
                if output_node:
                    links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
            
            # 设置世界颜色和强度
            background_node.inputs['Color'].default_value = scene.multi_view_world_color
            background_node.inputs['Strength'].default_value = scene.multi_view_world_strength
        
        # 导出每个视图
        total_views = len(scene.multi_view_views)
        for i, view_item in enumerate(scene.multi_view_views):
            # 激活相机
            if view_item.camera_name in bpy.data.objects:
                camera = bpy.data.objects[view_item.camera_name]
                scene.camera = camera
                
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
        
        col = row.column(align=True)
        col.operator("multi_view.add_view", icon="ADD", text="")
        col.operator("multi_view.remove_view", icon="REMOVE", text="")
        col.operator("multi_view.add_preset_view", icon="PRESET_NEW", text="")
        
        # 选中视角的设置
        if scene.multi_view_views and scene.multi_view_active_index < len(scene.multi_view_views):
            view_item = scene.multi_view_views[scene.multi_view_active_index]
            box = layout.box()
            box.label(text="视角设置")
            
            row = box.row()
            row.prop(view_item, "name", text="名称")
            
            row = box.row()
            row.prop(view_item, "view_type", text="视角类型")
            
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
        row.prop(scene, "multi_view_scene_lights", text="场景灯光")
        
        row = box.row()
        row.prop(scene, "multi_view_scene_world", text="场景世界")
        
        if scene.multi_view_scene_world:
            row = box.row()
            row.prop(scene, "multi_view_world_color", text="世界颜色")
            
            row = box.row()
            row.prop(scene, "multi_view_world_strength", text="世界强度")
        
        # 导出
        box = layout.box()
        box.label(text="导出（请在输出面板设置输出参数）")
        
        col = box.column()
        col.operator("multi_view.export_current_view", text="导出当前选中视图")
        col.operator("multi_view.export_all_views", text="导出所有视图")
