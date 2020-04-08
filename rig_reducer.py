# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any laTter version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


##########################################################################################################
##########################################################################################################

import bpy
from bpy.types import Panel, Operator
from bpy.props import *
from .utils import report
from .utils import popup
from .utils import select_only
from .utils import get_all_descendant_bone_names


prefs = bpy.context.preferences.addons[__package__].preferences

# props

class GYAZ_ReduceRig_BoneItem (bpy.types.PropertyGroup):
    name: StringProperty (name='', description="'Bone to remove' / 'Vertex group to merge and remove'")
    name_children_only: BoolProperty (name='', default=False, description="Children only: only look for children, leave this bone and vertex group alone")
    merge_to: StringProperty (name='', description="Vertex group to merge to. Leave it unset for just removing bone and vertex group")
  
class GYAZ_ReduceRig_Props (bpy.types.PropertyGroup):

    def get_preset_names (self, context):
        names = []
        for n in range (0, 20):
            name = getattr (prefs, 'preset_name_'+str(n) )
            names.append ( (str(n), name, "")  )
        return names 

    def load_active_preset (self, context):

        scene = bpy.context.scene
        
        active_preset = getattr (scene.gyaz_reduce_rig, "active_preset") 
        
        index = int(active_preset)
        index_str = active_preset
        
        scene_bones = getattr (scene.gyaz_reduce_rig, "bones")         
        preset_bones = getattr (prefs, "preset_"+index_str)
        
        scene_bones.clear ()
        
        for preset_item in preset_bones:
            scene_item = scene_bones.add ()
            scene_item.name = preset_item.name
            scene_item.name_children_only = preset_item.name_children_only
            scene_item.merge_to = preset_item.merge_to

    active_preset: EnumProperty (name='', items=get_preset_names, default=None, update=load_active_preset)

    bones: CollectionProperty (type = GYAZ_ReduceRig_BoneItem)
    

