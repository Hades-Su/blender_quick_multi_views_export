bl_info = {
    "name": "一键导出多视角图片",
    "author": "Hades Su",
    "version": (1, 2, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar > 多视角导出",
    "description": "一键导出3D模型的多个视角图片",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
from . import export_multi_view

classes = (
    export_multi_view.MULTI_VIEW_ViewItem,
    export_multi_view.MULTI_VIEW_ExportPanel,
    export_multi_view.MULTI_VIEW_OT_ExportCurrentView,
    export_multi_view.MULTI_VIEW_OT_ExportAllViews,
    export_multi_view.MULTI_VIEW_OT_AddView,
    export_multi_view.MULTI_VIEW_OT_RemoveView,
    export_multi_view.MULTI_VIEW_OT_AddPresetThreeView,
    export_multi_view.MULTI_VIEW_OT_AddPresetSixView,
)

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass  # 类已经注册，忽略错误
    
    # 检查属性是否已存在，避免重复创建
    if not hasattr(bpy.types.Scene, "multi_view_views"):
        bpy.types.Scene.multi_view_views = bpy.props.CollectionProperty(type=export_multi_view.MULTI_VIEW_ViewItem)
    if not hasattr(bpy.types.Scene, "multi_view_active_index"):
        bpy.types.Scene.multi_view_active_index = bpy.props.IntProperty()
    if not hasattr(bpy.types.Scene, "multi_view_transparent"):
        bpy.types.Scene.multi_view_transparent = bpy.props.BoolProperty(name="背景透明", default=False)
    if not hasattr(bpy.types.Scene, "multi_view_scene_lights"):
        bpy.types.Scene.multi_view_scene_lights = bpy.props.BoolProperty(name="场景灯光", default=False)
    if not hasattr(bpy.types.Scene, "multi_view_scene_world"):
        bpy.types.Scene.multi_view_scene_world = bpy.props.BoolProperty(name="场景世界", default=False)
    # if not hasattr(bpy.types.Scene, "multi_view_world_color"):
    #     bpy.types.Scene.multi_view_world_color = bpy.props.FloatVectorProperty(name="世界颜色", subtype='COLOR', size=4, default=(0.05, 0.05, 0.05, 1.0))
    # if not hasattr(bpy.types.Scene, "multi_view_world_strength"):
    #     bpy.types.Scene.multi_view_world_strength = bpy.props.FloatProperty(name="世界强度", default=1.0, min=0.0, max=1000.0)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except ValueError:
            pass  # 类未注册，忽略错误
    
    # 检查属性是否存在，避免删除不存在的属性
    if hasattr(bpy.types.Scene, "multi_view_views"):
        del bpy.types.Scene.multi_view_views
    if hasattr(bpy.types.Scene, "multi_view_active_index"):
        del bpy.types.Scene.multi_view_active_index
    if hasattr(bpy.types.Scene, "multi_view_transparent"):
        del bpy.types.Scene.multi_view_transparent
    if hasattr(bpy.types.Scene, "multi_view_scene_lights"):
        del bpy.types.Scene.multi_view_scene_lights
    if hasattr(bpy.types.Scene, "multi_view_scene_world"):
        del bpy.types.Scene.multi_view_scene_world
    # if hasattr(bpy.types.Scene, "multi_view_world_color"):
    #     del bpy.types.Scene.multi_view_world_color
    # if hasattr(bpy.types.Scene, "multi_view_world_strength"):
    #     del bpy.types.Scene.multi_view_world_strength

if __name__ == "__main__":
    register()