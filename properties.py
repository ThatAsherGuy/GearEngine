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

# Hell is other people's code.

import bpy
from bpy.types import PropertyGroup
from mathutils import Matrix
from bpy.props import (
    CollectionProperty,
    EnumProperty,
    FloatVectorProperty,
    BoolProperty,
    BoolVectorProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty,
    PointerProperty,
    FloatProperty,
)

rot_axes = [
    ('X', "X", ""),
    ('Y', "Y", ""),
    ('Z', "Z", "")
]

gear_types = [
    ("SPUR", "Spur Gear", "Your standard round gear with teeth on it"),
    ("PLANETARY", "Planetary Gear", "Not really a gear, but the math is different"),
    ("WORM", "Worm Gear", "Looks like a screw")
]

planetary_subtypes = [
    ("SUN", "Sun", ""),
    ("PLANET", "Planet", ""),
    ("RING", "Ring", ""),
    ("CARRIER", "Carrier", "")
]

planetary_drive_modes = [
    ('A', "A", "Sun Input, Fixed Carrier, Ring Output"),
    ('B', "B", "Ring Input, Fixed Carrier, Sun Output"),
    ('C', "C", "Carrier Input, Fixed Sun, Ring Output"),
    ('D', "D", "Ring Input, Fixed Sun, Carrier Output"),
    ('E', "E", "Sun Input, Fixed Ring, Carrier Output"),
    ('F', "F", "Carrier Input, Fixed Ring, Sun Output"),

]

def calc_spur_ratio(drive_gear, target_gear, mode):
    if (drive_gear.teeth == 0) or (target_gear.teeth == 0):
        return -1.0
    else:
        return drive_gear.teeth/target_gear.teeth

# a = Ring/Sun
def calc_planetary_ratio(sun, ring, mode):
    if (sun.teeth == 0) or (ring.teeth == 0):
        return -1.0

    a = ring.teeth/sun.teeth

    if mode == 'A': # SCR | -a
        return -a

    elif mode == 'B': # RCS | -1/a
        return -1/a

    elif mode == 'C': # CSR | a/(1 + a)
        return a / (1 + a)

    elif mode == 'D': # RSC | (1 + a)/a
        return (1 + a)/a

    elif mode == 'E': # SRC | (1 + a)
        return 1 + a

    elif mode == 'F': # CRS | 1 * (1 + a)
        return 1 * (1 + a)

    else:
        return -1.0


def calc_worm_ratio(worm, spur, mode):
    if (worm.teeth == 0) or (spur.teeth == 0):
        return -1.0

    return worm.teeth/spur.teeth # worm.teeth being the number of thread starts


ratio_dict = {
    "SPUR": calc_spur_ratio,
    "PLANETARY": calc_planetary_ratio,
    "WORM": calc_worm_ratio,
}


class GearProps(PropertyGroup):
    name: StringProperty(
        name="Gear Name",
        default="Jimmothy"
    )

    teeth: IntProperty(
        name="Teeth",
        default=24,
        min=0,
        options={'PROPORTIONAL'}
    )

    axis: EnumProperty(
        items=rot_axes,
        name="Rotation Axis",
        default='Z'
    )

    drive_object: PointerProperty(
        type=bpy.types.Object,
        name="Drive Object",
    )

    flip: BoolProperty(
        name="Flip Direction",
        default=False,
    )

    gear_type: EnumProperty(
        items=gear_types,
        name="Gear Type",
        description="Determines how the gear ratio is calculated",
        default='SPUR'
    )

    gear_mode: EnumProperty(
        items=planetary_drive_modes,
        name="Planetary Drive Mode",
        default='A'
    )
 
    planetary_subtype: EnumProperty(
        items=planetary_subtypes,
        name="Planetary Subtype",
        description="What role this gear plays in a planetary assemblage"
    )

    def get_ratio(self):
        parent = self.id_data

        if (self.gear_type == 'PLANETARY') and (self.planetary_subtype == 'PLANET'):
            ratio_func = ratio_dict["SPUR"]
        else:
            ratio_func = ratio_dict[self.gear_type]
        
        if hasattr(parent, 'gear_data'):
            if not parent.gear_data.drive_object:
                return 0.0

            if parent.gear_data.drive_gear == -1:
                return -1.0

            drive_obj = parent.gear_data.drive_object

            if len(drive_obj.gear_data.gears) > parent.gear_data.drive_gear:
                drive_gear = drive_obj.gear_data.gears[parent.gear_data.drive_gear]
                return ratio_func(drive_gear, self, self.gear_mode)
            else:
                return -1.0

    drive_ratio: FloatProperty(
        name="Drive Ratio",
        get=get_ratio
    )

    parent_obj: PointerProperty(
        type=bpy.types.Object,
        name="Parent Object"
    )


class MotorProps(PropertyGroup):
    show_motor = False

    speed: FloatProperty(
        name="Speed",
        default=1.0,
        soft_min=-50.0,
        soft_max=50.0
    )

    axis: EnumProperty(
        items=rot_axes,
        name="Axis"
    )

    enabled: BoolProperty(
        name="Enabled",
        description="Whether the motor is enabled",
        default=False,
    )


class GearSet(PropertyGroup):

    gears: CollectionProperty(
        type=GearProps,
        name="Gears",
    )

    motor: PointerProperty(
        type=MotorProps,
        name="Motor Properties"
    )

    def get_fps(self):
        return bpy.context.scene.render.fps

    fps: FloatProperty(
        name="Framerate",
        get=get_fps
    )

    # DRIVE info

    drive_mode_items = [
        ('DRIVER', "Driver-based",
            ("In this mode, the gear is driven by a driver. "
             "It's easy to work with for quick setups, "
             "but you might need to get tricky with parenting and "
             "axis-orders in order to make it work in local space")),

        ('CONSTRAINT', "Constraint-based",
            ("In this mode, the gear is driven by a constraint. "
             "This makes it easy to setup gears that rotate on weird axes "
             "but it can be harder to hand-tweak, since the final transform isn't visible")) 
    ]

    drive_mode: EnumProperty(
        items=drive_mode_items,
        name="Drive Mode",
        description="Controls whether the gear's movement is powered by drivers or constraints",
        options=set(),
        default='DRIVER'
    )

    drive_object: PointerProperty(
        type=bpy.types.Object,
        name="Drive Object",
    )

    drive_gear: IntProperty(
        name="Input Ring",
        description="The index of the gear ring on the drive object that rotates this object",
        default=-1,
        min=-1
    )

    driven_gear: IntProperty(
        name="Output Ring",
        description="The index of the gear ring on this object that engages with the drive object",
        default=-1,
        min=-1
    )

