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

class View3dPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        if context.view_layer.objects.active:
            return True

class GE_PT_MainPanel(View3dPanel, bpy.types.Panel):
    bl_idname = "GE_PT_MainPanel"
    bl_label = "Gear Settings"

    def draw(self, context):
        layout = self.layout
        obj = context.view_layer.objects.active

        root = layout.column(align=True)

        if obj.rotation_mode == 'QUATERNION':
            root.prop(obj, 'delta_rotation_quaternion', index=3, text='Delta Rotation')
        elif not obj.rotation_mode == 'AXIS_ANGLE':
            root.prop(obj, 'delta_rotation_euler', index=2, text='Delta Rotation')

        root.prop(obj, 'show_axis', text="Show Axis")

        op = root.operator(
            "ge.add_gear_to_set",
            text="Add Gear"
        )

        op = root.operator(
            "ge.init_drivers",
            text="Refresh Gear Driver"
        )

        root.separator()

        if obj.gear_data.motor.enabled:
            box = root.box()
            box = box.column(align=True)
            box.use_property_split = True

            box.label(text='Motor Settings')

            box.prop(obj.gear_data.motor, 'enabled')
            box.prop(obj.gear_data.motor, 'speed')

        for i, gear in enumerate(obj.gear_data.gears):
            box = root.box()
            box = box.column(align=True)

            header = box.row(align=True)
            header.label(text="Gear " + str(i))
            op = header.operator(
                "ge.remove_gear",
                text="",
                icon='PANEL_CLOSE'
            )
            op.index = i

            box.use_property_split = True

            box.prop(
                gear,
                "name"
            )

            box.prop(
                gear,
                "teeth"
            )

            box.prop(
                gear,
                "axis"
            )

            box.separator()

            row = box.row(align=True)

            if gear.drive_ratio == -1.0:
                err = row.row(align=True)
                err.alert =True
                err.label(text="", icon='ERROR')

            row.prop(
                gear,
                "drive_object"
            )

            if gear.drive_object:

                box.prop(
                    gear,
                    "drive_gear_index"
                )

                drive_obj_gears = gear.drive_object.gear_data.gears
                if len(drive_obj_gears) > gear.drive_gear_index:
                    box.prop(
                        gear,
                        "drive_ratio"
                    )

                box.prop(
                    gear,
                    "flip",
                    invert_checkbox=True
                )

