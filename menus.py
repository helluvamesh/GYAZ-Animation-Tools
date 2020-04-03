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
from bpy.types import Operator, Menu, Panel

class VIEW3D_MT_GYAZ_Pose (Menu):
    bl_label = 'Pose'
    
    def draw (self, context):
        lay = self.layout
        scene = context.scene
        wm = context.window_manager
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('pose.push', text='Push')
        lay.operator ('pose.relax', text='Relax')
        lay.operator ('pose.breakdown', text='Breakdown')
        lay.separator ()
        lay.operator ('pose.select_mirror', text='Flip Selection')
        lay.operator ('pose.paste', text='Paste Flipped').flipped=True
        lay.separator ()
        lay.operator ('pose.propagate', text='Propagate').mode='WHILE_HELD'
        lay.operator ('pose.propagate', text='To Next Keyframe').mode='NEXT_KEY'
        lay.operator ('pose.propagate', text='To Last Keyframe (Cyclic)').mode='LAST_KEY'
        lay.operator ('pose.propagate', text='On Selected Keyframes').mode='SELECTED_KEYS'
        lay.operator ('pose.propagate', text='On Selected Markers').mode='SELECTED_MARKERS'
        lay.separator ()
        lay.operator ('poselib.pose_add', text='Add To Library')
        lay.separator ()
        lay.operator ('pose.transforms_clear', text='Clear Transform')
        lay.operator ('pose.user_transforms_clear', text='Reset To Keframed Transform')
        lay.operator ('pose.visual_transform_apply', text='Apply Visual Transform')
        lay.operator ('nla.bake')
        lay.separator ()
        lay.operator ('pose.paths_calculate', text='Calc Paths')
        lay.operator ('pose.paths_clear', text='Clear Paths')
        

class VIEW3D_MT_GYAZ_Armature (Menu):
    bl_label = 'Armature'
    
    def draw (self, context):
        lay = self.layout
        scene = context.scene
        wm = context.window_manager
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('paint.weight_from_bones', text='Weight From Bones (Automatic)').type='AUTOMATIC'
        lay.operator ('paint.weight_from_bones', text='Weight From Bones (Envelopes)').type='ENVELOPES'
        lay.separator ()
        lay.operator ('pose.constraint_add_with_targets', text='Constraint with Target')
        lay.operator ('pose.constraints_copy', text='Copy Constraints to Selected')
        
        
class DOPESHEET_MT_GYAZ_Dopesheet (Menu):
    bl_label = 'Dopesheet'
    
    def draw (self, context):
        lay = self.layout
        scene = context.scene
        wm = context.window_manager
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('action.sample')
        lay.operator ('action.clean', text='Clean Keyframes').channels=True
        lay.operator ('action.clean', text='Clean Channels').channels=False
        lay.separator ()
        lay.operator ('action.paste', text='Paste Flipped').flipped=True
        lay.separator ()
        lay.operator_menu_enum ("action.keyframe_type", "type", text="Keyframe Type")
        lay.operator_menu_enum ("action.handle_type", "type", text="Handle Type")
        lay.operator_menu_enum ("action.interpolation_type", "type", text="Interpolation Mode")
        lay.operator_menu_enum ("action.extrapolation_type", "type", text="Extrapolation Mode")
        lay.separator ()
#        lay.operator ('anim.channels_group', text='Group')
#        lay.operator ('anim.channels_ungroup', text='Ungroup')
        lay.operator ('anim.channels_setting_disable', text='Unmute').type='MUTE'
        lay.operator ('anim.channels_setting_enable', text='Mute').type='MUTE'
        lay.operator ('anim.channels_setting_disable', text='Unlock').type='PROTECT'
        lay.operator ('anim.channels_setting_enable', text='Lock').type='PROTECT'
        lay.separator ()
        lay.operator ('transform.transform', text='Slide').mode='TIME_SLIDE'
        lay.operator ('transform.transform', text='Extend').mode='TIME_EXTEND'
        lay.separator ()
        lay.operator ('anim.channels_fcurves_enable')
                
        
class GRAPH_MT_GYAZ_GraphEditor (Menu):
    bl_label = 'Graph Editor'
    
    def draw (self, context):
        lay = self.layout
        scene = context.scene
        wm = context.window_manager
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('graph.clean', text='Clean Channels').channels=True
        lay.operator ('graph.clean', text='Clean Keyframes').channels=False
        lay.operator ('graph.sample', text='Sample')
        lay.operator ('graph.smooth', text='Smooth')
        lay.separator ()
        lay.operator ('graph.paste', text='Paste Flipped').flipped=True
        lay.separator ()
        lay.operator_menu_enum ("graph.handle_type", "type", text="Handle Type")
        lay.operator_menu_enum ("graph.interpolation_type", "type", text="Interpolation Mode")
        lay.operator_menu_enum ("graph.easing_type", "type", text="Easing Type")
        lay.operator_menu_enum ("graph.extrapolation_type", "type", text="Extrapolation Mode")
        lay.separator ()
#        lay.operator ('anim.channels_group', text='Group')
#        lay.operator ('anim.channels_ungroup', text='Ungroup')
        lay.operator ('anim.channels_setting_disable', text='Unmute').type='MUTE'
        lay.operator ('anim.channels_setting_enable', text='Mute').type='MUTE'
        lay.operator ('anim.channels_setting_disable', text='Unlock').type='PROTECT'
        lay.operator ('anim.channels_setting_enable', text='Lock').type='PROTECT'
        lay.separator ()
        lay.operator_menu_enum ('graph.fmodifier_add', 'type')
        lay.operator ('graph.sound_bake')        
        lay.separator ()
        lay.operator ('transform.transform', text='Extend').mode='TIME_EXTEND'
        lay.separator ()
        lay.operator ('graph.bake')
        lay.operator ('graph.euler_filter')
        
        
