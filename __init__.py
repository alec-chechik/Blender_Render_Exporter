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
        # 'context' provides access to current user states like active objects or selected vertices
        view_layer = context.view_layer
        scene = context.scene

        # Grab the value currently typed into the text box
        prefix = view_layer.input_scene_name

        # Safety fallback: If the user left it blank, assign a default string
        if not prefix.strip():
            prefix = "Render"
            
        self.report({'INFO'}, f"Using prefix variable: '{prefix}'")

        # Access the Compositor
        node_tree = context.scene.compositing_node_group
        if not node_tree:
            self.report({'INFO'}, "No compositor active. Creating a new node group...")
            # Create a completely fresh tree if the user hasn't turned on compositing yet
            node_tree = bpy.data.node_groups.new("Addon_Compositor", "CompositorNodeTree")
            scene.compositing_node_group = node_tree
            
        nodes = node_tree.nodes

        # 3. Find an existing File Output node, or generate a fresh one
        output_node = None
        for node in nodes:
            if node.type == 'OUTPUT_FILE':
                output_node = node
                break
                
        if not output_node:
            self.report({'INFO'}, "Creating a new File Output Node...")
            # Instantly spawn the node via the layout tracking engine
            output_node = nodes.new(type="CompositorNodeOutputFile")
            # Shift its location coordinates so it doesn't stack awkwardly at (0,0)
            output_node.location = (400, 200) #Might need to change size, it's quite small RN
            
        # 4. Set the global destination folder directory for this node
        output_node.directory = "C:\\RenderOutput\\" # You can change this to a dynamic path

        # 5. Apply the custom prefix string variable to the modern file items
        # Clear out any dummy default file items if it's a brand new node
        if len(output_node.file_output_items) == 1 and output_node.file_output_items[0].name == "Image":
            output_node.file_output_items.new('RGBA', f"{prefix}_Combined")
        else:
            # If the user already had multi-pass slots configured, batch update them
            for item in output_node.file_output_items:
                # Ensure we don't infinitely stack prefixes if they click multiple times
                if not item.name.startswith(prefix):
                    item.name = f"{prefix}_{item.name}"

        # 6. (Optional Workflow) Automatically connect Render Layers node to your new output node
        rlayers_node = None
        for node in nodes:
            if node.type == 'R_LAYERS':
                rlayers_node = node
                break
                
        if rlayers_node and output_node:
            # Safely create a link between the Render 'Image' socket and your File Output node
            node_tree.links.new(rlayers_node.outputs['Image'], output_node.inputs[0])

        self.report({'INFO'}, f"Configured File Output node with prefix: '{prefix}'")
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