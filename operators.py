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
import bpy_extras
from bpy.props import (
    BoolProperty, IntProperty,
    FloatVectorProperty,
    EnumProperty
)

class GE_OT_AddGearToSet(bpy.types.Operator):
    """Collection Property Handling"""
    bl_idname = "ge.add_gear_to_set"
    bl_label = "Add Gear to Set"

    def execute(self, context):
        obj = context.view_layer.objects.active
        obj.gear_data.gears.add()

        new_gear = obj.gear_data.gears[-1]
        new_gear.parent_obj = obj

        if 'Gear' in obj.data.keys():
            new_gear.teeth = obj.data["number_of_teeth"]

        return {'FINISHED'}


class GE_OT_RemoveGear(bpy.types.Operator):
    bl_idname = 'ge.remove_gear'
    bl_label = 'Remove Gear'

    index: IntProperty(
        name='Gear Index',
        default=-1
    )

    def execute(self, context):
        if not context.active_object:
            return {'CANCELLED'}

        if len(context.active_object.gear_data.gears) == 0:
            return{'CANCELLED'}

        obj = context.active_object
        obj.gear_data.gears.remove(self.index)
        return {'FINISHED'}


class GE_OT_AddMotor(bpy.types.Operator):
    bl_idname = 'ge.add_motor'
    bl_label = 'Add Motor'

    def execute(self, context):
        if not context.active_object:
            return {'CANCELLED'}

        obj = context.active_object
        fcurve = obj.driver_add('rotation_euler', 2)
        driver = fcurve.driver

        var = driver.variables.new()
        var.name = 'FPS'
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = context.scene
        var.targets[0].data_path = 'render.fps'

        var = driver.variables.new()
        var.name = 'speed'
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = obj
        var.targets[0].data_path = 'gear_data.motor.speed'

        driver.expression = '(frame/FPS) * speed'

        obj.gear_data.motor.enabled = True

        return {'FINISHED'}


class GE_OT_InitDrivers(bpy.types.Operator):
    """Does the initial Driver Wrangling"""
    bl_idname = "ge.init_drivers"
    bl_label = "Initialize Gear Drivers"

    do_all: BoolProperty(
        name="Initialize All",
        description="Only initiializes drivers for the selected objects when false",
        default=False
    )

    def execute(self, context):
        for obj in context.selected_editable_objects:
            if len(obj.gear_data.gears) == 0:
                continue

            main_gear = None
            for gear in obj.gear_data.gears:
                if gear.drive_object:
                    main_gear = gear
                    break

            if not main_gear:
                break

            fcurve = obj.driver_add('rotation_euler', gear.axis)
            driver = fcurve.driver

            var = driver.variables.new()
            var.name = 'ratio'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = obj
            var.targets[0].data_path = 'gear_data.gears[0].drive_ratio'

            var = driver.variables.new()
            var.name = 'flip'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = obj
            var.targets[0].data_path = 'gear_data.gears[0].flip'

            var = driver.variables.new()
            var.name = 'angle'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = main_gear.drive_object
            var.targets[0].data_path = 'rotation_euler[2]'

            driver.expression = '((flip * 2) - 1) * (ratio * angle)'

        return {'FINISHED'}


class GE_OT_ToolTip(bpy.types.Operator):
    """Use this operator to display inline tooltips."""
    bl_idname = "ge.tool_tip"
    bl_label = "Gear Tool Tip"
    bl_description = "If you can read this, something is broken."

    tooltip: bpy.props.StringProperty(default="")

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        return {'CANCELLED'}