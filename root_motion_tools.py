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

#SETTINGS-SETTINGS-SETTINGS-SETTINGS:

import bpy
from .utils import popup_lines as popup


#bones
prefs = bpy.context.preferences.addons[__package__].preferences

#drive_bone = prefs.bone_prefix+prefs.drive_bone
root_bone = prefs.root_bone
#left_toe = prefs.bone_prefix+prefs.toes+prefs.bone_left_suffix
#right_toe = prefs.bone_prefix+prefs.toes+prefs.bone_right_suffix


def clear_transformation (object):
    setattr (object, 'location', [0, 0, 0])
    setattr (object, 'scale', [1, 1, 1])
    setattr (object, 'rotation_euler', [0, 0, 0])
    setattr (object, 'rotation_quaternion', [1, 0, 0, 0])
    setattr (object, 'rotation_axis_angle', [0, 0, 0, 0])


###############################################################################
###############################################################################

from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty, IntProperty, FloatProperty, EnumProperty, BoolProperty
import os
from .utils import lerp
from .utils import report


#check for drive bone and animation data
def safety_check_1 (main, bone_name, bone_name_in_main_argument):

    checklist = []                
    obj = bpy.context.active_object

    #drive bone exists?
    bones = obj.data.bones
    if bones.find(bone_name) != -1:
        checklist.append (True)
    else:
        popup (["bone: '"+str(bone_name)+"' not found"], "ERROR")

    #has animation?
    if obj.animation_data is not None and obj.animation_data.action is not None:
        checklist.append (True)
    else:
        popup (["Armature has no animation."], "ERROR")
        
    if len (checklist) == 2:
        if bone_name_in_main_argument == False:
            main ()
        if bone_name_in_main_argument == True:
            main (bone_name)
            
            
#check for drive bone and animation data
def safety_check_2 (main, bone_name, bone_name_1, bone_name_2, bone_name_in_main_argument):

    checklist = []                
    obj = bpy.context.active_object

    #drive bone exists?
    bones = obj.data.bones
    if bones.find(bone_name) != -1 and bones.find(bone_name_1) != -1 and bones.find(bone_name_2) != -1:
        checklist.append (True)
    else:
        lines = []
        if bones.find(bone_name) == -1:
            lines.append ("bone: '"+str(bone_name)+"' not found")
        if bones.find(bone_name_1) == -1:
            lines.append ("bone: '"+str(bone_name_1)+"' not found")
        if bones.find(bone_name_2) == -1:
            lines.append ("bone: '"+str(bone_name_2)+"' not found")
            
        popup (lines, "ERROR")

    #has animation?
    if obj.animation_data is not None and obj.animation_data.action is not None:
        checklist.append (True)
    else:
        popup (["Armature has no animation."], "ERROR")
        
    if len (checklist) == 2:
        if bone_name_in_main_argument == False:
            main ()
        if bone_name_in_main_argument == True:
            main (bone_name, bone_name_1, bone_name_2)       


##############################################
##############################################

#OPERATORS    

