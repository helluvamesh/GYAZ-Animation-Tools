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
 "author": "helluvamesh",   
 "version": (4, 2, 1),   
 "blender": (4, 2, 0),   
 "location": "",   
 "description": "Various animation tools",
 "warning": "",   
 "wiki_url": "",   
 "tracker_url": "",   
 "category": "Animation"}



import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import *


class GYAZ_AnimationTools_ShortcutItem (PropertyGroup):
    km_name: StringProperty (default='')
    kmi_idname: StringProperty (default='')
    type: StringProperty (default='')
    value: StringProperty (default='')
    shift: BoolProperty (default=False)
    ctrl: BoolProperty (default=False)
    alt: BoolProperty (default=False)
    prop: StringProperty (default='')
    

def shortcut_activation(self, context):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.shortcuts_active:
        from .shortcuts import activate_shortcuts
        activate_shortcuts()
    else:
        from .shortcuts import deactivate_shortcuts
        deactivate_shortcuts() 


class GYAZ_AnimationTools_Preferences (AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    bl_label = 'Activate Addon Shortcuts'
    bl_description = 'Warning! This also overwrites built-in animation menus'
    
    addon_shortcuts: CollectionProperty (type=GYAZ_AnimationTools_ShortcutItem)
    disabled_shortcuts: CollectionProperty (type=GYAZ_AnimationTools_ShortcutItem)
    
    shortcuts_active: BoolProperty(name='Use Addon Shortcuts',
                                   description="Warning! This also changes Blender's default animation menus",
                                   update=shortcut_activation
                                   )
         
    # ROOT MOTION TOOLS
    root_bone: StringProperty(
            name="Root",
            default='root'
            )
    drive_bone: StringProperty(
            name="Drive Bone",
            default='hips'
            )
    
    # RIG REDUCER           
    #preset names
    preset_name_0: StringProperty (default='-')
    preset_name_1: StringProperty (default='-')
    preset_name_2: StringProperty (default='-')
    preset_name_3: StringProperty (default='-')
    preset_name_4: StringProperty (default='-')
    preset_name_5: StringProperty (default='-')
    preset_name_6: StringProperty (default='-')
    preset_name_7: StringProperty (default='-')
    preset_name_8: StringProperty (default='-')
    preset_name_9: StringProperty (default='-')
    preset_name_10: StringProperty (default='-')
    preset_name_11: StringProperty (default='-')
    preset_name_12: StringProperty (default='-')
    preset_name_13: StringProperty (default='-')
    preset_name_14: StringProperty (default='-')
    preset_name_15: StringProperty (default='-')
    preset_name_16: StringProperty (default='-')
    preset_name_17: StringProperty (default='-')
    preset_name_18: StringProperty (default='-')
    preset_name_19: StringProperty (default='-')
    
    #presets
    class GYAZ_ReduceRig_PresetItem (PropertyGroup):
        name: StringProperty (name='', description="'Bone to remove' / 'Vertex group to merge and remove'")
        name_children_only: BoolProperty (name='', default=False, description="Children only: only look for children, leave this bone and vertex group alone")               
        merge_to: StringProperty (name='', description="Vertex group to merge to. Leave it unset for just removing bone and vertex group")
    bpy.utils.register_class (GYAZ_ReduceRig_PresetItem)
    
    preset_0: CollectionProperty(type=GYAZ_ReduceRig_PresetItem)          
    preset_1: CollectionProperty(type=GYAZ_ReduceRig_PresetItem)        
    preset_2: CollectionProperty(type=GYAZ_ReduceRig_PresetItem)    
    preset_3: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_4: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_5: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_6: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_7: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_8: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_9: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_10: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_11: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_12: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_13: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_14: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_15: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_16: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_17: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_18: CollectionProperty(type=GYAZ_ReduceRig_PresetItem) 
    preset_19: CollectionProperty(type=GYAZ_ReduceRig_PresetItem)
                          
    def draw(self, context):
        lay = self.layout
        lay.label (text='')
        lay.label (text="Offset Animation:")
        lay.label (text="Global or local smooth offset of multiple bones or active object.")
        lay.label (text="Location: 3D View in Object/Pose mode > N Panel > Animation > Offset Animation")
        lay.label (text='')
        lay.label (text='Extract Root Motion:')
        lay.label (text="From the 'drive bone' of a full fk skeleton and apply it to Armature Object or root bone. The drive bone is at top of hierarchy, e.g. pelvis or hips. All bones should inherit rotation.")
        lay.label (text="Location: 3D View in Object mode > N Panel > Animation > Extract Root Motion")
        lay.prop (self, "drive_bone")
        lay.prop (self, "root_bone")
        lay.label (text='')
        lay.label (text="Rig Reducer:")
        lay.label (text="For creating Levels of Detail (LODs) of armatures and bone weights.")       
        lay.label (text="Location: 3D View in Object / Pose mode > N Panel > Animation > Reduce Rig")        
        lay.label (text='')
        lay.label (text="Retarget Animation:")
        lay.label (text="Location: 3D View in Object / Pose mode > N Panel > Animation > Retarget")
        lay.label (text='')
        lay.label (text='Setup IK Constraint:')
        lay.label (text='Location: 3D View in Object / Pose mode > N Panel > Animation > Setup IK Constraint')
        lay.label (text='')
        lay.label (text='Pose menu: 3D View in Pose mode > W')
        lay.label (text='Selection menu: 3D View in Pose mode > CTRL + D')
        lay.label (text='Weight paint menu: 3D View in Weight Paint mode > W')
        lay.prop (self, 'shortcuts_active')
        lay.label (text='')
        
#        debug rig riducer presets
#        for item in self.preset_0:
#            row = lay.row ()
#            row.prop (item, "name")
#            row.prop (item, "merge_to")
#            row.prop (item, "name_children_only")    
        
# Registration
def register():
    bpy.utils.register_class (GYAZ_AnimationTools_ShortcutItem)
    bpy.utils.register_class (GYAZ_AnimationTools_Preferences)


def unregister():
    bpy.utils.unregister_class (GYAZ_AnimationTools_Preferences)
    bpy.utils.unregister_class (GYAZ_AnimationTools_ShortcutItem)


register()

 
modulesNames = ['animation', 'offset_animation', 'root_motion_tools', 'retarget', 'weight_paint', 'rigging', 'rig_reducer', 'menus', 'shortcuts']
 
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