# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

bl_info = {   
 "name": "GYAZ Animation Tools",   
 "author": "Andras Gyalog",   
 "version": ('6'),   
 "blender": (2, 79, 0),   
 "location": "",   
 "description": "Various animation tools",
 "warning": "",   
 "wiki_url": "",   
 "tracker_url": "",   
 "category": "Animation"}



import bpy
from bpy.types import Operator, AddonPreferences, PropertyGroup
from bpy.props import *

class GYAZ_AnimationTools_ShortcutItem (PropertyGroup):
    km_name = StringProperty (default='')
    kmi_idname = StringProperty (default='')
    type = StringProperty (default='')
    value = StringProperty (default='')
    shift = BoolProperty (default=False)
    ctrl = BoolProperty (default=False)
    alt = BoolProperty (default=False)
    prop = StringProperty (default='')


class GYAZ_Animation_Tools_Preferences (AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    
    addon_shortcuts = CollectionProperty (type=GYAZ_AnimationTools_ShortcutItem)
    disabled_shortcuts = CollectionProperty (type=GYAZ_AnimationTools_ShortcutItem)
         
    # ROOT MOTION TOOLS
    root_bone = StringProperty(
            name="Root (Prefix not added)",
            default='root'
            )     
    bone_prefix = StringProperty(
            name="Bone Prefix",
            default=''
            )
    bone_left_suffix = StringProperty(
            name="Bone Left Suffix",
            default='_l'
            )
    bone_right_suffix = StringProperty(
            name="Bone Right Suffix",
            default='_r'
            )          
    drive_bone = StringProperty(
            name="Drive Bone",
            default='hips'
            ) 
    drive_bone_forward = EnumProperty(
        items=(
            ('+X', "+X", ""),
            ('-X', "-X", ""),
            ('+Y', "+Y", ""),
            ('-Y', "-Y", ""),
            ('+Z', "+Z", ""),
            ('-Z', "-Z", "")
            ),
        default='+Z',
        name="Drive Bone Forward Axis",
        description="Drive bone's axis that points forward."
        )  
    toes = StringProperty(
            name="toes",
            default='toes'
            )
    
    # RIG REDUCER           
    #preset names
    preset_name_0 = StringProperty (default='-')
    preset_name_1 = StringProperty (default='-')
    preset_name_2 = StringProperty (default='-')
    preset_name_3 = StringProperty (default='-')
    preset_name_4 = StringProperty (default='-')
    preset_name_5 = StringProperty (default='-')
    preset_name_6 = StringProperty (default='-')
    preset_name_7 = StringProperty (default='-')
    preset_name_8 = StringProperty (default='-')
    preset_name_9 = StringProperty (default='-')
    preset_name_10 = StringProperty (default='-')
    preset_name_11 = StringProperty (default='-')
    preset_name_12 = StringProperty (default='-')
    preset_name_13 = StringProperty (default='-')
    preset_name_14 = StringProperty (default='-')
    preset_name_15 = StringProperty (default='-')
    preset_name_16 = StringProperty (default='-')
    preset_name_17 = StringProperty (default='-')
    preset_name_18 = StringProperty (default='-')
    preset_name_19 = StringProperty (default='-')
    
    #presets
    class GYAZ_ReduceRig_PresetItem (PropertyGroup):
        name = StringProperty (name='', description="'Bone to remove' / 'Vertex group to merge and remove'")
        name_children_only = BoolProperty (name='', default=False, description="Children only: only look for children, leave this bone and vertex group alone")               
        merge_to = StringProperty (name='', description="Vertex group to merge to. Leave it unset for just removing bone and vertex group")
    bpy.utils.register_class (GYAZ_ReduceRig_PresetItem)
    
    preset_0 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem)          
    preset_1 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem)        
    preset_2 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem)    
    preset_3 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_4 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_5 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_6 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_7 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_8 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_9 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_10 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_11 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_12 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_13 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_14 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_15 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_16 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_17 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_18 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_19 = CollectionProperty(type=GYAZ_ReduceRig_PresetItem)
    
    # RETARGET REST POSE
    location_bones = StringProperty (default='hips', name='Location Bones', description='e.g.: hips, some_other_bone')
    halve_frame_rate = BoolProperty (default=True, name='Halve Frame Rate')
    override_frame_rate = IntProperty (default=30, name='Override Frame Rate', description="ignored if 'Halve Frame Rate' is False")
    bake = BoolProperty (default=True, name='Bake', description='Bake action to target rig. Forced if Halve Frame Rate is True')
    use_target_bone_prefix = BoolProperty (default=True, name='Use Target Bone Prefix')

                          
    def draw(self, context):
        lay = self.layout
        lay.label ('')
        lay.label ("Offset Animation:")
        lay.label ("Global or local smooth offset of multiple bones or active object.")
        lay.label ("Location: View3d>Toolshelf>Tools>Offset Animation")
        lay.label ('')
        lay.label ('Extract Root Motion:')
        lay.label ("From the 'drive bone' of a full fk skeleton and apply it to Armature Object or root bone. The drive bone is at top of hierarchy, e.g. pelvis or hips. All bones should inherit rotation.")
        lay.label ("Location: 'View3d>Toolshelf>Tools>Extract Root Motion")
        lay.label ("Bones:")
        lay.prop (self, "bone_prefix")
        lay.prop (self, "bone_left_suffix")
        lay.prop (self, "bone_right_suffix")
        lay.prop (self, "drive_bone")
        lay.prop (self, "drive_bone_forward")
        lay.prop (self, "toes")
        lay.prop (self, "root_bone")
        lay.label (text="All these bones should be on a visible bone layer.")
        lay.label ('')
        lay.label ("Rig Reducer:")
        lay.label ("For creating Levels of Detail (LODs) of armatures and bone weights.")
        lay.label ("Location: View3d>Toolshelf>Create (select an armature)")        
        lay.label ('')
        lay.label ("Retarget Rest Pose:")
        lay.label ("Change the rest pose of an animation.")
        lay.label ("Location: View3d>Toolshelf>Animation>Animation>Action>Retarget Rest Pose")
        lay.label ("Settings:")
        lay.prop (self, 'location_bones')
        lay.prop (self, 'halve_frame_rate')
        row = lay.row ()
        row.prop (self, 'override_frame_rate')
        row.label ('')
        lay.prop (self, 'bake')
        lay.prop (self, 'use_target_bone_prefix')
        lay.label ('')
        lay.label ('Setup IK Constraint:')
        lay.label ('Location: Properties Editor > Data > Setup IK Constraint')
        lay.label ('')
        
#        debug rig riducer presets
#        for item in self.preset_0:
#            row = lay.row ()
#            row.prop (item, "name")
#            row.prop (item, "merge_to")
#            row.prop (item, "name_children_only")    
        
# Registration
def register():
    bpy.utils.register_class (GYAZ_AnimationTools_ShortcutItem)
    bpy.utils.register_class (GYAZ_Animation_Tools_Preferences)


def unregister():
    bpy.utils.unregister_class (GYAZ_Animation_Tools_Preferences)
    bpy.utils.unregister_class (GYAZ_AnimationTools_ShortcutItem)


register()

 
modulesNames = ['root_motion_tools', 'offset_animation', 'rig_reducer', 'retarget_rest_pose', 'menus', 'shortcuts']
 
import sys
import importlib

modulesFullNames = []
modulesFullNames_values = []

for currentModuleName in modulesNames:
    modulesFullNames.append ([currentModuleName, __name__+'.'+currentModuleName])
    modulesFullNames_values.append (__name__+'.'+currentModuleName)
 
for currentModuleFullName in modulesFullNames_values:
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames_values:
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames_values:
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
if __name__ == "__main__":
    register()