#EXTRACT ROOT MOTION: VISUALIZE
class Op_GYAZ_ExtractRootMotion_Visualize (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_visualize"  
    bl_label = "Extract Root Motion: Visualize"
    bl_description = "Append capsule and arrow and parent them to armauture object"

    
    #operator function
    def execute(self, context):
        
        def main (obj_name):
        
            bpy.ops.object.mode_set (mode='OBJECT')
            
            filepath = os.path.dirname(__file__) + "/animation_tools_props.blend"
            
            # append, set to true to keep the link to the original file
            link = False
            # link all objects starting with 'obj_name'
            with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name.endswith(obj_name)]
            
            scene = bpy.context.scene
            root = bpy.context.active_object
            
            #get Unit Scale
            uSystem= scene.unit_settings.system
            uScale = scene.unit_settings.scale_length
            newScale = 1/uScale


            bpy.ops.object.select_all(action='DESELECT')
            #link object to current scene with correct scale
            for obj in data_to.objects:
                if obj is not None:
                    #link
                    scene.collection.objects.link (obj)
                    #set scale
                    obj['original_scale'] = obj.scale
                    oriScale = obj['original_scale']
                    obj.select_set (True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.scale_clear()
                    obj.scale[0] = obj.scale[1]*newScale*oriScale[0]
                    obj.scale[1] = obj.scale[1]*newScale*oriScale[1]
                    obj.scale[2] = obj.scale[2]*newScale*oriScale[2]
                    
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    
                    del obj['original_scale']
                    obj.parent = root
                    bpy.ops.object.select_all(action='DESELECT')    
            
            
            root.select_set (True)
            bpy.context.view_layer.objects.active = root
        
        has_ob = False
        obj_name = "capsule_ERM"
        root = bpy.context.active_object
        children = root.children
        for child in children:
            if bpy.data.objects.get(child.name) is not None:
                if child.name.startswith (obj_name) == True:
                    popup (["You already have a capsule parented to your armature."], "INFO")
                    has_ob = True
        if has_ob == False:
            main (obj_name)
        
        
        #end of operator
        return {'FINISHED'}
    
        
#EXTRACT ROOT MOTION: BASE
class Op_GYAZ_ExtractRootMotion_Base (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_base"  
    bl_label = "Extract Root Motion: Base"
    bl_description = "Extract root motion: location XY and rotation Z and applies it to the armature object. Set first and last frame on timeline"
    
    #properties    
    ui_modes: EnumProperty(
        items=(
            ('True', "Loc XY and Rot Z", ""),
            ('False', "Loc XY", "")
            ),
        default='True',
        name="Mode",
        description="Extract Location XY and Rotation Z or only Location XY"
        )
        
    ui_drive_bone: StringProperty(
        name='Drive Bone',
        default=prefs.bone_prefix+prefs.drive_bone,
        description="Bone that moves the whole skeleton, e.g. hips or pelvis")

    ui_drive_bone_forward: EnumProperty(
        items=(
            ('+X', "+X", ""),
            ('-X', "-X", ""),
            ('+Y', "+Y", ""),
            ('-Y', "-Y", ""),
            ('+Z', "+Z", ""),
            ('-Z', "-Z", "")
            ),
        default=prefs.drive_bone_forward,
        name="Drive Bone Forward Axis",
        description="Drive bone's axis that points forward"
        )
    
    ui_target_offset: FloatProperty(
        default=5.0, 
        name="Target Offset", 
        description="Offset of orientation target in meters")
    

    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    #operator function
    def execute(self, context):
        
        scene = bpy.context.scene
        driveBone_name = self.ui_drive_bone
        
        def main ():
            
            #SETTINGS-SETTINGS-SETTINGS-SETTINGS
            #NAME OF DRIVE-BONE
            #bone axis pointing forward: positive or negative z
            driveBone_fwd = self.ui_drive_bone_forward

            target_offset = self.ui_target_offset

            calculate_rotation = self.ui_modes
            
            #END OF SETTINGS
            
            #HOW TO USE-HOW TO USE-HOW TO USE
            #Make sure you're at the first frame of animation at the beginning!!!
            #Set the 'Start' and the 'End' of the animation on the timeline
            #Select your armature

            #END OF HOW TO USE

            #get selected object as root
            root = bpy.context.object
            #define driveBone as bone
            driveBone = root.data.bones[driveBone_name]
            #define driveBone as pose bone
            driveBone_pb = bpy.data.objects[root.name].pose.bones[driveBone.name]

            #root.rotation_mode = 'QUATERNION'

            #get scene
            scene = bpy.context.scene
            #get first and last frame of animation
            firstFrame = scene.frame_start
            lastFrame = scene.frame_end
            #jump to first frame of animation
            scene.frame_set (firstFrame)
            #unit_scale
            unit_scale = scene.unit_settings.scale_length
            #target offset    
            target_offset /= unit_scale
            
            #drive bone forward
            if driveBone_fwd == '+X':
                x = [target_offset, True]
                y = [0, False]
                z = [0, False]
            elif driveBone_fwd == '-X':
                x = [target_offset * -1, True]
                y = [0, False]
                z = [0, False]
            elif driveBone_fwd == '+Y':
                x = [0, False]
                y = [target_offset, True]
                z = [0, False]
            elif driveBone_fwd == '-Y':
                x = [0, False]
                y = [target_offset * -1, True]
                z = [0, False]            
            elif driveBone_fwd == '+Z':
                x = [0, False]
                y = [0, False]
                z = [target_offset, True]
            elif driveBone_fwd == '-Z':
                x = [0, False]
                y = [0, False]
                z = [target_offset * -1, True]
             
            bpy.ops.object.mode_set (mode='OBJECT')

            #ORIENTATION TARGET
            bpy.ops.object.add(type='EMPTY', location=(0, 0, 0))
            bpy.context.active_object.name = "ERM_orientation_target"
            orient_target = scene.objects ["ERM_orientation_target"]

            #initial position
            c = orient_target.constraints.new ('COPY_LOCATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'

            #apply visual transform
            bpy.ops.object.mode_set (mode='OBJECT')
            bpy.ops.object.select_all (action='DESELECT')
            orient_target.select_set (True)
            bpy.context.view_layer.objects.active = scene.objects[orient_target.name]

            bpy.ops.object.visual_transform_apply ()

            orient_target.constraints.remove (c)
            
            orient_target.parent = root
            orient_target.parent_type = 'BONE'
            orient_target.parent_bone = driveBone.name

            #offset
            c = orient_target.constraints.new ('COPY_ROTATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'

            bpy.ops.transform.translate (value=(x[0], y[0], z[0]), constraint_axis=(x[1], y[1], z[1]), orient_type='LOCAL', mirror=False, use_proportional_edit=False)

            #bake orient target
            bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})


            #ROTATOR
            bpy.ops.object.add(type='EMPTY', location=(0, 0, 0))
            bpy.context.active_object.name = "ERM_rotator"
            rotator = scene.objects ["ERM_rotator"]
            rotator.empty_display_type = "ARROWS"
            rotator.rotation_mode = 'QUATERNION'
            rotator.show_in_front = True

            #copy location: driveBone
            c = rotator.constraints.new ('COPY_LOCATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'

            #locked track to
            c = rotator.constraints.new ('LOCKED_TRACK')
            c.target = orient_target
            c.track_axis = 'TRACK_NEGATIVE_Y'
            c.lock_axis = 'LOCK_Z'

            #bake rotator
            bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})


            #DRIVE BONE ORIGINAL ROTATION
            bpy.ops.object.add(type='EMPTY', location=(0, 0, 0))
            context.active_object.name = "ERM_driveBone_original_rotation"
            orig_rotation = scene.objects ["ERM_driveBone_original_rotation"]
            orig_rotation.rotation_mode = 'QUATERNION'
            orig_rotation.show_in_front = True

            #initial position
            c = orig_rotation.constraints.new ('COPY_LOCATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'


            #copy rotation: driveBone
            c = orig_rotation.constraints.new ('COPY_ROTATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'

            #bake orig_rotation
            bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})


            #CONSTRAINT ARMATURE

            bpy.ops.object.mode_set (mode='OBJECT')
            bpy.ops.object.select_all (action='DESELECT')
            root.select_set (True)
            bpy.context.view_layer.objects.active = scene.objects[root.name]


            bpy.ops.object.mode_set (mode='POSE')
            bpy.ops.pose.select_all (action='DESELECT')
            driveBone.select = True
            root.data.bones.active = driveBone


            bpy.ops.object.mode_set (mode='OBJECT')
            bpy.ops.object.select_all (action='DESELECT')
            root.select_set (True)
            bpy.context.view_layer.objects.active = scene.objects[root.name]

            if calculate_rotation == 'True':

                #constraint drive bone to original rotation
                c = driveBone_pb.constraints.new ('COPY_ROTATION')
                c.target = orig_rotation
                c.use_offset = False
                c.use_x = False
                c.use_y = False
                c.use_z = True
                c.target_space = 'WORLD'
                c.owner_space = 'WORLD'

            #constraint drive bone to orientation target
            c = driveBone_pb.constraints.new ('COPY_LOCATION')
            c.target = rotator
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'

            if calculate_rotation == 'True':

                #constraint armature object to rotator
                c = root.constraints.new ('COPY_ROTATION')
                c.target = rotator
                c.use_offset = False
                c.use_x = False
                c.use_y = False
                c.use_z = True
                c.target_space = 'WORLD'
                c.owner_space = 'WORLD'

            #constraint armature object to rotator
            c = root.constraints.new ('COPY_LOCATION')
            c.target = rotator
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = False
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'


            #bake armature constraints
            bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'POSE'})
            bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})


            #CLEAN UP
            bpy.data.objects.remove (rotator, do_unlink=True)
            bpy.data.objects.remove (orient_target, do_unlink=True)
            bpy.data.objects.remove (orig_rotation, do_unlink=True)

        
        #checks
        safety_check_1 (main, driveBone_name, False)
         
        
        #end of operator
        return {'FINISHED'}


