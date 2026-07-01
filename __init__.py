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

# bl_info = { No longer necessary in add-ons for Blender 4.2 and newer
#     "name": "TTZ Render Exporter",
#     "author": "Alec Chechik",
#     "description": "Saves all render passes at once",
#     "blender": (2, 80, 0),
#     "version": (0, 0, 1),
#     # "location": "Properties > Scene > View Layer"
#     # "warning": "",
#     # "category": "Generic",
# }

import bpy

class OBJECT_OT_save_renders(bpy.types.Operator):
    "Saves renders in a specific file path"
    bl_idname = "object.save_renders"
    bl_label = "Save renders"
    bl_options = {'REGISTER', 'UNDO'} # Allows actions to be undone with Ctrl+Z, may remove if it breaks Blender

    def execute(self, context):
        """The core payload logic loop."""
        # 'context' provides access to current user states like active objects or selected vertices
        self.report({'INFO'}, "Export Initiated Successfully!")
        return {'FINISHED'} # Instructs Blender that the operation completed with no errors

    # def execute(self, context):
    #     return super().execute(context)

class PROPERTIES_PT_render_export_panel(bpy.types.Panel):
    bl_label = "Render Exporter"
    bl_idname = "PROPERTIES_PT_render_panel_view_layer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        view_layer = context.view_layer

        col = layout.column(align=True)
        col.label(text=f"Active Layer: {view_layer.name}")
        col.operator("object.render_export", text="Export Active Layer")

classes = (
    OBJECT_OT_save_renders,
    PROPERTIES_PT_render_export_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)