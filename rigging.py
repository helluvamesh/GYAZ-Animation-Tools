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


###############################################################################
###############################################################################

import bpy
from bpy.types import Operator, Panel, PropertyGroup, Scene
from .utils import report, get_pole_angle, set_end_mode, set_properties_context
from bpy.props import StringProperty, PointerProperty


class Op_GYAZ_SetupIKConstraint_GetActiveBone (Operator):
       
    bl_idname = "pose.setup_ik_constraint_get_active_bone"  
    bl_label = "Set Active Bone As"
    bl_description = "Set active pose bone (in pose mode)"
    
    prop_name: StringProperty (name='Prop Name', default='base_bone')
    
    #operator function
    def execute(self, context):      
        scene = bpy.context.scene
        owner = scene.gyaz_set_pole_angle
        
        if bpy.context.mode == 'POSE':
            prop = getattr (owner, self.prop_name)        
            if prop != None:
                prop = setattr (owner, self.prop_name, bpy.context.active_bone.name)
            
        return {'FINISHED'}
    
    
class Op_GYAZ_SetupIKConstraint (Operator):
       
    bl_idname = "pose.setup_ik_constraint"  
    bl_label = "Setup IK Constraint"
    bl_description = "Add an IK constraint to the constraint bone with all the settings done"
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):
        
        scene = bpy.context.scene
        owner = scene.gyaz_set_pole_angle
        
        start_mode = bpy.context.mode
        
        rig = bpy.context.object
        if rig.type == 'ARMATURE':
        
            if bpy.context.mode != 'EDIT_ARMATURE':
                bpy.ops.object.mode_set (mode='EDIT')
            ebones = rig.data.edit_bones
            
            base_bone_name = owner.base_bone
            constraint_bone_name = owner.constraint_bone
            ik_bone_name = owner.ik_bone
            pole_bone_name = owner.pole_bone
            
            base_bone = ebones.get (base_bone_name)
            constraint_bone = ebones.get (constraint_bone_name)
            ik_bone = ebones.get (ik_bone_name)
            pole_bone = ebones.get (pole_bone_name)
            
            # missing bones
            missing_bones = []
            if base_bone == None:
                missing_bones.append ('Base Bone')
            if constraint_bone == None:
                missing_bones.append ('Constraint Bone')
            if ik_bone == None:
                missing_bones.append ('IK Bone')
            if pole_bone == None:
                missing_bones.append ('Pole Bone')
            
            if len (missing_bones) > 0:
                set_end_mode (start_mode)
                popup ('Bones not found: '+list_to_visual_list(missing_bones), 'ERROR', 'Setup IK Constraints')
            else:
            
                # get pole angle
                pole_angle = get_pole_angle (base_bone, constraint_bone, pole_bone)
                
                # get ik constraint
                bpy.ops.object.mode_set (mode='POSE')
                pbones = rig.pose.bones
                cs = pbones[constraint_bone_name].constraints
                
                ik_constraint = None
                for c in cs:
                    if c.type == 'IK':
                        ik_constraint = c
                        break
                
                # create ik constraint, if not found any    
                if ik_constraint == None:
                    ik_constraint = cs.new (type='IK')
                
                # ik constraint settings
                c = ik_constraint  
                c.target = rig
                c.subtarget = ik_bone_name
                c.pole_target = rig
                c.pole_subtarget = pole_bone_name
                c.pole_angle = pole_angle
                c.chain_count = 2
                
                # set constraint bone to be the active bone
                bones = rig.data.bones
                bone = bones.get (constraint_bone_name)
                if bone != None:
                    bones.active = bone
                    bone.select = True
                
                # finalize    
                set_end_mode (start_mode)
                set_properties_context ('BONE_CONSTRAINT')
        
        #end of operator
        return {'FINISHED'}


class PG_GYAZ_SetPoleAngle (PropertyGroup):
    base_bone: StringProperty (name='Base Bone', default='', description='E.g.: upperarm, thigh')
    constraint_bone: StringProperty (name='Constraint Bone', default='', description='E.g.: forearm, shin')
    ik_bone: StringProperty (name='IK Target Bone', default='', description='E.g.: ik_hand, ik_foot')
    pole_bone: StringProperty (name='Pole Target Bone', default='', description='E.g.: target_elbow, target_knee')
    
    
class DATA_PT_GYAZ_SetPoleAngle (Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = 'Setup IK Constraint'
    bl_options = {'DEFAULT_CLOSED'}
    
    #add ui elements here
    def draw (self, context):
        lay = self.layout
        rig = bpy.context.object.data
        scene = bpy.context.scene
        owner = scene.gyaz_set_pole_angle
        row = lay.row (align=True)
        row.prop_search (owner, 'base_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='base_bone'
        row = lay.row (align=True)
        row.prop_search (owner, 'constraint_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='constraint_bone'
        row = lay.row (align=True)
        row.prop_search (owner, 'ik_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='ik_bone'
        row = lay.row (align=True)
        row.prop_search (owner, 'pole_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='pole_bone'
        lay.operator (Op_GYAZ_SetupIKConstraint.bl_idname)
         
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj is not None and (context.mode == 'OBJECT' or context.mode == 'POSE') and context.armature
    

class Op_GYAZ_AdjustActiveArmatureToSelected (Operator):
       
    bl_idname = "object.adjust_active_armature_to_selected"  
    bl_label = "Adjust Active Armature to Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):
        
        sel_objs = bpy.context.selected_objects
        if len(sel_objs) != 2:
            report(self, "Select two armatures", "WARNING")
        
        to_rig = bpy.context.active_object
        from_rig = None

        for obj in bpy.context.selected_objects:
            if obj != to_rig:
                from_rig = obj

        bpy.ops.object.mode_set(mode="EDIT")

        ebones_from = from_rig.data.edit_bones
        ebones_to = to_rig.data.edit_bones

        for ebone_from in ebones_from:
            ebone_to = ebones_to.get(ebone_from.name)
            if ebone_to is not None:
                ebone_to.head = ebone_from.head
                ebone_to.tail = ebone_from.tail
                ebone_to.roll = ebone_from.roll
                
        bpy.ops.object.mode_set(mode="OBJECT")
        
        #end of operator
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        if obj != None:
            return obj.type == "ARMATURE"
        else:
            return False

#######################################################
#######################################################

#REGISTER
#everything should be registeres here

def register():
    
    bpy.utils.register_class (PG_GYAZ_SetPoleAngle)
    Scene.gyaz_set_pole_angle = PointerProperty (type=PG_GYAZ_SetPoleAngle)
    
    bpy.utils.register_class (Op_GYAZ_SetupIKConstraint)
    bpy.utils.register_class (Op_GYAZ_SetupIKConstraint_GetActiveBone)
    bpy.utils.register_class (DATA_PT_GYAZ_SetPoleAngle) 
    
    bpy.utils.register_class (Op_GYAZ_AdjustActiveArmatureToSelected) 
    

def unregister ():
        
    bpy.utils.unregister_class (Op_GYAZ_SetupIKConstraint)
    bpy.utils.unregister_class (Op_GYAZ_SetupIKConstraint_GetActiveBone)
    bpy.utils.unregister_class (DATA_PT_GYAZ_SetPoleAngle)
    
    bpy.utils.unregister_class (Op_GYAZ_AdjustActiveArmatureToSelected)
    
    del Scene.gyaz_set_pole_angle     
    bpy.utils.unregister_class (PG_GYAZ_SetPoleAngle)
    


if __name__ == "__main__":   
    register()  
