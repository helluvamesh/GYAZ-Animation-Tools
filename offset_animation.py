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
from bpy.types import Panel, Operator, Scene, PropertyGroup, Menu
from bpy.props import *
import os
import mathutils
from mathutils import Vector, Quaternion
from .utils import report
from .utils import popup
from .utils import lerp
from .utils import smooth_lerp
from .utils import ease_in_lerp
from .utils import ease_out_lerp
from .utils import signed_angle
from .utils import get_pole_angle
from .utils import set_end_mode
from .utils import area_of_type
from .utils import areas_of_type
from .utils import set_properties_context 
from .utils import list_to_visual_list



def check (self):
    good_to_go = False
    obj = bpy.context.object
    if obj.animation_data != None:
        if obj.animation_data.action != None:
            good_to_go = True
    
    if good_to_go == False:
        report (self, "Object has no active action.", "WARNING")
    
    return good_to_go


#OPERATORS

#OFFSET ANIMATION: GLOBAL
class Op_GYAZ_OffsetAnim (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_offset_anim"  
    bl_label = "Offset Anim"
    bl_description = "Offset anim of selected bones. Global: from start to end of timeline, Local: between two markers, Local 2: between two markers with a user defined falloff curve, Local 4: marker1-2: falloff, m2-3: constant, m3-4: falloff" #For best results with smooth falloff you should sample the fcurves but you do not have to do so, though in that case you are responsible for having enough keyframes.
    bl_options = {'REGISTER', 'UNDO'}
    
    #properties
    Mode: EnumProperty(
        items=(
            ('GLOBAL', "GLOBAL", ""),
            ('SIMPLE_LOCAL', "SIMPLE LOCAL", ""),
            ('LOCAL_2', "LOCAL 2", ""),
            ('LOCAL_4', "LOCAL 4", "")),
        name="Mode",
        default='GLOBAL')

    
    #operator function
    def execute(self, context):
        
        def main ():
            
            #!!!!!!!!!!!!!!!!!!!!!!!!
            #Object animation offsetting is implemented with a hack: references to bones are overridden to point to the active object.
            #!!!!!!!!!!!!!!!!!!!!!!!!
        
            #scene properties:
            
            # Assign a collection
            class VectorPropertyItem(bpy.types.PropertyGroup):
                value = bpy.props.FloatVectorProperty()

            bpy.utils.register_class(VectorPropertyItem)
            
            class QuaternionPropertyItem(bpy.types.PropertyGroup):
                value = bpy.props.FloatVectorProperty(size=4)

            bpy.utils.register_class(QuaternionPropertyItem)
            
            #offseted transform
            bpy.types.Scene.OffLocs = \
                bpy.props.CollectionProperty(type=VectorPropertyItem)

            bpy.types.Scene.OffRotsQ = \
                bpy.props.CollectionProperty(type=QuaternionPropertyItem)
            
            bpy.types.Scene.OffRotsE = \
                bpy.props.CollectionProperty(type=VectorPropertyItem)        

            bpy.types.Scene.OffSca = \
                bpy.props.CollectionProperty(type=VectorPropertyItem)
                    
            #transform difference 
            bpy.types.Scene.DiffLocs = \
                bpy.props.CollectionProperty(type=VectorPropertyItem)

            bpy.types.Scene.DiffRotsQ = \
                bpy.props.CollectionProperty(type=QuaternionPropertyItem)
            
            bpy.types.Scene.DiffRotsE = \
                bpy.props.CollectionProperty(type=VectorPropertyItem)        

            bpy.types.Scene.DiffScas = \
                bpy.props.CollectionProperty(type=VectorPropertyItem)
            
            scene = context.scene
            
            blend_falloff = scene.GYAZ_OffsetAnimFalloff
            
            s1 = int (scene.GYAZ_OffsetAnimFalloffStrength_1)
            #s2 = int (scene.GYAZ_OffsetAnimFalloffStrength_2)
            s2 = 0
            blend_falloff_strength = float(str(s1)+'.'+str(s2))
            
            
            #########################################################################    
            #########################################################################    
                
            obj = bpy.context.active_object

            scene = bpy.context.scene        
            current_frame = scene.frame_current
            first_frame = scene.frame_start
            last_frame = scene.frame_end
            
            OffLocs = scene.OffLocs
            OffRotsQ = scene.OffRotsQ
            OffRotsE = scene.OffRotsE
            OffScas = scene.OffSca
            
            DiffLocs = scene.DiffLocs
            DiffRotsQ = scene.DiffRotsQ
            DiffRotsE = scene.DiffRotsE
            DiffScas = scene.DiffScas
            
            #markers
            markers = scene.timeline_markers
                            
            m1 = 0
            m2 = 0
            m3 = 0
            m4 = 0
                
            if self.Mode == 'SIMPLE_LOCAL' or self.Mode == 'LOCAL_2':
                if len(markers) != 0:
                    markers = [markers[0].frame, markers[1].frame]
                    sorted_markers = sorted (markers)
                    m1 = sorted_markers [0]
                    m2 = sorted_markers [1]
                    
            if self.Mode == 'LOCAL_4':
                if len(markers) != 0:
                    markers = [markers[0].frame, markers[1].frame, markers[2].frame, markers[3].frame]
                    sorted_markers = sorted (markers)
                    m1 = sorted_markers [0]
                    m2 = sorted_markers [1]
                    m3 = sorted_markers [2]
                    m4 = sorted_markers [3]
   
            #get selected bones
            if obj.type == 'ARMATURE':
                selected_bones = []
                bones = obj.data.bones
                for bone in bones:
                    if bone.select == True:
                        selected_bones.append (bone.name)
                                    
            #get active action's name
            action_name = (obj.animation_data.action.name
            if obj.animation_data is not None and
                obj.animation_data.action is not None
            else "")
                    
            if action_name != None:
                if bpy.context.mode == 'POSE':               
                    pbones = obj.pose.bones
                
                #HACK: object animation
                if bpy.context.mode == 'OBJECT':
                    selected_bones = [obj]
                    pbone = obj
                
                for index, bone in enumerate (selected_bones):
                    if bpy.context.mode == 'POSE': 
                        pbone = pbones[bone]
                    
                    #offseted transform
                    item = OffLocs.add()
                    item.value = pbone.location
                    
                    if pbone.rotation_mode == 'QUATERNION':
                        item = OffRotsQ.add()
                        item.value = pbone.rotation_quaternion
                    else:                    
                        item = OffRotsE.add()
                        item.value = pbone.rotation_euler
                        
                    item = OffScas.add()
                    item.value = pbone.scale 
                                 
                #delete offset
                scene.frame_set (current_frame + 1)
                scene.frame_set (current_frame)
                
                #go on    
                for index, bone in enumerate (selected_bones):
                    if bpy.context.mode == 'POSE':
                        pbone = pbones[bone]
                    
                    #HACK: object animation
                    if bpy.context.mode == 'OBJECT':
                        selected_bones = [obj]
                        pbone = obj                                 
                
                    #initial transform                    
                    IniLoc = pbone.location
                    
                    if pbone.rotation_mode == 'QUATERNION':
                        IniRotQ = pbone.rotation_quaternion
                    else:
                        IniRotE = pbone.rotation_euler
                    
                    IniSca = pbone.scale

                    #transform difference
                    DiffLoc = Vector ((OffLocs[index].value[:])) - IniLoc
                    
                    if pbone.rotation_mode == 'QUATERNION':
                        DiffRotQ = Quaternion ((OffRotsQ[index].value[:])) - IniRotQ
                    else:
                        DiffRotE = Vector ((OffRotsE[index].value[:])) - Vector (IniRotE)
                    
                    DiffSca = Vector ((OffScas[index].value[:])) - IniSca
                    
                    
                    #function: offset fcurves                        
                    def offset_transform_fcurves (attribute, offset_value, m1, m2, m3, m4):
                        if attribute in fc.data_path:
                            keys = fc.keyframe_points
                            for key in keys:
                                
                                def adjust_fcurve_all (offset_value):
                                    def adjust_fcurve (i):
                                        if fc.array_index == i:
                                            key.co.y += offset_value[i]
                                            key.handle_left.y += offset_value[i]
                                            key.handle_right.y += offset_value[i]
                                            
                                    adjust_fcurve (0)
                                    adjust_fcurve (1) 
                                    adjust_fcurve (2) 
                                    adjust_fcurve (3)
                                    
                                def falloff_selector ():
                                    if blend_falloff == 'LINEAR':
                                        new_percentage = lerp (interpolation_start, interpolation_end, blend_percentage)
                                    elif blend_falloff == 'SMOOTH':
                                        new_percentage = smooth_lerp (interpolation_start, interpolation_end, blend_percentage, blend_falloff_strength)
                                    elif blend_falloff == 'EASE_IN':
                                        new_percentage = ease_in_lerp (interpolation_start, interpolation_end, blend_percentage, blend_falloff_strength)
                                    elif blend_falloff == 'EASE_OUT':
                                        new_percentage = ease_out_lerp (interpolation_start, interpolation_end, blend_percentage, blend_falloff_strength)
                                    
                                    return new_percentage
                                
                                if self.Mode == 'GLOBAL':
                                    
                                    adjust_fcurve_all (offset_value)
                                   
                                   
                                elif self.Mode == 'SIMPLE_LOCAL':
                                    frame = key.co.x
                                    if m1 <= frame <= m2:
                                
                                        adjust_fcurve_all (offset_value)
                                       
                                elif self.Mode == 'LOCAL_2':
                                    frame = key.co.x
                                    frame_offset = 0
                                    
                                    #blend in
                                    if m1 != current_frame:
                                        
                                        frame_offset = 1
                                    
                                        blend_start = m1
                                        blend_end = current_frame
                                        interpolation_start = 0
                                        interpolation_end = 1
                                           
                                        blend_length = blend_end - blend_start
                                        if blend_start <= frame <= blend_end:
                                            current_blend_frame = frame - blend_start
                                            blend_percentage = current_blend_frame / blend_length
                                            
                                            adjust_fcurve_all (offset_value * falloff_selector())
                                    
                                    #blend out
                                    if m2 != current_frame:  
                                                                  
                                        blend_start = current_frame + frame_offset
                                        blend_end = m2
                                        interpolation_start = 1
                                        interpolation_end = 0
                                        interpolation_strength = 2
                                        
                                        blend_length = blend_end - blend_start
                                        if blend_start <= frame <= blend_end:
                                            current_blend_frame = frame - blend_start
                                            blend_percentage = current_blend_frame / blend_length
                                            
                                            adjust_fcurve_all (offset_value * falloff_selector())
                                        
                                
                                elif self.Mode == 'LOCAL_4':
                                    frame = key.co.x
                                    
                                    #blend in
                                    blend_start = m1
                                    blend_end = m2
                                    interpolation_start = 0
                                    interpolation_end = 1
                                    interpolation_strength = 2
                                       
                                    blend_length = blend_end - blend_start
                                    if blend_start <= frame <= blend_end:
                                        current_blend_frame = frame - blend_start
                                        blend_percentage = current_blend_frame / blend_length
                                        
                                        adjust_fcurve_all (offset_value * falloff_selector())
                                    
                                        
                                    #keep offset
                                    if m2+1 <= frame <= m3:
                                
                                        adjust_fcurve_all (offset_value)
                                   
                                    #blend out                                
                                    blend_start = m3 + 1
                                    blend_end = m4
                                    interpolation_start = 1
                                    interpolation_end = 0
                                    interpolation_strength = 2
                                    
                                    blend_length = blend_end - blend_start
                                    if blend_start <= frame <= blend_end:
                                        current_blend_frame = frame - blend_start
                                        blend_percentage = current_blend_frame / blend_length
                                        new_percentage = smooth_lerp (interpolation_start, interpolation_end, blend_percentage, interpolation_strength)
                                        
                                        adjust_fcurve_all (offset_value * falloff_selector())        
                               
                    #filter f-curves for bone name
                    action = bpy.data.actions [action_name]
                    fcurves = action.fcurves
                    for fc in fcurves:
                        if bpy.context.mode == 'POSE':
                            if 'pose.bones["'+bone+'"].location' in fc.data_path:
                                offset_transform_fcurves ('location', DiffLoc, m1, m2, m3, m4)
                                
                            if 'pose.bones["'+bone+'"].scale' in fc.data_path:
                                offset_transform_fcurves ('scale', DiffSca, m1, m2, m3, m4)
                            
                            if pbone.rotation_mode == 'QUATERNION':    
                                if 'pose.bones["'+bone+'"].rotation_quaternion' in fc.data_path:
                                    offset_transform_fcurves ('rotation_quaternion', DiffRotQ, m1, m2, m3, m4)
                            
                            else: 
                                if 'pose.bones["'+bone+'"].rotation_euler' in fc.data_path:
                                    offset_transform_fcurves ('rotation_euler', DiffRotE, m1, m2, m3, m4)
                                    
                        #OBJECT ANIMATION
                        if bpy.context.mode == 'OBJECT':
                            if fc.data_path.startswith ('location'):
                                offset_transform_fcurves ('location', DiffLoc, m1, m2, m3, m4)
                                
                            if fc.data_path.startswith ('scale'):
                                offset_transform_fcurves ('scale', DiffSca, m1, m2, m3, m4)
                            
                            if pbone.rotation_mode == 'QUATERNION':    
                                if fc.data_path.startswith ('rotation_quaternion'):
                                    offset_transform_fcurves ('rotation_quaternion', DiffRotQ, m1, m2, m3, m4)
                            
                            else: 
                                if fc.data_path.startswith ('rotation_euler'):
                                    offset_transform_fcurves ('rotation_euler', DiffRotE, m1, m2, m3, m4)                                              
                        
            
        ####################################################################    
        ####################################################################    
            
            #CLEAN UP
                                                    
            #clear collections
            OffLocs.clear()
            del OffLocs
            DiffLocs.clear()
            del DiffLocs
            
            if pbone.rotation_mode == 'QUATERNION':
                OffRotsQ.clear()
                del OffRotsQ
                DiffRotsQ.clear()
                del DiffRotsQ
            else:
                OffRotsE.clear()
                del OffRotsE
                DiffRotsE.clear()
                del DiffRotsE
                
            OffScas.clear()
            del OffScas
            DiffScas.clear()
            del DiffScas
            
            #delete markers
            scene.timeline_markers.clear ()
            
            #force viewport update
            scene.frame_set (current_frame + 1)
            scene.frame_set (current_frame)
        
        
        # general check
        good_to_go = check (self)
        
        if good_to_go:
            #marker check    
            markers = bpy.context.scene.timeline_markers
            if self.Mode == 'GLOBAL':    
                main ()
                
            elif self.Mode == 'SIMPLE_LOCAL' or self.Mode == 'LOCAL_2':
                if len(markers) == 2:
                    main ()
                else:
                    report (self, "Exactly 2 markers should be placed on the timeline.", "WARNING")

            elif self.Mode == 'LOCAL_4':
                if len(markers) == 4:
                    main ()
                else:
                    report (self, "Exactly 4 markers should be placed on the timeline.", "WARNING")
            
                          
        #end of operator
        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return bpy.context.mode == 'POSE' and obj != None or bpy.context.mode == 'OBJECT' and obj != None
    
    
#SAMPLE FCURVES
class Op_GYAZ_AnimSampleFcurves (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_sample_fcurves"  
    bl_label = "Sample Fcurves"
    bl_description = "Places a keyframe on every frame for selected bones. For best results with local offset with smooth falloff you should sample the fcurves, if you do not, you are responsible for having enough keyframes for decent results"
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):
        
        # general check
        good_to_go = check (self)
        
        if good_to_go:        
        
            obj = bpy.context.active_object
            scene = bpy.context.scene
            first_frame = scene.frame_start
            last_frame = scene.frame_end
                                        
            #get active action's name
            action_name = (obj.animation_data.action.name
            if obj.animation_data is not None and
                obj.animation_data.action is not None
            else "")
                    
            if action_name != None:
                                           
                #make dope sheet active area
                bpy.context.area.type = 'DOPESHEET_EDITOR'
                bpy.context.space_data.mode = 'ACTION'

                #insert keyframes to every fcurve of selected bones or object
                for frameIndex in range(first_frame, last_frame+1):
                    scene.frame_set(frameIndex)
                    bpy.ops.action.keyframe_insert(type='SEL')
                        
            bpy.context.area.type = 'VIEW_3D'

                
        #end of operator
        return {'FINISHED'}
    
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return bpy.context.mode == 'POSE' and obj != None or bpy.context.mode == 'OBJECT' and obj != None
        

#DELETE FCURVES
class Op_GYAZ_DeleteTimelineMarkers (bpy.types.Operator):
       
    bl_idname = "anim.gyaz_delete_timeline_markers"  
    bl_label = "Delete Timeline Markers"
    bl_description = "Delete all timeline markers"
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):
        
        scene = bpy.context.scene
        markers = scene.timeline_markers
        
        markers.clear ()

        #end of operator
        return {'FINISHED'}
    
    