#EXTRACT ROOT MOTION LOC Z
class Op_GYAZ_ExtractRootMotion_locZ (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_loc_z"  
    bl_label = "Extract Root Motion: Loc Z"
    bl_description = "Extract root motion from drive bone and apply it to armature object: location Z. It is a local effect, works after placing exactly 4 markers on the timeline. Strength: marker 1: 0, marker 2-3: 1, marker 4: 0"
    
    #properties
    
    ui_method: EnumProperty(
        items=(        
        #hero assets
        ('drive bone', "Drive Bone", ""),
        ('toes', "Toes", "")
    ),
    default='toes',
    name ="Reference"
    ) 
    
    ui_drive_bone: StringProperty(
        name='Drive Bone',
        default=prefs.bone_prefix+prefs.drive_bone,
        description="Bone that moves the whole skeleton, e.g. hips or pelvis")
        
    ui_left_toes: StringProperty(
        name='Left Toes',
        default=prefs.bone_prefix+prefs.toes+prefs.bone_left_suffix,
        description="")
        
    ui_right_toes: StringProperty(
        name='Right Toes',
        default=prefs.bone_prefix+prefs.toes+prefs.bone_right_suffix,
        description="")
    
    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    
    #operator function
    def execute(self, context):
        
        if self.ui_method == 'drive bone':
        
            #SETTINGS-SETTINGS-SETTINGS-SETTINGS
            #NAME OF DRIVE-BONE
            
            scene = bpy.context.scene
            driveBone_name = self.ui_drive_bone

            #END OF SETTINGS

            #HOW TO USE-HOW TO USE-HOW TO USE
            #Place exactly 4 markers on timeline
            #Select your armature

            #END OF HOW TO USE
            
            def main ():

                #get selected object as root
                root = bpy.context.object
                #define driveBone (returns Bone)
                driveBone = root.data.bones[driveBone_name]

                #get scene
                scene = bpy.context.scene
                #get first and last frame of animation
                firstFrame = scene.frame_start
                lastFrame = scene.frame_end
                
                bpy.ops.object.mode_set (mode='OBJECT')

                #ease in/out (lerp)
                #influence: marker1-marke2:0-->1, m2-m3:1, m3-m4:1-->0
                #get list of markers
                markers = []
                for k, v in scene.timeline_markers.items():
                    frame = v.frame
                    markers.append(frame)

                #get length of list
                num_markers = len(markers)

                #4 markers found: good to go, if not: error
                if num_markers != 4:
                    print ("EXACTLY 4 MARKERS SHOULD EXIST,"+" currently you have "+str(num_markers)+" markers.")
                    
                m1=markers[0]
                m2=markers[1]
                m3=markers[2]
                m4=markers[3]

                #get first and last marker
                first_marker = markers[0]
                last_marker = markers[-1]

                #set influence
                scene.frame_set (m1)
                root['influence_DRM_78k4']=0.0
                root.keyframe_insert (data_path='["influence_DRM_78k4"]')

                scene.frame_set (m2)
                root['influence_DRM_78k4']=1.0
                root.keyframe_insert (data_path='["influence_DRM_78k4"]')

                scene.frame_set (m3)
                root['influence_DRM_78k4']=1.0
                root.keyframe_insert (data_path='["influence_DRM_78k4"]')

                scene.frame_set (m4)
                root['influence_DRM_78k4']=0.0
                root.keyframe_insert (data_path='["influence_DRM_78k4"]')

                #jump to first frame of animation
                scene.frame_set (firstFrame)

                #define driveBone as pose bone
                driveBone_pb = bpy.data.objects[root.name].pose.bones[driveBone.name]

                #enter pose mode
                bpy.ops.object.mode_set (mode='POSE')
                #deselect all bones, select drivebone, active
                bpy.ops.pose.select_all (action='DESELECT')

                #enter object mode
                bpy.ops.object.mode_set (mode = 'OBJECT')
                #create empty at origin
                empty31 = bpy.ops.object.add (type='EMPTY', location=(0,0,0))
                #change name of empty
                bpy.context.active_object.name = "empty_DRM_locZ_toes_1"
                empty31 = bpy.data.objects["empty_DRM_locZ_toes_1"]
                    
                #enter object mode
                bpy.ops.object.mode_set (mode = 'OBJECT')
                bpy.ops.object.select_all (action='DESELECT')
                empty31.select_set (True)
                bpy.context.view_layer.objects.active = empty31
                #lock empty tp touch_pointZ (bake lower toe's locZ to empty31)                
                c = empty31.constraints.new ('CHILD_OF')
                c.target = root
                c.subtarget = driveBone.name
                c.use_location_x = False
                c.use_location_y = False
                c.use_location_z = True
                c.use_rotation_x = False
                c.use_rotation_y = False
                c.use_rotation_z = False
                c.use_scale_x = False
                c.use_scale_y = False
                c.use_scale_z = False                
                
                #set inverse matrix
                context_copy = context.copy()
                context_copy["constraint"] = empty31.constraints["Child Of"]
                bpy.ops.constraint.childof_set_inverse(context_copy, constraint="Child Of", owner='OBJECT')
                #bake driveBone's locZ to empty31 (visual transform)
                bpy.ops.nla.bake (frame_start=first_marker, frame_end=last_marker+1, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})

                bpy.ops.object.mode_set (mode = 'OBJECT')
                bpy.ops.object.select_all (action='DESELECT')
                root.select_set (True)


                #bake empty31's locZ to root
                for frameIndex in range(first_marker, last_marker+1):
                    scene.frame_set(frameIndex)
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    influence = root['influence_DRM_78k4']
                    root.location[2] = lerp(root.location[2], empty31.location[2], influence)
                    bpy.ops.anim.keyframe_insert_menu(type='Location')
                    
                #to object mode, root is active, pose mode, driveBone is active
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                root.select_set (True)
                bpy.context.view_layer.objects.active = root
                bpy.ops.object.mode_set(mode = 'POSE')
                bpy.ops.pose.select_all(action='DESELECT')
                driveBone.select=True

                #bake empty31's locZ to driveBone
                for frameIndex in range(first_marker, last_marker+1):
                    scene.frame_set(frameIndex)
                    influence = root['influence_DRM_78k4']
                    bpy.ops.transform.translate(value=(0, 0, lerp(0, -(empty31.location[2]), influence)), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False)
                    bpy.ops.anim.keyframe_insert_menu(type='Location')
                    #print(frameIndex, touch_pointZ)
                    
                #clean up
                #delete empty31
                bpy.data.objects.remove(empty31, do_unlink=True)

                bpy.ops.object.mode_set(mode = 'OBJECT')
            
            #checks
            safety_check_1 (main, driveBone_name, False)
        
    
        if self.ui_method == 'toes':
        
            #SETTINGS-SETTINGS-SETTINGS-SETTINGS
            #NAME OF DRIVE-BONE
            scene = bpy.context.scene
            driveBone_name = self.ui_drive_bone
            #NAME OF LEFT TOE
            left_toe_name = self.ui_left_toes
            #NAME OF RIGHT TOE
            right_toe_name = self.ui_right_toes

            #END OF SETTINGS

            #HOW TO USE-HOW TO USE-HOW TO USE
            #Put EXACTLY 4 MARKERS
            #marker1-2: blending in, marker2-3: full effect, marker3-4: blending out
            #Select your armature

            #END OF HOW TO USE
        
            def main ():

                #get selected object as root
                root = bpy.context.object
                #define driveBone (returns Bone)
                driveBone = root.data.bones[driveBone_name]

                #get scene
                scene = bpy.context.scene
                #get first and last frame of animation
                firstFrame = scene.frame_start
                lastFrame = scene.frame_end

                #lerp
                def lerp(A, B, alpha):
                    x = A*(1-alpha)+B*(alpha)
                    return x

                #ease in/out (lerp)
                #influence: marker1-marke2:0-->1, m2-m3:1, m3-m4:1-->0
                #get list of markers
                markers = []
                for k, v in scene.timeline_markers.items():
                    frame = v.frame
                    markers.append(frame)

                #get length of list
                num_markers = len(markers)

                #4 markers found: good to go, if not: error
                if num_markers != 4:
                    print ("EXACTLY 4 MARKERS SHOULD EXIST,"+" currently you have "+str(num_markers)+" markers.")
                    
                m1=markers[0]
                m2=markers[1]
                m3=markers[2]
                m4=markers[3]

                #get first and last marker
                first_marker = markers[0]
                last_marker = markers[-1]

                #set influence
                scene.frame_set (m1)
                root['influence_DRM_78k4']=0.0
                root.keyframe_insert(data_path='["influence_DRM_78k4"]')

                scene.frame_set (m2)
                root['influence_DRM_78k4']=1.0
                root.keyframe_insert(data_path='["influence_DRM_78k4"]')

                scene.frame_set (m3)
                root['influence_DRM_78k4']=1.0
                root.keyframe_insert(data_path='["influence_DRM_78k4"]')

                scene.frame_set (m4)
                root['influence_DRM_78k4']=0.0
                root.keyframe_insert(data_path='["influence_DRM_78k4"]')

                #print(markers)

                #jump to first frame of animation
                scene.frame_set (firstFrame)

                #define driveBone as pose bone
                driveBone_pb = bpy.data.objects[root.name].pose.bones[driveBone.name]

                #enter pose mode
                bpy.ops.object.mode_set(mode = 'POSE')
                #deselect all bones, select drivebone, active
                bpy.ops.pose.select_all(action='DESELECT')

                #define toeL and toeR
                toeL = root.data.bones[left_toe_name]
                toeR = root.data.bones[right_toe_name]

                #define bones as pose bones
                toeL_pb = bpy.data.objects[root.name].pose.bones[toeL.name]
                toeR_pb = bpy.data.objects[root.name].pose.bones[toeR.name]

                #enter object mode
                bpy.ops.object.mode_set(mode = 'OBJECT')
                #create empty at origin
                empty21 = bpy.ops.object.add(type='EMPTY', location=(0,0,0))
                #change name of empty
                bpy.context.active_object.name = "empty_DRM_locZ_toes_1"
                empty21 = bpy.data.objects["empty_DRM_locZ_toes_1"]

                #get time line markers
                markers = []
                for k, v in scene.timeline_markers.items():
                    frame = v.frame
                    markers.append(frame)
                
                
                #create empties to store toe head and tail locations
                toe_positions = [left_toe_name+"_head", left_toe_name+"_tail", right_toe_name+"_head", right_toe_name+"_tail"]
                const_targets = [left_toe_name, left_toe_name, right_toe_name, right_toe_name]
                head_or_tail = [0, 1, 0, 1]
                
                for index, tp in enumerate(toe_positions):
                    e = bpy.data.objects.new (name = "empty_"+tp, object_data = None)
                    scene.collection.objects.link (e)
                    
                    c = e.constraints.new ('COPY_LOCATION')
                    c.target = root
                    c.subtarget = const_targets [index]
                    c.head_tail = head_or_tail [index]
                    
                    
                    #bake empties on relevant frames
                    bpy.ops.object.select_all (action='DESELECT')
                    e.select_set (True)
                    bpy.context.view_layer.objects.active = e
                    
                    bpy.ops.nla.bake(frame_start=first_marker, frame_end=last_marker+1, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})
                    
                
                scene.frame_set (markers[0])
                for frameIndex in range(first_marker, last_marker+1):
                    scene.frame_set(frameIndex)
                    #get whichever toe is closer to the ground
                    #gether head and tail data
                    toe_loc1 = scene.objects["empty_"+left_toe_name+"_head"]
                    toe_loc2 = scene.objects["empty_"+left_toe_name+"_tail"]
                    toe_loc3 = scene.objects["empty_"+right_toe_name+"_head"]
                    toe_loc4 = scene.objects["empty_"+right_toe_name+"_tail"]
                    
                    a = toe_loc1.location[2]
                    b = toe_loc2.location[2]
                    c = toe_loc3.location[2]
                    d = toe_loc4.location[2]
                                       
                    #get the lowest value
                    touch_pointZ = min(a, b, c, d)
                    
                    #enter object mode
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    #lock empty tp touch_pointZ (bake lower toe's locZ to empty21)
                    empty21.location[2] = touch_pointZ
                    bpy.ops.object.select_all(action='DESELECT')
                    empty21.select_set (True)
                    bpy.context.view_layer.objects.active = empty21
                    #insert keyframe
                    bpy.ops.anim.keyframe_insert_menu(type='Location')


                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                root.select_set (True)


                #bake empty21's locZ to root
                for frameIndex in range(first_marker, last_marker+1):
                    scene.frame_set(frameIndex)
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    influence = root['influence_DRM_78k4']
                    root.location[2] = lerp(root.location[2], empty21.location[2], influence)
                    bpy.ops.anim.keyframe_insert_menu(type='Location')
                    
                #to object mode, root is active, pose mode, driveBone is active
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                root.select_set (True)
                bpy.context.view_layer.objects.active = root
                bpy.ops.object.mode_set(mode = 'POSE')
                bpy.ops.pose.select_all(action='DESELECT')
                root.data.bones.active = root.data.bones[driveBone_name]
                driveBone.select=True
                #set driveBone's locZ
                for frameIndex in range(first_marker, last_marker+1):
                    scene.frame_set(frameIndex)
                    influence = root['influence_DRM_78k4']
                    bpy.ops.transform.translate(value=(0, 0, -(lerp(0, empty21.location[2], influence))), constraint_axis=(False, False, True), orient_type='GLOBAL', mirror=False, use_proportional_edit=False)
                    bpy.ops.anim.keyframe_insert_menu(type='Location')
                    
                #clean up
                #delete empty21
                bpy.data.objects.remove(empty21, do_unlink=True)
                
                l = [toe_loc1, toe_loc2, toe_loc3, toe_loc4]
                for i in l:
                    bpy.data.objects.remove (bpy.data.objects[i.name], do_unlink=True)
                    
                bpy.ops.object.mode_set(mode = 'OBJECT')

                #delete influence property
                del root['influence_DRM_78k4']

        
            #checks
            safety_check_2 (main, driveBone_name, left_toe_name, right_toe_name, False)

    
        #end of operator
        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        markers = scene.timeline_markers
        return len(markers) == 4
    

