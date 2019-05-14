import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os
from ..bp_lib import bp_types, bp_utils

class ASSEMBLY_OT_create_new_assembly(Operator):
    bl_idname = "bp_assembly.create_new_assembly"
    bl_label = "Create New Assembly"
    bl_description = "This will create a new assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = bp_types.Assembly()
        assembly.create_assembly()
        assembly.obj_x.location.x = 1
        assembly.obj_y.location.y = 1
        assembly.obj_z.location.z = 1
        assembly.obj_bp.select_set(True)
        context.view_layer.objects.active = assembly.obj_bp
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the assembly to add.")
        layout.prop(self,'assembly_name')

class ASSEMBLY_OT_add_object(Operator):
    bl_idname = "bp_assembly.add_object"
    bl_label = "Add Object to Assembly"
    bl_description = "This will add a new object to the assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")

    object_name: StringProperty(name="Object Name",default="New Object")
    object_type: bpy.props.EnumProperty(name="Object Type",
                                        items=[('EMPTY',"Empty","Add an Empty Object"),
                                               ('MESH',"Mesh","Add an Mesh Object"),
                                               ('CURVE',"Curve","Add an Curve Object"),
                                               ('LIGHT',"Light","Add an Light Object")],
                                        default='EMPTY')
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = bp_types.Assembly(context.view_layer.active_layer_collection.collection)
        if self.object_type == 'EMPTY':
            assembly.add_empty("New Empty")

        if self.object_type == 'MESH':
            obj_mesh = bp_utils.create_cube_mesh(self.object_name,(assembly.obj_x.location.x,
                                                                   assembly.obj_y.location.y,
                                                                   assembly.obj_z.location.z))
            
            assembly.add_object(obj_mesh)

            # MAKE NORMALS CONSISTENT
            context.view_layer.objects.active = obj_mesh
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()

        if self.object_type == 'CURVE':
            pass           
        if self.object_type == 'LIGHT':
            pass
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'object_type',expand=True)
        layout.prop(self,'object_name')

class ASSEMBLY_OT_connect_mesh_to_hooks_in_assembly(Operator):
    bl_idname = "bp_assembly.connect_meshes_to_hooks_in_assembly"
    bl_label = "Connect Mesh to Hooks In Assembly"
    bl_options = {'UNDO'}
    
    obj_name = StringProperty(name="Object Name")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        coll = bp_utils.get_assembly_collection(obj)
        assembly = bp_types.Assembly(coll)

        hooklist = []
        for child in coll.objects:
            if child.type == 'EMPTY' and 'obj_prompts' not in child:
                hooklist.append(child)
        
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
        
        bp_utils.apply_hook_modifiers(context,obj)
        for vgroup in obj.vertex_groups:
            for hook in hooklist:
                if hook.name == vgroup.name:
                    bp_utils.hook_vertex_group_to_object(obj,vgroup.name,hook)

            # if vgroup.name == 'X Dimension':
            #     bp_utils.hook_vertex_group_to_object(obj,'X Dimension',assembly.obj_x)
            # elif vgroup.name == 'Y Dimension':
            #     bp_utils.hook_vertex_group_to_object(obj,'Y Dimension',assembly.obj_y)
            # elif vgroup.name == 'Z Dimension':
            #     bp_utils.hook_vertex_group_to_object(obj,'Z Dimension',assembly.obj_z)
            # else:
            #     for hook in hooklist:
            #         if hook.mv.name_object == vgroup.name:
            #             bp_utils.hook_vertex_group_to_object(obj,vgroup.name,hook)
                
        obj.lock_location = (True,True,True)
                
        return {'FINISHED'}

classes = (
    ASSEMBLY_OT_create_new_assembly,
    ASSEMBLY_OT_add_object,
    ASSEMBLY_OT_connect_mesh_to_hooks_in_assembly
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()