class Op_GYAZ_SetupIKConstraint_GetActiveBone (bpy.types.Operator):
       
    bl_idname = "pose.setup_ik_constraint_get_active_bone"  
    bl_label = "Set Active Bone As"
    bl_description = "Set active pose bone (in pose mode)"
    
    prop_name: StringProperty (name='Prop Name', default='base_bone')
    
    #operator function
    def execute(self, context):      
        scene = bpy.context.scene
        owner = scene.gyaz_set_pole_angle
        
        if bpy.context.mode == 'POSE':
            prop = getattr (owner, self.prop_name)        
            if prop != None:
                prop = setattr (owner, self.prop_name, bpy.context.active_bone.name)
            
        return {'FINISHED'}
    
    
class Op_GYAZ_SetupIKConstraint (bpy.types.Operator):
       
    bl_idname = "pose.setup_ik_constraint"  
    bl_label = "Setup IK Constraint"
    bl_description = "Add an IK constraint to the constraint bone with all the settings done"
    bl_options = {'REGISTER', 'UNDO'}
    
    #operator function
    def execute(self, context):
        
        scene = bpy.context.scene
        owner = scene.gyaz_set_pole_angle
        
        start_mode = bpy.context.mode
        
        rig = bpy.context.object
        if rig.type == 'ARMATURE':
        
            if bpy.context.mode != 'EDIT_ARMATURE':
                bpy.ops.object.mode_set (mode='EDIT')
            ebones = rig.data.edit_bones
            
            base_bone_name = owner.base_bone
            constraint_bone_name = owner.constraint_bone
            ik_bone_name = owner.ik_bone
            pole_bone_name = owner.pole_bone
            
            base_bone = ebones.get (base_bone_name)
            constraint_bone = ebones.get (constraint_bone_name)
            ik_bone = ebones.get (ik_bone_name)
            pole_bone = ebones.get (pole_bone_name)
            
            # missing bones
            missing_bones = []
            if base_bone == None:
                missing_bones.append ('Base Bone')
            if constraint_bone == None:
                missing_bones.append ('Constraint Bone')
            if ik_bone == None:
                missing_bones.append ('IK Bone')
            if pole_bone == None:
                missing_bones.append ('Pole Bone')
            
            if len (missing_bones) > 0:
                set_end_mode (start_mode)
                popup ('Bones not found: '+list_to_visual_list(missing_bones), 'ERROR', 'Setup IK Constraints')
            else:
            
                # get pole angle
                pole_angle = get_pole_angle (base_bone, constraint_bone, pole_bone)
                
                # get ik constraint
                bpy.ops.object.mode_set (mode='POSE')
                pbones = rig.pose.bones
                cs = pbones[constraint_bone_name].constraints
                
                ik_constraint = None
                for c in cs:
                    if c.type == 'IK':
                        ik_constraint = c
                        break
                
                # create ik constraint, if not found any    
                if ik_constraint == None:
                    ik_constraint = cs.new (type='IK')
                
                # ik constraint settings
                c = ik_constraint  
                c.target = rig
                c.subtarget = ik_bone_name
                c.pole_target = rig
                c.pole_subtarget = pole_bone_name
                c.pole_angle = pole_angle
                c.chain_count = 2
                
                # set constraint bone to be the active bone
                bones = rig.data.bones
                bone = bones.get (constraint_bone_name)
                if bone != None:
                    bones.active = bone
                    bone.select = True
                
                # finalize    
                set_end_mode (start_mode)
                set_properties_context ('BONE_CONSTRAINT')
        
        #end of operator
        return {'FINISHED'}
    
                      
