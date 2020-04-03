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
from bpy.types import Operator, Panel
from bpy.props import *
from .utils import report
from .utils import popup
from .utils import list_to_visual_list


prefs = bpy.context.preferences.addons[__package__].preferences

class Op_GYAZ_RetargetAnimation (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_retarget"  
    bl_label = "Anim: Retarget"
    bl_description = "Selected: source (from) armature, active: target (to) armature"
    
    location_bones: StringProperty (default=prefs.location_bones, name='Location Bones', description='E.g.: hips, some_other_bone')
    halve_frame_rate: BoolProperty (default=prefs.halve_frame_rate, name='Halve Frame Rate')
    override_frame_rate: IntProperty (default=prefs.override_frame_rate, name='Scene Frame Rate', description="Ignored if 'Halve Frame Rate' is False", min=1)
    bake: BoolProperty (default=prefs.bake, name='Bake', description='Bake action to target rig')
    use_target_bone_prefix: BoolProperty (default=prefs.use_target_bone_prefix, name='Use Target Bone Prefix')
    target_bone_prefix: StringProperty (default=prefs.target_bone_prefix, name='Target Bone Prefix', description='target bone name = prefix + source bone name')
    correct_loc_keys: BoolProperty (default=prefs.correct_loc_keys, name="Correct Location Keys", description="e.g. correct foot slipping")
    
    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)    
    
    #operator function
    def execute(self, context):

        """SETTINGS"""

        location_bones = self.location_bones.split (', ')
        halve_frame_rate = self.halve_frame_rate
        override_frame_rate = self.override_frame_rate
        bake = self.bake

        ###

        scene = bpy.context.scene
        
        sel_objs = bpy.context.selected_objects
        try:
            obj_types = [sel_objs[0].type, sel_objs[1].type]
        except:
            obj_types = []
        if len (sel_objs) == 2 and obj_types == ['ARMATURE', 'ARMATURE']:
        
            # get rig and source rig
            rig = bpy.context.active_object
            for obj in bpy.context.selected_objects:
                if obj != rig:
                    source_rig = obj
            
            if source_rig.type == 'ARMATURE' and rig.type == 'ARMATURE':
            
                # make list of source rig bones
                bones = source_rig.data.bones
                source_bone_names = list( map( lambda x: x.name, bones) )

                # constraint rig to source rig
                bpy.ops.object.mode_set (mode='POSE')
                pbones = rig.pose.bones

                # check if rig has an equivalent bone to all source rig bones
                if self.use_target_bone_prefix == True:
                    target_bone_names = list( map( lambda x: self.target_bone_prefix + x, source_bone_names) )
                else:
                    target_bone_names = source_bone_names
                    
                missing_bones = list( filter( lambda x: x not in pbones, target_bone_names) )

                if len (missing_bones) > 0:
                    popup ('missing_bones: '+list_to_visual_list(missing_bones), 'ERROR')
                    
                else:
                        
                    """MAIN"""
                    
                    # halve framerate:
                    # get active action
                    if hasattr (source_rig, 'animation_data') == True:
                        anim_data = source_rig.animation_data
                        if anim_data.action != None:
                            action = anim_data.action
                            fcurves = action.fcurves
                            
                            # get first and last frame of action
                            first_frame, last_frame = action.frame_range
                            scene.frame_start = first_frame
                            scene.frame_end = last_frame
                            scene.frame_set (first_frame)
                            if halve_frame_rate == True:                            
                                scene.render.fps = override_frame_rate
                            
                            # halve frame rate
                            if halve_frame_rate:
                                for fc in fcurves:
                                    for key in fc.keyframe_points:
                                        key.co.x = key.co.x * .5 + first_frame * .5
                                        
                                # frame start, end
                                first_frame, last_frame = action.frame_range
                                scene.frame_start = first_frame
                                scene.frame_end = last_frame
                                scene.frame_set (first_frame)
                                        
                    
                    # clear object transforms
                    def clear_transform (object):
                        setattr (object, 'location', [0, 0, 0])
                        setattr (object, 'scale', [1, 1, 1])
                        setattr (object, 'rotation_euler', [0, 0, 0])
                        setattr (object, 'rotation_quaternion', [1, 0, 0, 0])
                        setattr (object, 'rotation_axis_angle', [0, 0, 0, 0])
                        
                    clear_transform (rig)
                    clear_transform (source_rig)
                    
                    
                    for name in source_bone_names:
                        if self.use_target_bone_prefix == True:
                            pbone = pbones[self.target_bone_prefix + name]
                        else:
                            pbone = pbones[name]
                            
                        # constraint rig to source rig:
                        # rotation
                        c = pbone.constraints.new ('COPY_ROTATION')
                        c.name = "GYAZ_retarget__48u2__rot"
                        c.target = source_rig
                        c.subtarget = name
                        
                        # location
                        if name in location_bones:
                            c = pbone.constraints.new ('COPY_LOCATION')
                            c.name = "GYAZ_retarget__48u2__loc"
                            c.target = source_rig
                            c.subtarget = name

                    if hasattr (source_rig, 'animation_data') == True:
                        anim_data = source_rig.animation_data
                        if anim_data.action != None:
                            
                            # select target rig
                            bpy.ops.object.mode_set (mode='OBJECT')
                            bpy.ops.object.select_all (action='DESELECT')
                            rig.select_set (True)
                            bpy.context.view_layer.objects.active = rig
                                
                            # select relevant bones
                            bpy.ops.object.mode_set (mode='POSE')
                            bpy.ops.pose.select_all (action='DESELECT')
                            for index, bone_name in enumerate(target_bone_names):
                                rig.data.bones[bone_name].select = True
                                if index == 0:
                                    rig.data.bones.active = rig.data.bones[bone_name]
                            
                            if bake == True:
                                
                                # bake
                                bpy.ops.object.mode_set (mode='POSE')
                                bpy.ops.nla.bake(frame_start=first_frame, frame_end=last_frame, only_selected=True, visual_keying=True, clear_constraints=True, clear_parents=False, use_current_action=False, bake_types={'POSE'})
                            
                                # correct loc anim
                                if self.correct_loc_keys:
                                    
                                    anim_data = rig.animation_data
                                    if anim_data.action != None:
                                        
                                        fcurves = anim_data.action.fcurves
                                    
                                        for source_name in location_bones:
                                            
                                            target_name = self.target_bone_prefix + source_name if self.use_target_bone_prefix else source_name
                                            data_path = 'pose.bones["' + target_name + '"].location'
                                            source_loc_z = (source_rig.data.bones[source_name].head @ source_rig.matrix_world)[2]
                                            target_loc_z = (rig.data.bones[target_name].head @ rig.matrix_world)[2]
                                            
                                            if source_loc_z != 0 and target_loc_z != 0:
                                                
                                                multiplier = target_loc_z / source_loc_z
                                                
                                                for fc in fcurves:
                                                    if fc.data_path == data_path:
                                                        for key in fc.keyframe_points:
                                                            key.co.y *= multiplier
                                
                                
            bpy.ops.object.mode_set (mode='OBJECT')
                                
        else:
            report (self, "Select two armatures.", "WARNING")
            
                                              
        return {'FINISHED'}

    
#######################################################
#######################################################

#REGISTER

def register():
    bpy.utils.register_class (Op_GYAZ_RetargetAnimation)                                                       
   

def unregister ():
    bpy.utils.unregister_class (Op_GYAZ_RetargetAnimation)

  
if __name__ == "__main__":   
    register()   
