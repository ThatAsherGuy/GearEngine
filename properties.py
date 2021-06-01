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
        name="Trnasform Space",
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
        default=True,
    )

    def get_ratio(self):
        do_flip = False
        if not self.drive_object.gear_data:
            return 0.0

        if len(self.drive_object.gear_data.gears) > self.drive_gear_index:
            drive_gear = self.drive_object.gear_data.gears[self.drive_gear_index]
            if do_flip:
                return ((self.flip * 2) - 1) * (drive_gear.teeth/self.teeth)
            else:
                return drive_gear.teeth/self.teeth
        else:
            return 0.0

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