class VIEW3D_MT_GYAZ_WeightTools (Menu):
    bl_label = 'Weight Tools'
    
    def draw (self, context):
        lay = self.layout
        scene = context.scene
        wm = context.window_manager
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('object.vertex_group_levels', text='Levels')
        lay.operator ('object.vertex_group_smooth', text='Smooth')
        lay.operator ('object.vertex_group_mirror', text='Mirror')
        lay.operator ('paint.weight_from_bones').type = 'AUTOMATIC'
        lay.separator ()
        lay.operator ('paint.weight_gradient', text='Radial Gradient').type='RADIAL'
        lay.operator ('paint.weight_gradient', text='Linear Gradient').type='LINEAR'
        lay.separator ()
        lay.operator ('object.vertex_group_normalize_all', text='Normalize All').lock_active=False
        lay.operator ('object.vertex_group_normalize_all', text='Normalize All (Lock Active)').lock_active=True
        lay.operator ('object.vertex_group_normalize', text='Normalize')
        lay.separator ()
        lay.operator ('object.vertex_group_limit_total', text='Limit Total')
        lay.operator ('object.vertex_group_clean', text='Clean')
        lay.separator ()
        
        op = lay.operator ('object.data_transfer', text='Transfer Weights')
        op.use_reverse_transfer = True
        op.data_type = 'VGROUP_WEIGHTS'
        op.vert_mapping = 'POLYINTERP_NEAREST'
        op.layers_select_src = 'NAME'
        op.layers_select_dst = 'ALL'
        
        op = lay.operator ('object.data_transfer', text='Transfer Active Weight')
        op.use_reverse_transfer = True
        op.data_type = 'VGROUP_WEIGHTS'
        op.vert_mapping = 'POLYINTERP_NEAREST'
        op.layers_select_src = 'ACTIVE'
        op.layers_select_dst = 'ACTIVE'
        
        lay.separator ()
        lay.operator ('object.vertex_group_invert', text='Invert')
        lay.operator ('object.vertex_group_quantize', text='Quantize')
        lay.operator ('object.vertex_group_fix', text='Fix Deforms')
        lay.separator ()
        lay.operator ('paint.weight_set', text='Set Weight')      


class VIEW3D_MT_GYAZ_AnimTools (Menu):
    bl_label = 'Object Anim Tools'
    
    #add ui elements here
    def draw (self, context):
        scene = bpy.context.scene
        lay = self.layout
        lay.label (text='Extract Root Motion:')
        lay.separator ()
        lay.operator_context = 'INVOKE_REGION_WIN'
        lay.operator ('anim.gyaz_extract_root_motion_base', text="Base")
        lay.operator ('anim.gyaz_extract_root_motion_loc_z', text="Loc Z")
        lay.separator ()
        lay.operator('anim.gyaz_extract_root_motion_manual', text="Start Manual")
        lay.operator('anim.extract_root_motion_manual_cancel', text="Cancel Manual", icon='PANEL_CLOSE')
        lay.operator('anim.gyaz_extract_root_motion_bake_manual', text="Bake Manual", icon='FILE_TICK')
        lay.separator ()
        lay.operator ('anim.gyaz_extract_root_motion_visualize', text='Visualize')
        lay.operator('anim.gyaz_extract_root_motion_delete_root_anim', text="Delete Root Anim")
        lay.operator ('anim.gyaz_extract_root_copy_to_bone', text="Move To Root Bone")
        lay.separator ()
        lay.operator ('nla.bake')
        lay.operator ('anim.gyaz_retarget', text='Retarget')
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        ao = context.active_object
        if ao != None:
            return context.mode == 'OBJECT' and bpy.context.object.type == 'ARMATURE'
        

class VIEW3D_PT_GYAZ_Animation (Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AnimTools'
    bl_label = 'Animation'    
    
    #add ui elements here
    def draw (self, context):
        lay = self.layout
        col = lay.column (align=True)
        col.operator ('nla.bake')
        col.operator ('anim.gyaz_retarget', text='Retarget')

    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None and (bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE')

        
#######################################################
#######################################################

#REGISTER
#everything should be registeres here

def register():
        
    bpy.utils.register_class (VIEW3D_MT_GYAZ_Pose)    
    bpy.utils.register_class (VIEW3D_MT_GYAZ_Armature)    
    bpy.utils.register_class (DOPESHEET_MT_GYAZ_Dopesheet)    
    bpy.utils.register_class (GRAPH_MT_GYAZ_GraphEditor)    
    bpy.utils.register_class (VIEW3D_MT_GYAZ_WeightTools)    
    bpy.utils.register_class (VIEW3D_MT_GYAZ_AnimTools)    
    bpy.utils.register_class (VIEW3D_PT_GYAZ_Animation)    

def unregister ():
    
    bpy.utils.unregister_class (VIEW3D_MT_GYAZ_Pose)
    bpy.utils.unregister_class (VIEW3D_MT_GYAZ_Armature)
    bpy.utils.unregister_class (DOPESHEET_MT_GYAZ_Dopesheet)
    bpy.utils.unregister_class (GRAPH_MT_GYAZ_GraphEditor)
    bpy.utils.unregister_class (VIEW3D_MT_GYAZ_WeightTools)
    bpy.utils.unregister_class (VIEW3D_MT_GYAZ_AnimTools)
    bpy.utils.unregister_class (VIEW3D_PT_GYAZ_Animation)
  
if __name__ == "__main__":   
    register()      