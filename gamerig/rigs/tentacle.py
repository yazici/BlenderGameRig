import bpy
from rna_prop_ui import rna_idprop_ui_prop_get
from ..utils import (
    copy_bone, put_bone,
    org, basename, connected_children_names,
    create_widget, create_sphere_widget, create_circle_widget,
    MetarigError
)


class Rig:

    def __init__(self, obj, bone_name, params):
        self.obj = obj
        self.org_bones = [bone_name] + connected_children_names(obj, bone_name)
        self.params = params

        self.copy_rotaion_axes = params.copy_rotaion_axes

        if len(self.org_bones) <= 1:
            raise MetarigError(
                "GAMERIG ERROR: invalid rig structure" % basename(bone_name)
            )


    def make_controls( self ):

        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones

        ctrl_chain = []
        for i in range( len( org_bones ) ):
            name = org_bones[i]

            ctrl_bone  = copy_bone(
                self.obj,
                name,
                basename(name)
            )

            ctrl_chain.append( ctrl_bone )

        # Make widgets
        bpy.ops.object.mode_set(mode ='OBJECT')

        for ctrl in ctrl_chain:
            create_circle_widget(self.obj, ctrl, radius=0.3, head_tail=0.5)

        return ctrl_chain


    def parent_bones( self, all_bones ):

        bpy.ops.object.mode_set(mode ='EDIT')
        org_bones = self.org_bones
        eb        = self.obj.data.edit_bones

        # Parent control bones
        for bone in all_bones['control'][1:]:
            previous_index    = all_bones['control'].index( bone ) - 1
            eb[ bone ].parent = eb[ all_bones['control'][previous_index] ]


    def make_constraints( self, all_bones ):

        bpy.ops.object.mode_set(mode ='OBJECT')
        org_bones = self.org_bones
        pb        = self.obj.pose.bones

        # org bones' constraints
        ctrls = all_bones['control']

        for org, ctrl in zip( org_bones, ctrls ):
            con           = pb[org].constraints.new('COPY_TRANSFORMS')
            con.target    = self.obj
            con.subtarget = ctrl

            # Control bones' constraints
            if ctrl != ctrls[0]:
                con = pb[ctrl].constraints.new('COPY_ROTATION')
                con.target       = self.obj
                con.subtarget    = ctrls[ ctrls.index(ctrl) - 1 ]
                for i, prop in enumerate( [ 'use_x', 'use_y', 'use_z' ] ):
                    if self.copy_rotaion_axes[i]:
                        setattr( con, prop, True )
                    else:
                        setattr( con, prop, False )
                con.use_offset   = True
                con.target_space = 'LOCAL'
                con.owner_space  = 'LOCAL'



    def generate(self):
        bpy.ops.object.mode_set(mode ='EDIT')
        eb = self.obj.data.edit_bones

        # Clear all initial parenting
        for bone in self.org_bones:
            # eb[ bone ].parent      = None
            eb[ bone ].use_connect = False

        # Creating all bones
        ctrl_chain  = self.make_controls()

        all_bones = {
            'control' : ctrl_chain,
        }

        self.make_constraints( all_bones )
        self.parent_bones( all_bones )


def add_parameters(params):
    """ Add the parameters of this rig type to the
        GameRigParameters PropertyGroup
    """
    params.copy_rotaion_axes = bpy.props.BoolVectorProperty(
        size        = 3,
        description = "Layers for the tweak controls to be on",
        default     = tuple( [ i == 0 for i in range(0, 3) ] )
        )


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """

    r = layout.row()
    col = r.column(align=True)
    row = col.row(align=True)
    for i,axis in enumerate( [ 'x', 'y', 'z' ] ):
        row.prop(params, "copy_rotaion_axes", index=i, toggle=True, text=axis)


def create_sample(obj):
    # generated by gamerig.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('Bone')
    bone.head[:] = 0.0000, 0.0000, 0.0000
    bone.tail[:] = 0.0000, 0.0000, 0.3333
    bone.roll = 0.0000
    bone.use_connect = False
    bones['Bone'] = bone.name

    bone = arm.edit_bones.new('Bone.002')
    bone.head[:] = 0.0000, 0.0000, 0.3333
    bone.tail[:] = 0.0000, 0.0000, 0.6667
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['Bone']]
    bones['Bone.002'] = bone.name

    bone = arm.edit_bones.new('Bone.001')
    bone.head[:] = 0.0000, 0.0000, 0.6667
    bone.tail[:] = 0.0000, 0.0000, 1.0000
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['Bone.002']]
    bones['Bone.001'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['Bone']]
    pbone.gamerig_type = 'gamerig.tentacle'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['Bone.002']]
    pbone.gamerig_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['Bone.001']]
    pbone.gamerig_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in arm.edit_bones:
        bone.select = False
        bone.select_head = False
        bone.select_tail = False
    for b in bones:
        bone = arm.edit_bones[bones[b]]
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        arm.edit_bones.active = bone