#######################################################
#######################################################
    
#UI 

#Tools
class PG_GYAZ_SetPoleAngle (PropertyGroup):
    base_bone: StringProperty (name='Base Bone', default='', description='E.g.: upperarm, thigh')
    constraint_bone: StringProperty (name='Constraint Bone', default='', description='E.g.: forearm, shin')
    ik_bone: StringProperty (name='IK Target Bone', default='', description='E.g.: ik_hand, ik_foot')
    pole_bone: StringProperty (name='Pole Target Bone', default='', description='E.g.: target_elbow, target_knee')
    
    
class DATA_PT_GYAZ_SetPoleAngle (Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = 'Setup IK Constraint'
    bl_options = {'DEFAULT_CLOSED'}
    
    #add ui elements here
    def draw (self, context):
        lay = self.layout
        rig = bpy.context.object.data
        scene = bpy.context.scene
        owner = scene.gyaz_set_pole_angle
        row = lay.row (align=True)
        row.prop_search (owner, 'base_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='base_bone'
        row = lay.row (align=True)
        row.prop_search (owner, 'constraint_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='constraint_bone'
        row = lay.row (align=True)
        row.prop_search (owner, 'ik_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='ik_bone'
        row = lay.row (align=True)
        row.prop_search (owner, 'pole_bone', rig, 'bones')
        row.operator (Op_GYAZ_SetupIKConstraint_GetActiveBone.bl_idname, text='', icon='EYEDROPPER').prop_name='pole_bone'
        lay.operator (Op_GYAZ_SetupIKConstraint.bl_idname)
         
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj is not None and (context.mode == 'OBJECT' or context.mode == 'POSE') and context.armature
        

class VIEW3D_PT_GYAZ_OffsetAnimation (Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Offset Animaion'
    bl_category = 'AnimTools'
    
    #add ui elements here
    def draw (self, context):
        scene = bpy.context.scene   
        lay = self.layout
        col = lay.column(align=True)
        col.label(text="Simple Offset:")
        row = col.row(align=True)
        row.operator (Op_GYAZ_OffsetAnim.bl_idname, text = "Global").Mode = 'GLOBAL'
        row.operator (Op_GYAZ_OffsetAnim.bl_idname, text = "Local").Mode = 'SIMPLE_LOCAL'
        col = lay.column(align=True)
        col.label(text="Smooth Offset:")        
        row = col.row(align=True)
        row.operator (Op_GYAZ_OffsetAnim.bl_idname, text = "Local 2").Mode = 'LOCAL_2'
        row.operator (Op_GYAZ_OffsetAnim.bl_idname, text = "Local 4").Mode = 'LOCAL_4'
        col = lay.column(align=True)
        col.label(text="Falloff Curve:")
        row = col.row(align=True)
        row.prop(scene, 'GYAZ_OffsetAnimFalloff', text='')
        if scene.GYAZ_OffsetAnimFalloff != 'LINEAR': 
            row.prop(scene, 'GYAZ_OffsetAnimFalloffStrength_1', text='')
        col = lay.column(align=True)
        col.label(text="Misc:")
        col = col.column(align=True)
        col.operator (Op_GYAZ_AnimSampleFcurves.bl_idname, text = "Sample Fcurves")
        col.operator (Op_GYAZ_DeleteTimelineMarkers.bl_idname, text = "Delete Markers")
        
                
    #when the buttons should show up    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return bpy.context.mode == 'POSE' and obj != None or bpy.context.mode == 'OBJECT' and obj != None
        
    
#######################################################
#######################################################

#REGISTER
#everything should be registeres here

def register():
    
    # props
    Scene.GYAZ_OffsetAnimFalloff = EnumProperty(
        items=(
            ('LINEAR', "Linear", ""),
            ('SMOOTH', "Smooth", ""),
            ('EASE_IN', "Ease In", ""),
            ('EASE_OUT', "Ease Out", "")),
        name = 'Fall Off',
        default = 'SMOOTH',
        description = "Falloff curve used for smooth local offset")
        
    Scene.GYAZ_OffsetAnimFalloffStrength_1 = IntProperty(
        default = 2,
        min = 0,
        name = 'Fall Off Strength 1',
        description = 'Strength of falloff curve. Ignored when Falloff is Linear')
    
    # set pole angle    
    bpy.utils.register_class (PG_GYAZ_SetPoleAngle)
    Scene.gyaz_set_pole_angle = PointerProperty (type=PG_GYAZ_SetPoleAngle)
        
    
    bpy.utils.register_class (Op_GYAZ_OffsetAnim)
    bpy.utils.register_class (Op_GYAZ_AnimSampleFcurves)
    bpy.utils.register_class (Op_GYAZ_DeleteTimelineMarkers)
    bpy.utils.register_class (Op_GYAZ_SetupIKConstraint)
    bpy.utils.register_class (Op_GYAZ_SetupIKConstraint_GetActiveBone)
       
    bpy.utils.register_class (DATA_PT_GYAZ_SetPoleAngle)    
    bpy.utils.register_class (VIEW3D_PT_GYAZ_OffsetAnimation) 

def unregister ():
    
    
    bpy.utils.unregister_class (Op_GYAZ_OffsetAnim)
    bpy.utils.unregister_class (Op_GYAZ_AnimSampleFcurves)
    bpy.utils.unregister_class (Op_GYAZ_DeleteTimelineMarkers)
    bpy.utils.unregister_class (Op_GYAZ_SetupIKConstraint)
    bpy.utils.unregister_class (Op_GYAZ_SetupIKConstraint_GetActiveBone)
    
    bpy.utils.unregister_class (DATA_PT_GYAZ_SetPoleAngle)
    bpy.utils.unregister_class (VIEW3D_PT_GYAZ_OffsetAnimation)


    # props
    del Scene.GYAZ_OffsetAnimFalloff
    del Scene.GYAZ_OffsetAnimFalloffStrength_1
    
    # set pole angle
    del Scene.gyaz_set_pole_angle     
    bpy.utils.unregister_class (PG_GYAZ_SetPoleAngle)
  
if __name__ == "__main__":   
    register()      