#EXTRACT ROOT MOTION: MANUAL
class Op_GYAZ_ExtractRootMotion_Manual (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_manual"  
    bl_label = "Extract Root Motion: Manual"
    bl_description = "Adjust root (armature object) location and rotation manually, insert keyframes then hit 'Bake'. Set first and last frame on timeline"
    
    #properties    
    ui_modes: EnumProperty(
        items = (
            ('False', "Clean", ""),
            ('True', "Offset", "")
            ),
        default = 'False',
        name = "Mode",
        description = "Either used for editing previously extracted root motion or for extracting manualy from the start"
        )
        
    ui_drive_bone: StringProperty(
        name='Drive Bone',
        default=prefs.bone_prefix+prefs.drive_bone,
        description="Bone that moves the whole skeleton, e.g. hips or pelvis.")
        
    def draw (self, context):
        lay = self.layout
        lay.prop (self, 'ui_modes', expand=True)
        lay.prop (self, 'ui_drive_bone')
        
    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    #operator function
    def execute(self, context):
        
        #SETTINGS-SETTINGS-SETTINGS-SETTINGS
        #NAME OF DRIVE-BONE
        
        scene = bpy.context.scene
        driveBone_name = self.ui_drive_bone
        
        bake_previous_data = self.ui_modes
        
        #END OF SETTINGS
        
        #HOW TO USE-HOW TO USE-HOW TO USE
        #Set the 'Start' and the 'End' of the animation on the timeline
        #Select your armature
        #Position 'empty_OFFSET_ROOT_dynamic and insert keyframes
        #Once done, select your armature and run script

        #END OF HOW TO USE

        
        def main ():
        
            #get selected object as root
            root = bpy.context.object
            #get armatureData
            armatureData = root.data
            #define driveBone (returns Bone)
            driveBone = root.data.bones[driveBone_name]
            #define driveBone as pose bone
            driveBone_pb = bpy.data.objects[root.name].pose.bones[driveBone.name]
            
            bpy.ops.object.mode_set (mode='OBJECT')
            
            #get scene
            scene = bpy.context.scene
            #get first and last frame of animation
            firstFrame = scene.frame_start
            lastFrame = scene.frame_end

            #jump to first frame of animation
            scene.frame_set (firstFrame)
            
            #set active keying set to LocRot
            ks = scene.keying_sets_all
            ks.active = ks["LocRot"]
            
            
            #PREVIOUSLY EXTRACTED ROOT MOTION DATA
            if bake_previous_data == 'True':
            
                bpy.ops.object.mode_set (mode='OBJECT')
                
                bpy.ops.object.add(type='EMPTY', location=(root.location))
                bpy.context.active_object.name = "empty_OFFSET_ROOT_previos_data"
                previous_data = scene.objects ["empty_OFFSET_ROOT_previos_data"]
                previous_data.empty_display_type = 'CUBE'
                previous_data.empty_display_size = .2
                
                #constraint empty to armature object
                c = previous_data.constraints.new ('COPY_LOCATION')
                c.target = root
                c.use_offset = False
                c.use_x = True
                c.use_y = True
                c.use_z = True
                c.target_space = 'WORLD'
                c.owner_space = 'WORLD'
                
                c = previous_data.constraints.new ('COPY_ROTATION')
                c.target = root
                c.use_offset = False
                c.use_x = True
                c.use_y = True
                c.use_z = True
                c.target_space = 'WORLD'
                c.owner_space = 'WORLD'
                
                #bake driveBone's locXY to empty (visual transform)
                bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})
            
                                    
            #EMPTY STATIC
            
            empty_static = bpy.ops.object.add(type='EMPTY', location=(0,0,0))
            #change name of empty
            bpy.context.active_object.name = "empty_OFFSET_ROOT_static"
            empty_static = bpy.data.objects["empty_OFFSET_ROOT_static"]
            #add Copy Location constraint to empty, target: driveBone
            c = empty_static.constraints.new (type = 'COPY_LOCATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            #add Copy Rotation constraint to empty, target: driveBone
            c = empty_static.constraints.new (type = 'COPY_ROTATION')
            c.target = root
            c.subtarget = driveBone.name
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            #bake driveBone's locXY to empty (visual transform)
            bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})

            
            #EMPTY DYNAMIC
            
            #jump to first frame of animation
            #scene.frame_set (firstFrame)
            #create empty at origin
            empty_dynamic = bpy.ops.object.empty_add(type='ARROWS', location=(root.location))
            #change name of empty
            bpy.context.active_object.name = "empty_OFFSET_ROOT_dynamic"
            empty_dynamic = bpy.data.objects["empty_OFFSET_ROOT_dynamic"]
            empty_dynamic.show_in_front = True
            
            
            if bake_previous_data == 'True':
                
                #constraint empty dynamic to previos data empty
                c = empty_dynamic.constraints.new (type='COPY_LOCATION')
                c.target = previous_data
                c.use_offset = True
                c.use_x = True
                c.use_y = True
                c.use_z = True
                c.influence = 1.0     

                
                c = empty_dynamic.constraints.new (type='COPY_ROTATION')
                c.target = previous_data
                c.use_offset = True
                c.use_x = True
                c.use_y = True
                c.use_z = True
                c.influence = 1.0
            
            #clear transform    
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            empty_dynamic.select_set (True)
            bpy.context.view_layer.objects.active = empty_dynamic
            
            bpy.ops.object.location_clear ()
            bpy.ops.object.rotation_clear ()

            
            #ROOT
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            root.select_set (True)
            bpy.context.view_layer.objects.active = root
            #add Copy Location constraint to root, target: empty_dynamic
            c = root.constraints.new (type = 'COPY_LOCATION')
            c.target = empty_dynamic
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True

            #add Copy Rotation constraint to root, target: empty_dynamic
            c = root.constraints.new (type = 'COPY_ROTATION')
            c.target = empty_dynamic
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True

            
            #DRIVE BONE
            
            bpy.ops.object.mode_set(mode = 'POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            driveBone.select = True
            
            #add Copy Location constraint to driveBone, target: empty_static
            constraints = bpy.context.object.pose.bones[driveBone.name].constraints
            c = constraints.new (type='COPY_LOCATION')
            c.target = empty_static
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True

            #add Copy Rotation constraint to driveBone, target: empty_static
            constraints = bpy.context.object.pose.bones[driveBone.name].constraints
            c = constraints.new (type='COPY_ROTATION')
            c.target = empty_static
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True
            
                        
            #select empty_dynamic
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            empty_dynamic.select_set (True)
            bpy.context.view_layer.objects.active = empty_dynamic
            
            
            #object properties register that we have started manual editing
            root["ExtractRootMotion_manual_mode"] = True
            
            root["ExtractRootMotion_manual_empty1"] = empty_static.name
            root["ExtractRootMotion_manual_empty2"] = empty_dynamic.name
            if bake_previous_data == 'True':
                root["ExtractRootMotion_manual_empty3"] = previous_data.name
            if bake_previous_data == 'False':
                root["ExtractRootMotion_manual_empty3"] = "None"
                
            
            if bake_previous_data == 'True':
                previous_data.hide_viewport = True
            empty_static.hide_viewport = True
           
        #check for drive bone                
        ob = bpy.context.active_object
        bones = ob.data.bones
        if bones.find(driveBone_name) != -1:
            main ()
        else:
            popup (["bone: '"+str(driveBone_name)+"' not found"], "ERROR")
        
        
        #end of operator
        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return "ExtractRootMotion_manual_mode" not in obj

         
#EXTRACT ROOT MOTION: BAKE MANUAL OFFSET
class Op_GYAZ_ExtractRootMotion_ManualBake (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_bake_manual"  
    bl_label = "Extract Root Motion: Bake Manual"
    bl_description = "Bake keyframed manual root offset"
    
    #operator function
    def execute(self, context):
        
        #HOW TO USE-HOW TO USE-HOW TO USE
        #Set the 'Start' and the 'End' of the animation on the timeline
        #Select your armature

        #END OF HOW TO USE

        #get selected object as root
        root = bpy.context.object

        #get scene
        scene = bpy.context.scene
        #get first and last frame of animation
        firstFrame = scene.frame_start
        lastFrame = scene.frame_end
        
        bpy.ops.object.mode_set (mode='OBJECT')
            
        #jump to first frame of animation
        scene.frame_set (firstFrame)
        #bake action
        bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'POSE'})
        bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})

            
        #clean up
        #delete empties and manual mode
        scene = bpy.context.scene
        
        empties = [
        root["ExtractRootMotion_manual_empty1"],
        root["ExtractRootMotion_manual_empty2"],
        root["ExtractRootMotion_manual_empty3"]
        ]
        
        for empty in empties:
            if bpy.data.objects.get(empty) is not None:
                bpy.data.objects.remove(bpy.data.objects[empty], do_unlink=True)
                
        del root['ExtractRootMotion_manual_mode']
        del root['ExtractRootMotion_manual_empty1']
        del root['ExtractRootMotion_manual_empty2']
        del root['ExtractRootMotion_manual_empty3']

        
        #end of operator
        return {'FINISHED'}
        
    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        return 'ExtractRootMotion_manual_mode' in obj

    
