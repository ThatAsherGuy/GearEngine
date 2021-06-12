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
from bpy.props import PointerProperty

from . properties import GearProps
from . properties import GearSet
from . properties import MotorProps

from . operators import GE_OT_AddGearToSet
from . operators import GE_OT_RemoveGear
from . operators import GE_OT_AddMotor
from . operators import GE_OT_InitDrivers
from . operators import GE_OT_InitConstraint
from . operators import GE_OT_ToolTip

from . interface import GE_PT_MainPanel
from . interface import GE_PT_MotorPanel
from . interface import GE_PT_HelpPanel

bl_info = {
    "name" : "GearEngine",
    "author" : "ThatAsherGuy",
    "description" : "",
    "blender" : (2, 90, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

classes = [
    # Props
    GearProps,
    MotorProps,
    GearSet,
    # Ops
    GE_OT_AddGearToSet,
    GE_OT_RemoveGear,
    GE_OT_InitDrivers,
    GE_OT_InitConstraint,
    GE_OT_AddMotor,
    GE_OT_ToolTip,
    # UI
    GE_PT_MainPanel,
    GE_PT_MotorPanel,
    GE_PT_HelpPanel,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.gear_data = PointerProperty(type=GearSet)


def unregister():
    del bpy.types.Object.gear_data

    for cls in classes:
        bpy.utils.unregister_class(cls)
