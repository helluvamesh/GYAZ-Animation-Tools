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

prefs = bpy.context.user_preferences.addons[__package__].preferences
addon_shortcuts = prefs.addon_shortcuts
disabled_shortcuts = prefs.disabled_shortcuts

def save_shortcut (km, kmi):
    i = addon_shortcuts.add ()
    i.km_name, i.kmi_idname, i.type, i.value, i.shift, i.ctrl, i.alt, i.prop = km.name, kmi.idname, kmi.type, kmi.value, kmi.shift, kmi.ctrl, kmi.alt, kmi.properties.name if hasattr (kmi.properties, 'name') else ''

def save_dis_shortcut (km, kmi):
    i = disabled_shortcuts.add ()
    i.km_name, i.kmi_idname, i.type, i.value, i.shift, i.ctrl, i.alt, i.prop = km.name, kmi.idname, kmi.type, kmi.value, kmi.shift, kmi.ctrl, kmi.alt, kmi.properties.name if hasattr (kmi.properties, 'name') else ''


def register():
    
    wm = bpy.context.window_manager
   
    # disable default shortcuts
    for km in wm.keyconfigs.user.keymaps:
        if km.name == 'Pose': 
            for kmi in km.keymap_items:
                if kmi.idname == 'wm.call_menu' and kmi.type=='W' and kmi.shift==False and kmi.ctrl==False and kmi.alt==False:
                    if kmi.properties.name == 'VIEW3D_MT_pose_specials':
                        kmi.active = False
                        save_dis_shortcut (km, kmi)
                        
                elif kmi.idname == 'wm.call_menu' and kmi.type=='A' and kmi.shift==False and kmi.ctrl==True and kmi.alt==False:
                    if kmi.properties.name == 'VIEW3D_MT_pose_apply':
                        kmi.active = False
                        save_dis_shortcut (km, kmi)  
                                                           
                elif kmi.idname == 'wm.call_menu' and kmi.type=='W' and kmi.shift==True and kmi.ctrl==False and kmi.alt==False:
                    if kmi.properties.name == 'VIEW3D_MT_bone_options_toggle':
                        kmi.active = False
                        save_dis_shortcut (km, kmi)     
    
    
    # add addon shortcuts
    for km in wm.keyconfigs.user.keymaps:            

        # Object Mode
        if km.name == 'Object Mode':
          
            kmi = km.keymap_items.new ('wm.call_menu', 'F', 'PRESS')
            kmi.properties.name = "Me_GYAZ_OffsetAnimation"
            save_shortcut (km, kmi)
            
            kmi = km.keymap_items.new ('wm.call_menu', 'W', 'PRESS', shift=True)
            kmi.properties.name = "Me_GYAZ_ExtractRootMotion"
            save_shortcut (km, kmi)
            
        # Pose Mode
        elif km.name == 'Pose':
          
            kmi = km.keymap_items.new ('wm.call_menu', 'F', 'PRESS')
            kmi.properties.name = "Me_GYAZ_OffsetAnimation"
            save_shortcut (km, kmi)
            
            kmi = km.keymap_items.new ('wm.call_menu', 'W', 'PRESS')
            kmi.properties.name = "Me_GYAZ_Pose"
            save_shortcut (km, kmi)
            
            kmi = km.keymap_items.new ('wm.call_menu', 'E', 'PRESS')
            kmi.properties.name = "Me_GYAZ_Armature"
            save_shortcut (km, kmi)
            
        # Dopesheet
        if km.name == 'Dopesheet':
          
            kmi = km.keymap_items.new ('wm.call_menu', 'W', 'PRESS')
            kmi.properties.name = "Me_GYAZ_Dopesheet"
            save_shortcut (km, kmi)
            
        # Graoh Editor
        if km.name == 'Graph Editor':
          
            kmi = km.keymap_items.new ('wm.call_menu', 'W', 'PRESS')
            kmi.properties.name = "Me_GYAZ_GraphEditor"
            save_shortcut (km, kmi)
            
        # Weight Paint Mode
        if km.name == 'Weight Paint':
          
            kmi = km.keymap_items.new ('wm.call_menu', 'Q', 'PRESS')
            kmi.properties.name = "Me_GYAZ_WeightTools"
            save_shortcut (km, kmi)
                  


def unregister ():
     
    wm = bpy.context.window_manager
    
    addon_shortcuts = prefs.addon_shortcuts
    disabled_shortcuts = prefs.disabled_shortcuts
    
    keymaps = wm.keyconfigs.user.keymaps
    for km in keymaps:
        for kmi in km.keymap_items:
            for i in addon_shortcuts:
                try:
                    if km.name==i.km_name and kmi.idname==i.kmi_idname and kmi.type==i.type and kmi.value==i.value and kmi.shift==i.shift and kmi.ctrl==i.ctrl and kmi.alt==i.alt:
                        if hasattr (kmi.properties, 'name'):
                            if kmi.properties.name == i.prop:
                                km.keymap_items.remove (kmi)
                        else:
                            km.keymap_items.remove (kmi)
                except:
                    ""
                    
            for di in disabled_shortcuts:
                try:
                    if km.name==di.km_name and kmi.idname==di.kmi_idname and kmi.type==di.type and kmi.value==di.value and kmi.shift==di.shift and kmi.ctrl==di.ctrl and kmi.alt==di.alt:
                        if hasattr (kmi.properties, 'name'):
                            if kmi.properties.name == di.prop:
                                kmi.active = True
                        else:
                            kmi.active = True
                except:
                    ""                   
  
if __name__ == "__main__":   
    register()