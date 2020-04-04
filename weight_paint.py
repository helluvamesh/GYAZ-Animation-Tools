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
from bpy.types import Operator, MESH_MT_vertex_group_context_menu
from bpy.props import BoolProperty


class Op_GYAZ_CopyMirrorVertexGroup (Operator):
       
    bl_idname = "object.gyaz_vertex_group_copy_mirror"  
    bl_label = "Copy Mirror Vertex Group"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    use_topology: BoolProperty()
    
    #operator function
    def execute(self, context):
        
        left_suffixes = ["_l", "_L", ".l", ".L"]
        right_suffixes = ["_r", "_R", ".r", ".R"]
        
        obj = bpy.context.object
        vgroups = obj.vertex_groups
        if len(vgroups) == 0:
            return {"FINISHED"}
        
        name = vgroups[vgroups.active_index].name
        
        found_suffix = False
        
        for i in range(0, len(left_suffixes)):
            
            left_suffix = left_suffixes[i]
            right_suffix = right_suffixes[i]
            
            if name.endswith(left_suffix):
                stem = name[0 : -len(left_suffix)]
                mirrored_name = stem + right_suffix
                found_suffix = True
                break
                
            elif name.endswith(right_suffix):
                stem = name[0 : -len(right_suffix)]
                mirrored_name = stem + left_suffix
                found_suffix = True
                break
                
        if found_suffix == False:
            return {"FINISHED"}
        
        mirrored_vgroup = vgroups.get(mirrored_name)
        if mirrored_vgroup != None:
            vgroups.remove(mirrored_vgroup)
            
        bpy.ops.object.vertex_group_copy()
        bpy.ops.object.vertex_group_mirror(use_topology=self.use_topology)
        last_group = vgroups[-1]
        if last_group.name == name + "_copy":
            last_group.name = mirrored_name
        
        return {"FINISHED"}
        
#######################################################
#######################################################

#REGISTER
#everything should be registeres here

def register():

    bpy.utils.register_class (Op_GYAZ_CopyMirrorVertexGroup)
    
    def ui(self, context):
        lay = self.layout
        lay.separator()
        lay.operator(Op_GYAZ_CopyMirrorVertexGroup.bl_idname, text="Copy Mirror", icon="ARROW_LEFTRIGHT").use_topology = False
        lay.operator(Op_GYAZ_CopyMirrorVertexGroup.bl_idname, text="Copy Mirror (Topology)").use_topology = True
        
    MESH_MT_vertex_group_context_menu.append(ui)

def unregister ():
    
    bpy.utils.unregister_class (Op_GYAZ_CopyMirrorVertexGroup)
  
  
if __name__ == "__main__":   
    register()      