#EXTRACT ROOT MOTION: MANUAL - CANCEL
class Op_GYAZ_ExtractRootMotion_ManualCancel (bpy.types.Operator):
       
    bl_idname = "anim.extract_root_motion_manual_cancel"  
    bl_label = "Extract Root Motion: Manual Cancel"
    bl_description = "Cancel manual editing"
    
    ui_drive_bone: StringProperty(
        name='Drive Bone',
        default=prefs.bone_prefix+prefs.drive_bone,
        description="Bone that moves the whole skeleton, e.g. hips or pelvis")
        
    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    #operator function
    def execute(self, context):
        
        scene = bpy.context.scene
        driveBone_name = self.ui_drive_bone
        
        root = bpy.context.object
        
        def main ():
        
            #delete existing empties and manual mode
            scene = context.scene
            
            empties = [
                root["ExtractRootMotion_manual_empty1"],
                root["ExtractRootMotion_manual_empty2"],
                root["ExtractRootMotion_manual_empty3"]
                ]
                
            for empty in empties:
                if bpy.data.objects.get(empty) is not None:
                    bpy.data.objects.remove (bpy.data.objects[empty], do_unlink=True)
                    
            #delete driveBone constraint
            cs = root.pose.bones[driveBone_name].constraints
            for c in cs:
                cs.remove (c)
                
            #delete object constraints
            cs = root.constraints
            for c in cs:
                cs.remove (c)            
                        
            del root['ExtractRootMotion_manual_mode']
            del root['ExtractRootMotion_manual_empty1']
            del root['ExtractRootMotion_manual_empty2']
            del root['ExtractRootMotion_manual_empty3']
        
        
        #checks
        safety_check_1 (main, driveBone_name, False)
        
               
        #end of operator
        return {'FINISHED'}

        
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return 'ExtractRootMotion_manual_mode' in obj
 

