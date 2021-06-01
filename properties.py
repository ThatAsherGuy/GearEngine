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
    ('A', "A", "Sun input, carrier output, fixed ring"),
    ('B', "B", "Ring Input, Carrier Output, Fixed Sun"),
    ('C', "C", "Sun Input, Ring Output, Fixed Carrier"),
]

def calc_spur_ratio(drive_gear, target_gear, mode):
    if (drive_gear.teeth == 0) or (target_gear.teeth == 0):
        return -1.0
    else:
        return drive_gear.teeth/target_gear.teeth


def calc_planetary_ratio(sun, ring, mode):
    if (sun.teeth == 0) or (ring.teeth == 0):
        return -1.0

    if mode == 'A': # Sun Input, Carrier Output, Fixed Ring
        return sun.teeth / (sun.teeth + ring.teeth)

    elif mode == 'B': # Ring Input, Carrier Output, Fixed Sun
        return 1 + (sun.teeth/ring.teeth)

    elif mode == 'C': # Sun Input, Ring Output, Fixed Carrier
        return -(ring.teeth/sun.teeth)

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

    axis: IntProperty(
        name="Rotation Axis",
        default=2,
        min=0,
        max=2
    )

    space: IntProperty(
        name="Transform Space",
        default=0
    )

    drive_object: PointerProperty(
        type=bpy.types.Object,
        name="Drive Object",
    )

    drive_gear: StringProperty(
        name="Drive Gear",
        default=""
    )

    def set_drive_index(self, val):
        self["drive_gear_index"] = val
        self.parent_obj.gear_data.driven_gear_index 

    drive_gear_index: IntProperty(
        name="Drive Gear",
        default=0,
        min=0
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
        if (self.gear_type == 'PLANETARY') and (self.planetary_subtype == 'PLANET'):
            ratio_func = ratio_dict["SPUR"]
        else:
            ratio_func = ratio_dict[self.gear_type]

        if not self.drive_object:
            return 0.0

        if not self.drive_object.gear_data:
            return -1.0

        if len(self.drive_object.gear_data.gears) > self.drive_gear_index: 
            drive_gear = self.drive_object.gear_data.gears[self.drive_gear_index]

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
    speed: FloatProperty(
        name="Speed",
        default=1.0,
        soft_min=-50.0,
        soft_max=50.0
    )

    enabled: BoolProperty(
        name="Enabled",
        default=False
    )

class GearSet(PropertyGroup):

    gears: CollectionProperty(
        type=GearProps,
        name="Gears",
    )

    driven_gear_index: IntProperty(
        name="Drive Index",
        default=-1
    )

    system: StringProperty(
        name="Gear System",
        default=""
    )

    motor: PointerProperty(
        type=MotorProps,
        name="Motor Properties"
    )
