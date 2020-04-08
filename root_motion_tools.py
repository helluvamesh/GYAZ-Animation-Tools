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
from .utils import popup as popup_single
from .utils import select_only
from bpy.types import Scene


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
    bl_options = {'REGISTER', 'UNDO'}

    
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
    

#EXTRACT ROOT MOTION: MANUAL
class Op_GYAZ_ExtractRootMotion_Manual (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_manual"  
    bl_label = "Extract Root Motion: Manual"
    bl_description = "Adjust root (armature object) location and rotation manually, insert keyframes then hit 'Bake'. Set first and last frame on timeline"
    bl_options = {'REGISTER', 'UNDO'}
    
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
        
    def draw (self, context):
        lay = self.layout
        lay.prop (self, 'ui_modes', expand=True)
        
    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    #operator function
    def execute(self, context):
        
        #SETTINGS-SETTINGS-SETTINGS-SETTINGS
        #NAME OF DRIVE-BONE
        
        scene = bpy.context.scene
        driveBone_name = scene.gyaz_root_motion_drive_bone
        
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
            c.name = "GYAZ_root_motion__loc"
            c.target = empty_static
            c.use_offset = False
            c.use_x = True
            c.use_y = True
            c.use_z = True

            #add Copy Rotation constraint to driveBone, target: empty_static
            constraints = bpy.context.object.pose.bones[driveBone.name].constraints
            c = constraints.new (type='COPY_ROTATION')
            c.name = "GYAZ_root_motion__rot"
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
    bl_options = {'REGISTER', 'UNDO'}
    
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
        driveBoneName = scene.gyaz_root_motion_drive_bone
        #get first and last frame of animation
        firstFrame = scene.frame_start
        lastFrame = scene.frame_end
        
        bpy.ops.object.mode_set (mode='OBJECT')
            
        #jump to first frame of animation
        scene.frame_set (firstFrame)
        #bake action
        bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=False, clear_parents=True, use_current_action=True, bake_types={'POSE'})
        bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})
        
        constraints = bpy.context.object.pose.bones[driveBoneName].constraints
        
        for c in constraints:
            if c.name.startswith("GYAZ_root_motion"):
                constraints.remove(c)
        
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
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):
        
        scene = bpy.context.scene
        driveBone_name = bpy.context.scene.gyaz_root_motion_drive_bone
        
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
class Op_GYAZ_ExtractRootMotion_DeleteRootMotion (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_extract_root_motion_delete_root_motion"  
    bl_label = "Extract Root Motion: Delete Root Motion"
    bl_description = "Delete root animation (Object animation)"
    bl_options = {'REGISTER', 'UNDO'}
    
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
    bl_options = {'REGISTER', 'UNDO'}
    
    ui_root_bone: StringProperty(
            name="Root",
            default=prefs.root_bone
            )
    
    #popup with properties
    def invoke(self, context, event):
        wm = bpy.context.window_manager
        return wm.invoke_props_dialog(self)
    
    #operator function
    def execute(self, context):
        
        root_bone_name = self.ui_root_bone
        
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
                
                root_info = bpy.data.objects.new(object_data=None, name="ERM_root_info")
                bpy.context.scene.collection.objects.link(root_info)

                c = root_info.constraints.new ("COPY_TRANSFORMS")
                c.target = root
                
                #bake root info
                select_only(root_info)
                bpy.ops.nla.bake(frame_start=firstFrame, frame_end=lastFrame, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})
                
                #delete root motion from armature object:
                select_only(root)            
                
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
                
                bpy.ops.object.mode_set (mode='OBJECT')
                            
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
        col.label(text="Drive Bone:")
        col.prop(bpy.context.scene, "gyaz_root_motion_drive_bone", text="")
        col = lay.column(align=True)
        row = col.row(align=True)
        row.operator(Op_GYAZ_ExtractRootMotion_Manual.bl_idname, text = "Start")
        row.operator(Op_GYAZ_ExtractRootMotion_ManualCancel.bl_idname, text="Cancel", icon='PANEL_CLOSE')
        col.operator(Op_GYAZ_ExtractRootMotion_ManualBake.bl_idname, text="Bake", icon='FILE_TICK')
        col = lay.column(align=True)
        col.operator (Op_GYAZ_ExtractRootMotion_Visualize.bl_idname, text = 'Visualize')
        col.operator(Op_GYAZ_ExtractRootMotion_DeleteRootMotion.bl_idname, text="Delete Root Motion")
        col.operator (Op_GYAZ_ExtractRootMotion_CopyToBone.bl_idname, text = "Move to Root Bone")
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        ao = context.active_object
        if ao != None:
            return context.mode == 'OBJECT' and bpy.context.object.type == 'ARMATURE'


#REGISTER
#everything should be registeres here

def register():  
    
    Scene.gyaz_root_motion_drive_bone = StringProperty(
        name="Drive Bone", 
        default=prefs.drive_bone,
        description="Bone that moves the whole skeleton, e.g. hips or pelvis")
    
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_Visualize) 
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_Manual)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_ManualCancel)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_ManualBake)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_DeleteRootMotion)
    bpy.utils.register_class (Op_GYAZ_ExtractRootMotion_CopyToBone)
    
    bpy.utils.register_class (VIEW3D_PT_GYAZ_ExtractRootMotion)
    

def unregister ():
        
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_Visualize) 
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_Manual)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_ManualCancel)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_ManualBake)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_DeleteRootMotion)
    bpy.utils.unregister_class (Op_GYAZ_ExtractRootMotion_CopyToBone) 
    
    bpy.utils.unregister_class (VIEW3D_PT_GYAZ_ExtractRootMotion) 
    
    del Scene.drive_bone
  
if __name__ == "__main__":   
    register()      