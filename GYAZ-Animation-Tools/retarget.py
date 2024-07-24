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
from bpy.types import Operator
from bpy.props import *
from .utils import report
from .utils import popup


prefs = bpy.context.preferences.addons[__package__].preferences


class Op_GYAZ_RetargetAnimation (Operator):
       
    bl_idname = "anim.gyaz_retarget"  
    bl_label = "Retarget Animation"
    bl_description = "Selected: source (from) armature, active: target (to) armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    bone_name_mode: EnumProperty(
        name="Bone Names From",
        items=(
            ("TARGET", "TARGET RIG", ""),
            ("SOURCE", "SOURCE RIG", "")
        ),
        default="TARGET",
        description=""
    )
    location_bones: StringProperty (default="hips", name='Location Bones', description='E.g.: hips, some_other_bone')
    halve_frame_rate: BoolProperty (default=False, name='Halve Frame Rate')
    override_scene_frame_rate: IntProperty (default=30, name='Scene Frame Rate', description="Ignored if 'Halve Frame Rate' is False", min=1)
    bake: BoolProperty (default=True, name='Bake', description='Bake action to target rig')
    use_action_frame_range: BoolProperty (default=True, name="Use Action Frame Range")
    frame_start: IntProperty (default=1, name="Start Frame")
    frame_end: IntProperty (default=250, name="End Frame")
    use_target_bone_prefix: BoolProperty (default=False, name='Use Target Bone Prefix')
    target_bone_prefix: StringProperty (default="", name='Target Bone Prefix', description='target bone name = prefix + source bone name')
    correct_loc_keys: BoolProperty (default=False, name="Correct Location Keys", description="e.g. correct foot slipping")

    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)    
    
    #operator function
    def execute(self, context):

        location_bones = self.location_bones.split (', ')
        halve_frame_rate = self.halve_frame_rate
        override_scene_frame_rate = self.override_scene_frame_rate
        bake = self.bake
        target_bone_prefix = self.target_bone_prefix if self.use_target_bone_prefix else ""

        scene = bpy.context.scene
        
        sel_objs = bpy.context.selected_objects
        try:
            obj_types = [sel_objs[0].type, sel_objs[1].type]
        except:
            obj_types = []
        if not (len (sel_objs) == 2 and obj_types == ['ARMATURE', 'ARMATURE']):
            report (self, "Select two armatures.", "WARNING")
            return {"CANCELLED"}
        
        # get rig and source rig
        rig = bpy.context.active_object
        for obj in bpy.context.selected_objects:
            if obj != rig:
                source_rig = obj
        
        # make list of source rig bones
        if self.bone_name_mode == "SOURCE":
            bones = source_rig.data.bones
        else:
            bones = rig.data.bones
        bone_names = list( map( lambda x: x.name, bones) )

        matching_source_bone_names = []
        matching_target_bone_names = []
        source_bones = source_rig.data.bones
        target_bones = rig.data.bones
        for bone_name in bone_names:
            source_bone = source_bones.get(bone_name)
            target_bone_name = target_bone_prefix + bone_name
            target_bone = target_bones.get(target_bone_name)
            if source_bone is not None and target_bone is not None:
                matching_source_bone_names.append(source_bone.name)
                matching_target_bone_names.append(target_bone.name)

        if len(matching_source_bone_names) == 0:
            popup("No matching bones found.", 'ERROR', 'Retarget')
            return {"CANCELLED"}

        matching_source_location_bone_names = []
        matching_target_location_bone_names = []
        for source_bone_name in location_bones:
            source_bone = source_bones.get(source_bone_name)
            target_bone_name = target_bone_prefix + source_bone_name
            target_bone = target_bones.get(target_bone_name)
            if source_bone is None:
                popup("Location bone in source rig not found: " + source_bone_name, 'ERROR', 'Retarget')
                return {"CANCELLED"}
            elif target_bone is None:
                popup("Location bone in target rig not found: " + source_bone_name, 'ERROR', 'Retarget')
                return {"CANCELLED"}
            else:
                matching_source_location_bone_names.append(source_bone.name)
                matching_target_location_bone_names.append(target_bone.name)

        # constraint rig to source rig
        bpy.ops.object.mode_set (mode='POSE')
        pbones = rig.pose.bones

        target_bone_names = list( map( lambda x: target_bone_prefix + x, bone_names) )
        
        # halve framerate:
        # get active action
        if hasattr (source_rig, 'animation_data') == True:
            anim_data = source_rig.animation_data
            if anim_data.action != None:
                action = anim_data.action
                fcurves = action.fcurves
                
                # get first and last frame of action
                first_frame, last_frame = action.frame_range
                first_frame = int(first_frame)
                last_frame = int(last_frame)
                scene.frame_start = first_frame
                scene.frame_end = last_frame
                scene.frame_set (first_frame)
                if halve_frame_rate == True:                            
                    scene.render.fps = override_scene_frame_rate
                
                # halve frame rate
                if halve_frame_rate:
                    for fc in fcurves:
                        for key in fc.keyframe_points:
                            key.co.x = key.co.x * .5 + first_frame * .5
                            
                    # frame start, end
                    first_frame, last_frame = action.frame_range
                    scene.frame_start = int(first_frame)
                    scene.frame_end = int(last_frame)
                    scene.frame_set (int(first_frame))
                            
        
        # clear object transforms
        def clear_transform (object):
            setattr (object, 'location', [0, 0, 0])
            setattr (object, 'scale', [1, 1, 1])
            setattr (object, 'rotation_euler', [0, 0, 0])
            setattr (object, 'rotation_quaternion', [1, 0, 0, 0])
            setattr (object, 'rotation_axis_angle', [0, 0, 0, 0])
            
        clear_transform (rig)
        clear_transform (source_rig)
        

        for source_bone_name, target_bone_name in zip(matching_source_bone_names, matching_target_bone_names):
            pbone = pbones[target_bone_name]
                
            # constraint rig to source rig:
            # rotation
            c = pbone.constraints.new ('COPY_ROTATION')
            c.name = "GYAZ_retarget__48u2__rot"
            c.target = source_rig
            c.subtarget = source_bone_name
            
            # location
            if source_bone_name in matching_source_location_bone_names:
                c = pbone.constraints.new ('COPY_LOCATION')
                c.name = "GYAZ_retarget__48u2__loc"
                c.target = source_rig
                c.subtarget = source_bone_name
                
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

            first_frame = last_frame = None
            if self.use_action_frame_range:
                if hasattr (source_rig, 'animation_data') == True:
                    anim_data = source_rig.animation_data
                    if anim_data.action != None:
                        action = anim_data.action
                        first_frame = int(action.frame_range[0])
                        last_frame = int(action.frame_range[1])
            if not self.use_action_frame_range or first_frame is None:
                first_frame = self.frame_start
                last_frame = self.frame_end

            bpy.ops.nla.bake(frame_start=first_frame, frame_end=last_frame, only_selected=True, visual_keying=True, clear_constraints=False, clear_parents=False, use_current_action=False, bake_types={'POSE'})
            
            # clear constraints
            pbones = rig.pose.bones
            for target_bone_name in matching_target_bone_names:
                pbone = pbones[target_bone_name]
                for c in pbone.constraints:
                    if c.name.startswith("GYAZ_retarget"):
                        pbone.constraints.remove(c)
            
            # correct loc anim
            if self.correct_loc_keys:
                
                anim_data = rig.animation_data
                if anim_data.action != None:
                    
                    fcurves = anim_data.action.fcurves
                
                    for source_name, target_name in zip(matching_source_location_bone_names, matching_target_location_bone_names):
                        
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
