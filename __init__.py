# pyright: reportMissingModuleSource=none
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

class PROPERTIES_PT_render_export_panel(bpy.types.Panel):
    bl_label = "Render Exporter"
    bl_idname = "PROPERTIES_PT_render_panel_view_layer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'

    # UI
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        view_layer = context.view_layer
        
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.

        rd = context.scene.render
        col = layout.column()
        # image_settings = rd.image_settings

        # 1. Add file name text entry
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(view_layer, "input_scene_name", text="Scene Name", icon='FONT_DATA')

        # 2. File explorer tab; need to see how to actually use this directory; is it tied to the render tab I copied it from?
        col.use_property_split = True
        col.prop(rd, "filepath", text="Save Path")
  
        # 2.b (optional) Add passes preset select

        # 3. Add Render and save button
        col.operator("object.save_renders", icon='RENDER_STILL')

class OBJECT_OT_save_renders(bpy.types.Operator):
    "Saves renders in a specific file path"
    bl_idname = "object.save_renders"
    bl_label = "Render Passes"
    bl_options = {'REGISTER', 'UNDO'} # Allows actions to be undone with Ctrl+Z, may remove if it breaks Blender

    def execute(self, context):
        return {'FINISHED'}

classes = (
    OBJECT_OT_save_renders,
    PROPERTIES_PT_render_export_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.ViewLayer.input_scene_name = bpy.props.StringProperty(
        name="Scene Name",
        description="The custom prefix string applied to render files",
        default="Scene_Name"
        )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)