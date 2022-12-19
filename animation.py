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
from bpy.types import Operator


class Op_GYAZ_ResetAllBones (Operator):
       
    bl_idname = "pose.gyaz_reset_all_bones"  
    bl_label = "Reset All Bones"
    bl_description = "Clear transforms from all bones including invisible ones"
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):

        rig = bpy.context.object

        zero_vec = (0, 0, 0)
        zero_quat = (1, 0, 0, 0)
        one_vec = (1, 1, 1)
        zero_axis_angle = (0, 0, 1, 0)

        for pbone in rig.pose.bones:
            pbone.location = zero_vec
            rm = pbone.rotation_mode
            if rm == "QUATERNION":
                pbone.rotation_quaternion = zero_quat
            elif rm == "AXIS_ANGLE":
                pbone.rotation_axis_angle = zero_axis_angle
            else:
                pbone.rotation_euler = zero_vec
            pbone.scale = one_vec

        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj is not None and obj.type == "ARMATURE"
        

class Op_GYAZ_AdjustSceneToActionFrameRange (Operator):
       
    bl_idname = "anim.adjust_scene_to_action_frame_range"  
    bl_label = "Adjust Scene to Action Frame Range"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):

        obj = context.object
        scene = context.scene
        if obj.animation_data is not None:
            action = obj.animation_data.action
            if action is not None:
                frame_start, frame_end = action.frame_range
                scene.frame_start = int(frame_start)
                scene.frame_end = int(frame_end)
                scene.frame_preview_start = int(frame_start)
                scene.frame_preview_end = int(frame_end)

        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj is not None and obj.type == "ARMATURE"

    
#######################################################
#######################################################

#REGISTER

def register():
       
    bpy.utils.register_class (Op_GYAZ_ResetAllBones) 
    bpy.utils.register_class (Op_GYAZ_AdjustSceneToActionFrameRange) 


def unregister ():
    
    bpy.utils.unregister_class (Op_GYAZ_ResetAllBones)
    bpy.utils.unregister_class (Op_GYAZ_AdjustSceneToActionFrameRange)
  

if __name__ == "__main__":   
    register()      
