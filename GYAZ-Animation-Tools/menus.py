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
from bpy.types import Menu, Panel

class VIEW3D_MT_GYAZ_Pose (Menu):
    bl_label = 'Pose'
    
    def draw (self, context):
        lay = self.layout
        scene = context.scene
        wm = context.window_manager
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('pose.push', text='Push Pose From Breakdown')
        lay.operator ('pose.relax', text='Relax Pose To Breakdown')
        lay.operator ('pose.breakdown', text='Pose Breakdowner')
        lay.operator ('pose.blend_to_neighbor', text='Blend To Neightbor')
        lay.separator ()
        lay.operator ("anim.gyaz_offset_anim", text='Offset Global').Mode='GLOBAL'
        lay.operator ("anim.gyaz_offset_anim", text='Offset Local').Mode='SIMPLE_LOCAL'
        lay.operator ("anim.gyaz_offset_anim", text='Offset Local 2').Mode='LOCAL_2'
        lay.operator ("anim.gyaz_offset_anim", text='Offset Local 4').Mode='LOCAL_4'
        lay.separator ()
        lay.operator ('pose.paste', text='Paste Flipped').flipped=True
        lay.separator ()
        lay.operator ('pose.transforms_clear', text='Clear Transform')
        lay.operator ('pose.user_transforms_clear', text='Reset To Keframed Transform')
        lay.operator ('pose.gyaz_reset_all_bones')


class VIEW3D_MT_GYAZ_PoseSelect (Menu):
    bl_label = 'Select'
    
    def draw (self, context):
        lay = self.layout
        lay.operator ('pose.select_mirror')
        lay.operator ('pose.select_constraint_target')
        lay.operator ('pose.select_linked', text="Select Linked")
        lay.menu("VIEW3D_MT_select_pose_more_less")
        lay.operator_menu_enum("pose.select_grouped", "type", text="Grouped")


class VIEW3D_PT_GYAZ_Animation (Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animation'
    bl_label = 'Animation'    
    
    #add ui elements here
    def draw (self, context):
        lay = self.layout
        col = lay.column (align=True)
        col.operator ('nla.bake')
        col.operator ('anim.gyaz_retarget', text='Retarget')
        col.operator ('pose.gyaz_reset_all_bones')
        col.operator ('anim.keyframe_clear_v3d')

    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None and (bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE')


def timeline_header_extension(self, context):
    self.layout.operator("anim.gyaz_adjust_scene_to_action_frame_range", text="", icon="ACTION")

        
#######################################################
#######################################################

#REGISTER

def register():
        
    bpy.utils.register_class (VIEW3D_MT_GYAZ_Pose)
    bpy.utils.register_class (VIEW3D_MT_GYAZ_PoseSelect)   
    bpy.utils.register_class (VIEW3D_PT_GYAZ_Animation)   

    bpy.types.DOPESHEET_HT_header.append(timeline_header_extension)   

def unregister ():
    
    bpy.utils.unregister_class (VIEW3D_MT_GYAZ_Pose)
    bpy.utils.unregister_class (VIEW3D_MT_GYAZ_PoseSelect)
    bpy.utils.unregister_class (VIEW3D_PT_GYAZ_Animation)

    bpy.types.DOPESHEET_HT_header.remove(timeline_header_extension)  
  
if __name__ == "__main__":   
    register()      