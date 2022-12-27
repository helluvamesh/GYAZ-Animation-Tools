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


def report (self, item, error_or_info):
    self.report({error_or_info}, item)
    

def popup (item, icon, title='Anim Tools'):
    def draw(self, context):
        self.layout.label(text=item)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
    print (item)
    

def popup_lines (lines, icon, title='Anim Tools'):
    def draw(self, context):
        for line in lines:
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


#lerp
def lerp(A, B, alpha):
    x = A*(1-alpha)+B*alpha
    return x


#smooth lerp
def smooth_lerp (A, B, alpha, strength):
    #default strength = 2
    if alpha <= 0.5:      
        alpha = (alpha * 2) ** strength / 2
    else:
        alpha = 1 - ((1 - alpha) * 2) ** strength / 2
        
    x = A*(1-alpha)+B*alpha 
    
    return x


#ease in lerp
def ease_in_lerp (A, B, alpha, strength):
    
    alpha **= strength
    x = A*(1-alpha)+B*alpha  
    
    return x

#ease out lerp
#ease in lerp
def ease_out_lerp (A, B, alpha, strength):
    
    alpha **= 1/strength
    x = A*(1-alpha)+B*alpha  
    
    return x    

    
# calc pole angle
def signed_angle (vector_u, vector_v, normal):
    #normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle
    return angle


def get_pole_angle (base_bone, constraint_bone, pole_bone):
    pole_location = pole_bone.head
    pole_normal = (constraint_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)


def set_end_mode (start_mode):
    if 'EDIT' in start_mode:
        end_mode = 'EDIT'
    elif start_mode == 'PAINT_TEXTURE':
        end_mode = 'TEXTURE_PAINT'
    elif start_mode == 'PAINT_VERTEX':
        end_mode = 'VERTEX_PAINT'
    elif start_mode == 'PAINT_WEIGHT':
        end_mode = 'WEIGHT_PAINT'                    
    else:
        end_mode = start_mode
    bpy.ops.object.mode_set (mode=end_mode)


def area_of_type (type_name):
    for area in bpy.context.screen.areas:
        if area.type == type_name:
            return area
 
        
def areas_of_type (type_name):
    areas = []
    for area in bpy.context.screen.areas:
        if area.type == type_name:
            areas.append (area)
    return areas


def set_properties_context (data):
    prop_editors = areas_of_type ('PROPERTIES')
    for e in prop_editors:
        e.spaces[0].context = data
       
        
def list_to_visual_list (list):
    return ', '.join(list)


def select_only (obj):
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set (mode = 'OBJECT')
    bpy.ops.object.select_all (action='DESELECT')
    obj.select_set (True)
    bpy.context.view_layer.objects.active = obj
    
    
def _get_descendants(bone, list):
    for child in bone.children:
        list.append(child.name)
        _get_descendants(child, list)
        
        
def get_all_descendant_bone_names(bone):
    list = []
    _get_descendants(bone, list)
    return list


def deselect_all_bones(rig):
    for bone in rig.data.bones:
        bone.select = False