class Op_GYAZ_ReduceRig_SavePreset (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_save_preset"  
    bl_label = "GYAZ Reduce Rig: Save Preset"
    bl_description = "Save preset"
    
    ui_name: StringProperty (name = 'name', default = '')
    
    #popup with properties
    def invoke (self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    #operator function
    def execute(self, context):
        ui_name = self.ui_name        
        scene = bpy.context.scene
            
        if ui_name != '':
            
            active_preset = getattr (scene.gyaz_reduce_rig, "active_preset") 
            
            index = int(active_preset)
            index_str = active_preset
            
            scene_bones = getattr (scene.gyaz_reduce_rig, "bones")          
            preset_bones = getattr (prefs, "preset_"+index_str)
            
            preset_bones.clear ()
            
            for scene_item in scene_bones:
                preset_item = preset_bones.add ()
                preset_item.name = scene_item.name
                preset_item.name_children_only = scene_item.name_children_only
                preset_item.merge_to = scene_item.merge_to

            setattr (prefs, 'preset_name_'+index_str, ui_name) 
            
            #save user preferences
            bpy.context.area.type = 'PREFERENCES'
            bpy.ops.wm.save_userpref()
            bpy.context.area.type = 'VIEW_3D'      

            
        return {'FINISHED'}
    

class Op_GYAZ_ReduceRig_ClearPreset (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_clear_preset"  
    bl_label = "GYAZ Reduce Rig: Clear Preset"
    bl_description = "Clear preset"
    
    #operator function
    def execute(self, context):      
        scene = bpy.context.scene
            
        active_preset = getattr (scene.gyaz_reduce_rig, "active_preset") 
        
        index = int(active_preset)
        index_str = active_preset
        
        scene_bones = getattr (scene.gyaz_reduce_rig, "bones")          
        preset_bones = getattr (prefs, "preset_"+index_str)
        
        preset_bones.clear ()
        scene_bones.clear ()
        
        prefs.property_unset ('preset_name_'+index_str)
        
        #save user preferences
        bpy.context.area.type = 'PREFERENCES'
        bpy.ops.wm.save_userpref()
        bpy.context.area.type = 'VIEW_3D'      

            
        return {'FINISHED'}


class Op_GYAZ_ReduceRig_Functions (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_functions"  
    bl_label = "GYAZ Reduce Rig: Functions"
    bl_description = ""
    
    ui_mode: EnumProperty(
        name = 'mode',
        items = (
            ('ADD', '', ''),
            ('REMOVE_ALL', '', '')
            ),
        default = "ADD")
    
    #operator function
    def execute(self, context):
        mode = self.ui_mode        
        scene = bpy.context.scene
        
        if mode == 'ADD':
            item = scene.gyaz_reduce_rig.bones.add ()
            item.name = ''
            item.marge_to = ''
        elif mode == 'REMOVE_ALL':
            scene.gyaz_reduce_rig.bones.clear ()
            
        return {'FINISHED'}
        
    
class Op_GYAZ_ReduceRig_RemoveItem (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_remove_item"  
    bl_label = "GYAZ Reduce Rig: Remove Item"
    bl_description = "Remove item"
    
    ui_index: IntProperty (name='', default=0)
    
    #operator function
    def execute(self, context):
        index = self.ui_index        
        scene = bpy.context.scene
        
        scene.gyaz_reduce_rig.bones.remove (index)
            
        return {'FINISHED'}


class Op_GYAZ_ReduceRig_SetNameAsActiveBone (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_set_prop_as_active_bone"  
    bl_label = "GYAZ Reduce Rig: Set Prop As Active Bone"
    bl_description = "Set active bone"
    
    ui_index: IntProperty (name='', default=0)
    
    #operator function
    def execute(self, context):
        index = self.ui_index        
        scene = bpy.context.scene
        
        if bpy.context.mode == 'POSE':        
            scene.gyaz_reduce_rig.bones[index].name = bpy.context.active_bone.name
            
        return {'FINISHED'}

    
class Op_GYAZ_ReduceRig_SetMergeToAsActiveBone (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_set_merge_to_as_active_bone"  
    bl_label = "GYAZ Reduce Rig: Set Merge To As Active Bone"
    bl_description = "Set active bone"
    
    ui_index: IntProperty (name='', default=0)
    
    #operator function
    def execute(self, context):
        index = self.ui_index        
        scene = bpy.context.scene
        
        if bpy.context.mode == 'POSE':        
            scene.gyaz_reduce_rig.bones[index].merge_to = bpy.context.active_bone.name
            
        return {'FINISHED'}
    
    
class Op_GYAZ_ReduceRig_MergeWeightsAndRemoveBones (bpy.types.Operator):
       
    bl_idname = "object.gyaz_reduce_rig_merge_weights_and_remove_bones"  
    bl_label = "GYAZ Reduce Rig: Merge Weights And Remove Bones"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    ui_remove_bones: BoolProperty (name='remove bones', default=True)    
    ui_merge_weights: BoolProperty (name='merge weights', default=True)
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)    
    
    #operator function
    def execute(self, context):
        
        merge_weights = self.ui_merge_weights
        remove_bones = self.ui_remove_bones
        scene = bpy.context.scene
        rig = bpy.context.active_object
        
        if rig.type != 'ARMATURE':
            report (self, 'Active object is not a mesh', 'WARNING')
        else:
        
            scene_bones = getattr (scene.gyaz_reduce_rig, "bones")                       
            
            for slot in scene_bones:
                if slot.name != '':
                    select_only (rig)
                    
                    descendants = []
                    
                    #make list of descendants
                    bone_name = slot.name
                    bones = rig.data.bones
                    bone = bones.get (bone_name)
                    if bone != None:
                        descendants = get_all_descendant_bone_names (bone)
                        
                        if slot.name_children_only == False:                                                                   
                            descendants.insert (0, bone.name)
                        
                        #remove bones
                        if remove_bones: 
                            bpy.ops.object.mode_set (mode="EDIT")
                            ebones = rig.data.edit_bones              
                            for name in descendants:
                                ebones.remove (ebones[name])
                    
                        #merge weights
                        if merge_weights:
                            bpy.ops.object.mode_set (mode="OBJECT")
                            meshes = []
                            if len(rig.children) > 0:
                                for child in rig.children:
                                    if child.type == 'MESH':
                                        meshes.append (child)
                                        
                            for name in descendants:
                                weight_to_merge = name
                                weight_to_merge_to = slot.merge_to
                                
                                if weight_to_merge_to != '':       
                                
                                    for mesh in meshes:
                                        select_only (mesh)
                                        #mix weights if mesh has those weights
                                        vgroups = mesh.vertex_groups
                                        if vgroups.get (weight_to_merge) != None:
                                            if vgroups.get (weight_to_merge_to) == None:
                                                vgroups.new (name=weight_to_merge_to)
                                            m = mesh.modifiers.new (type='VERTEX_WEIGHT_MIX', name="Mix Twist Weight")
                                            m.mix_mode = 'ADD'
                                            m.mix_set = 'ALL'
                                            m.vertex_group_a = weight_to_merge_to
                                            m.vertex_group_b = weight_to_merge
                                            bpy.ops.object.modifier_apply (apply_as='DATA', modifier="Mix Twist Weight")
                                            #delete surplus weights
                                            vgroups = mesh.vertex_groups
                                            vgroups.remove (vgroups[weight_to_merge])
            
            #finalize
            select_only (rig)   
            
        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):     
        return bpy.context.active_object != None

    
#UI

class VIEW3D_PT_GYAZ_ReduceRig (Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AnimTools'
    bl_label = 'Reduce Rig'    
    
    #add ui elements here
    def draw (self, context):
        scene = bpy.context.scene        
        lay = self.layout
        col = lay.column()
        col.label (text='Presets:')
        row = col.row (align=True)
        row.prop (scene.gyaz_reduce_rig, "active_preset", text='')
        row.operator (Op_GYAZ_ReduceRig_SavePreset.bl_idname, text='', icon='ADD')
        row.operator (Op_GYAZ_ReduceRig_ClearPreset.bl_idname, text='', icon='REMOVE')
        col = lay.column()
        col.label (text='Remove Bones:')
        row = col.row (align=True)
        row.scale_x = 2
        row.operator (Op_GYAZ_ReduceRig_Functions.bl_idname, text='', icon='ADD').ui_mode = 'ADD'
        row.operator (Op_GYAZ_ReduceRig_Functions.bl_idname, text='', icon='X').ui_mode = 'REMOVE_ALL'
        col = lay.column (align=True)
        for index, name in enumerate(scene.gyaz_reduce_rig.bones):
            row = col.row (align=True)
            row.prop_search(scene.gyaz_reduce_rig.bones[index], "name", bpy.context.active_object.data, "bones", icon='BONE_DATA')
            row.operator (Op_GYAZ_ReduceRig_SetNameAsActiveBone.bl_idname, text='', icon='EYEDROPPER').ui_index = index
            prop = scene.gyaz_reduce_rig.bones[index].name_children_only
            icon = 'ANIM' if prop == True else 'BLANK1'
            row.prop (scene.gyaz_reduce_rig.bones[index], "name_children_only", text='', icon=icon)
            row.separator ()
            row.prop_search(scene.gyaz_reduce_rig.bones[index], "merge_to", bpy.context.active_object.data, "bones", icon='FULLSCREEN_EXIT')
            row.operator (Op_GYAZ_ReduceRig_SetMergeToAsActiveBone.bl_idname, text='', icon='EYEDROPPER').ui_index = index
            row.separator ()
            row.operator (Op_GYAZ_ReduceRig_RemoveItem.bl_idname, text='', icon='REMOVE').ui_index = index
        lay.operator (Op_GYAZ_ReduceRig_MergeWeightsAndRemoveBones.bl_idname, text='Remove Bones and Merge Weights')


    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        if obj != None:
            if obj.type == 'ARMATURE':
                return bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE'
            else:
                return False
        else:
            return False

#######################################################
#######################################################

#REGISTER

def register():
    
    # props
    bpy.utils.register_class (GYAZ_ReduceRig_BoneItem)
    bpy.utils.register_class (GYAZ_ReduceRig_Props)        
    bpy.types.Scene.gyaz_reduce_rig = PointerProperty (type = GYAZ_ReduceRig_Props)     
    
    # operators  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_SavePreset)  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_ClearPreset)  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_Functions)  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_RemoveItem)  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_SetNameAsActiveBone)  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_SetMergeToAsActiveBone)  
    bpy.utils.register_class (Op_GYAZ_ReduceRig_MergeWeightsAndRemoveBones)   
    bpy.utils.register_class (VIEW3D_PT_GYAZ_ReduceRig)  
   

def unregister ():
    
    # props
    bpy.utils.unregister_class (GYAZ_ReduceRig_BoneItem)
    bpy.utils.unregister_class (GYAZ_ReduceRig_Props)      
    del bpy.types.Scene.gyaz_reduce_rig
    
    # operators
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_SavePreset)
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_ClearPreset)
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_Functions)
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_RemoveItem)
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_SetNameAsActiveBone)
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_SetMergeToAsActiveBone)
    bpy.utils.unregister_class (Op_GYAZ_ReduceRig_MergeWeightsAndRemoveBones)
    bpy.utils.unregister_class (VIEW3D_PT_GYAZ_ReduceRig)

  
if __name__ == "__main__":   
    register()   