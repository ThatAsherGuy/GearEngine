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

        op = root.operator(
            "ge.add_gear_to_set",
            text="Add Gear"
        )

        row = root.row(align=True)
        row.prop(obj.gear_data, "drive_mode", text="")
        op = row.operator(
            "ge.init_drivers",
            text="",
            icon='FILE_REFRESH'
        )

        root.separator()

        col = root.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        # if obj.rotation_mode == 'QUATERNION':
        #     col.prop(obj, 'delta_rotation_quaternion', index=3, text='Delta Rotation')
        # elif not obj.rotation_mode == 'AXIS_ANGLE':
        #     col.prop(obj, 'delta_rotation_euler', index=2, text='Delta Rotation')

        # col.prop(obj, 'show_axis', text="Show Axis")
        row = col.row(align=True)
        row.prop(obj.gear_data, "driver_type", expand=True)

        if obj.gear_data.driver_type == 'OBJ':
            col.prop(obj.gear_data, "drive_object")
            col.prop(obj.gear_data, "drive_gear")
            col.prop(obj.gear_data, "driven_gear")
        else:
            col.prop(obj.gear_data.motor, 'speed')
            row = col.row(align=True)
            row.prop(obj.gear_data.motor, 'axis', expand=True)


        col.separator()

        root.label(text="Gear Rings:")

        for i, gear in enumerate(obj.gear_data.gears):
            box = root.box()
            box = box.column(align=True)
            box.use_property_decorate = False
            box.use_property_split = True

            header = box.row(align=True)
            header.label(text="Ring " + str(i))
            op = header.operator(
                "ge.remove_gear",
                text="",
                icon='PANEL_CLOSE'
            )
            op.index = i

            box.prop(gear, "name")
            if gear.gear_type == 'WORM':
                box.prop(gear, "teeth", text='Threads')
            else:
                box.prop(gear, "teeth")
            row = box.row(align=True)
            row.prop(gear, "axis", expand=True)
            box.separator()

            if obj.gear_data.drive_object:

                row = box.row(align=True)
                row.prop(gear, "gear_type")

                if gear.gear_type == 'PLANETARY':
                    row.prop(gear, "planetary_subtype", text="")

                    if gear.planetary_subtype == 'PLANET':
                        tip = row.operator("ge.tool_tip", text="", icon='INFO')
                        tip.tooltip = "Drive this with a gear on the carrier"

                    if not gear.planetary_subtype == 'PLANET':
                        row = box.row(align=True)
                        row.prop(
                            gear,
                            "gear_mode",
                            text="Drive Mode",
                            expand=True
                        )


            row = box.row(align=True)
            row.prop(gear, "drive_ratio")

            if gear.drive_ratio == -1.0:
                err = row.row(align=True)
                err.alert =True
                err.emboss = 'NONE'
                # err.label(text="", icon='ERROR')
                tip = err.operator("ge.tool_tip", text="", icon='ERROR')
                tip.tooltip = gear.ratio_err

            box.prop(
                gear,
                "flip",
                invert_checkbox=True
            )


class GE_PT_MotorPanel(View3dPanel, bpy.types.Panel):
    bl_idname = "GE_PT_MotorPanel"
    bl_label = "Gear Motor"
    bl_parent_id = "GE_PT_MainPanel"

    def draw_header(self, context):
        layout = self.layout
        obj = context.view_layer.objects.active
        root = layout.row(align=True)
        root.prop(obj.gear_data.motor, 'enabled', text="")


    def draw(self, context):
        layout = self.layout
        obj = context.view_layer.objects.active

        root = layout.column(align=True)
        root.use_property_split = True
        root.use_property_decorate = False
        root.prop(obj.gear_data.motor, 'speed')

        row = root.row(align=True)
        row.prop(obj.gear_data.motor, 'axis', expand=True)


class GE_PT_HelpPanel(View3dPanel, bpy.types.Panel):
    bl_idname = "GE_PT_HelpPanel"
    bl_label = "Gear Info"
    bl_parent_id = "GE_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.view_layer.objects.active

        root = layout.column(align=True)
        root.scale_y = 0.75
        root.use_property_split = True
        root.use_property_decorate = False

        section_flags = [False, False, False]

        if hasattr(obj, 'gear_data'):
            for ring in obj.gear_data.gears:
                if ring.gear_type == 'SPUR':
                    section_flags[0] = True
                elif ring.gear_type == 'PLANETARY':
                    section_flags[1] = True
                elif ring.gear_type == 'WORM':
                    section_flags[2] = True

        if section_flags[0]:
            root.label(text="Your standard spur gear.")
            root.label(text="Parent it to an empty for better axis control.")
        elif section_flags[1]:
            root.label(text="How To Planetary Gear:")
            root.label(text="If the carrier spins, drive the planets with it.")
            root.label(text="Otherwise, drive them with the ring.")
            root.label(text="Use the ring's tooth count for the drive gear.")
        elif section_flags[2]:
            root.label(text="How to Worm Gear:")
            root.label(text="For worms, Tooth Count == Number of Threads.")

        