#EXTRACT ROOT MOTION: DELETE ROOT ANIMATION
class Op_GYAZ_ExtractRootMotion_DeleteRootAnim (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_delete_root_anim"  
    bl_label = "Extract Root Motion: Delete Root Anim"
    bl_description = "Delete root animation (Object animation)"
    
    #operator function
    def execute(self, context):

        #get scene
        scene = bpy.context.scene
        #get first and last frame of animation
        firstFrame = scene.frame_start
        lastFrame = scene.frame_end
            
        #jump to first frame of animation
        scene.frame_set (firstFrame)
        
        #delete anim data
        root = bpy.context.active_object
        bpy.ops.object.mode_set (mode='OBJECT')
        bpy.ops.object.select_all (action='DESELECT')
        root.select_set (True)
        bpy.context.view_layer.objects.active = root
                             
        #delete keys
        #get active action's name
        obj = bpy.context.object
        action_name = (obj.animation_data.action.name
        if obj.animation_data is not None and
            obj.animation_data.action is not None
        else "")
        
        if action_name == "":
            popup (["Armature has no animation."], "ERROR")
            
            return {'FINISHED'}
        
        #delete object animation (not bones) and scale keys
        action = bpy.data.actions[action_name]
        fcurves = action.fcurves
        for fc in fcurves:
            if "bone" not in fc.data_path:
                fcurves.remove (fc)
            
        bpy.ops.object.location_clear ()
        bpy.ops.object.rotation_clear ()  

        
        #end of operator
        return {'FINISHED'}


#EXTRACT ROOT MOTION: ROOT BONE
class Op_GYAZ_ExtractRootMotion_CopyToBone (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_copy_to_bone"  
    bl_label = "Extract Root Motion: Copy To Bone"
    bl_description = "Moves extracted root motion from armature object to root bone. Root bone should be on a visible armature layer"
    
    #operator function
    def execute(self, context):
        
        root_bone_name = root_bone
        
        def main (root_bone_name):
            
            # check if root bone is visible
            # save mode
            mode = bpy.context.mode
            bpy.ops.object.mode_set (mode='POSE')
            rig = bpy.context.active_object 
            rig.data.bones.active = rig.data.bones[root_bone_name]            
            if bpy.context.active_pose_bone == None:
                bpy.ops.object.mode_set (mode=mode)
                popup (["bone: '"+root_bone_name+"' not visible"], 'ERROR')
            else:
            
                bpy.ops.object.mode_set (mode='OBJECT')
                
                root = bpy.context.active_object
                
                root_bone_name = root_bone
                
                #get scene
                scene = bpy.context.scene
                #get first and last frame of animation
                firstFrame = scene.frame_start
                lastFrame = scene.frame_end
                    
                #jump to first frame of animation
                scene.frame_set (firstFrame)
                
                #create empty to store root motion
                bpy.ops.object.add(type='EMPTY', location=(0, 0, 0))
                bpy.context.active_object.name = "ERM_root_info"
                root_info = scene.objects ["ERM_root_info"]

                #initial position
                c = root_info.constraints.new ('COPY_TRANSFORMS')
                c.target = root

                #apply visual transform
                bpy.ops.object.mode_set (mode='OBJECT')
                bpy.ops.object.select_all (action='DESELECT')
                root_info.select_set (True)
                bpy.context.view_layer.objects.active = scene.objects[root_info.name]

                bpy.ops.object.visual_transform_apply ()

                root_info.constraints.remove (c)
                
                #parent it to root
                c = root_info.constraints.new ('CHILD_OF')
                c.target = root        
                
                #set inverse matrix
                context_copy = bpy.context.copy()
                context_copy["constraint"] = root_info.constraints["Child Of"]
                bpy.ops.constraint.childof_set_inverse(context_copy, constraint=c.name, owner='OBJECT')
                #update
                scene.frame_set (scene.frame_current + 1)
                scene.frame_set (scene.frame_current - 1)
                
                #bake root info
                bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})
                
                #delete root motion from armature object:
                bpy.ops.object.select_all (action='DESELECT')
                root.select_set (True)
                bpy.context.view_layer.objects.active = root            
                
                #get active action's name
                obj = bpy.context.object
                action_name = (obj.animation_data.action.name
                if obj.animation_data is not None and
                    obj.animation_data.action is not None
                else "")

                #delete object animation (not bones)
                action = bpy.data.actions[action_name]
                fcurves = action.fcurves
                for fc in fcurves:
                    if "bone" not in fc.data_path:
                        fcurves.remove (fc)
                    
                clear_transformation (root)        
                
                #parent root bone to empty (root_info)
                bpy.ops.object.mode_set (mode='POSE')
                pbone = root.pose.bones[root_bone_name]
                
                c = pbone.constraints.new ('COPY_TRANSFORMS')
                c.target = root_info                             
                
                #bake root bone
                bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame+1, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'POSE'})

                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                root.select_set (True)
                bpy.context.view_layer.objects.active = root
                            
                #delete empty (root_info)
                root_info.user_clear ()
                bpy.data.objects.remove (root_info, do_unlink=True)

               
        #check for drive bone                
        safety_check_1 (main, root_bone, True)      

        
        #end of operator
        return {'FINISHED'}
    
    
class VIEW3D_PT_GYAZ_ExtractRootMotion (Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Extract Root Motion'
    bl_category = 'AnimTools'
    
    #add ui elements here
    def draw (self, context):
        scene = bpy.context.scene
        lay = self.layout   
        col = lay.column(align=True)
        col.label(text="Auto:")
        row = col.row(align=True)
        row.operator (Op_GYAZ_ExtractRootMotion_Base.bl_idname, text = "Base")
        row.operator (Op_GYAZ_ExtractRootMotion_locZ.bl_idname, text = "Loc Z")
        col = lay.column(align=True)
        col.label(text="Manual:")
        row = col.row(align=True)
        row.operator(Op_GYAZ_ExtractRootMotion_Manual.bl_idname, text = "Start")
        row.operator(Op_GYAZ_ExtractRootMotion_ManualCancel.bl_idname, text="Cancel", icon='PANEL_CLOSE')
        col.operator(Op_GYAZ_ExtractRootMotion_ManualBake.bl_idname, text="Bake", icon='FILE_TICK')
        col = lay.column(align=True)
        col.label(text="Extra:")
        col.operator (Op_GYAZ_ExtractRootMotion_Visualize.bl_idname, text = 'Visualize')
        col.operator(Op_GYAZ_ExtractRootMotion_DeleteRootAnim.bl_idname, text="Delete Root Anim")
        col.operator (Op_GYAZ_ExtractRootMotion_CopyToBone.bl_idname, text = "Move To Root Bone")
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        ao = context.active_object
        if ao != None:
            return context.mode == 'OBJECT' and bpy.context.object.type == 'ARMATURE'


#REGISTER
#everything should be registeres here

def register():  
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_Visualize) 
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_Base)    
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_locZ)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_Manual)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_ManualCancel)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_ManualBake)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_DeleteRootAnim)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_CopyToBone)
    
    bpy.utils.register_class (VIEW3D_PT_GYAZ_ExtractRootMotion)
    

def unregister ():    
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_Visualize) 
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_Base) 
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_locZ)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_Manual)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_ManualCancel)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_ManualBake)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_DeleteRootAnim)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_CopyToBone) 
    
    bpy.utils.unregister_class (VIEW3D_PT_GYAZ_ExtractRootMotion) 

  
if __name__ == "__main__":   
    register()      