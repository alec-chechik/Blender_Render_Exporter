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
import os # used for manipulating file directory data.

# UI panel
class PROPERTIES_PT_render_export_panel(bpy.types.Panel):
    bl_label = "Render Exporter"
    bl_idname = "PROPERTIES_PT_render_panel_view_layer" # Will show up in the View Layer property in the rightside tab.
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'

    # Visual UI elements.
    def draw(self, context): # context provides access to current user states like active scene, objects, or selected vertices.
        layout = self.layout
        view_layer = context.view_layer # Accesses view_layer properties panel.
        
        layout.use_property_split = False
        layout.use_property_decorate = False  # Disables animating layout parameters.

        rd = context.scene.render # Accesses render as a variable.
        col = layout.column()

        # UI 1. Add file name text entry.
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(view_layer, "input_scene_name", text="Scene Name")

        # UI 2. File explorer tab to set save directory.
        col.use_property_split = True
        col.prop(rd, "filepath", text="Save Path")
  
        # UI 2.b Passes preset selection. (optional, may be added in the future) 

        # UI 3. Render and save button.
        col.operator("object.save_renders", icon='RENDER_STILL')

# Main operator that renders scene with selected passes and saves them all at once with appropriate names & formatting.
class OBJECT_OT_save_renders(bpy.types.Operator):
    "Saves renders in a specific file path"
    bl_idname = "object.save_renders"
    bl_label = "Render Passes"
    bl_options = {'REGISTER', 'UNDO'} # Allows actions to be undone with Ctrl+Z, may remove if it breaks Blender

    def execute(self, context):
        view_layer = context.view_layer
        scene = context.scene

        # Grab the values currently typed into the text boxes.
        prefix = view_layer.input_scene_name
        saveDirectory = context.scene.render.filepath
            
        self.report({'INFO'}, f"Using prefix variable: '{prefix}'")

        # Access the Compositor, which will be used to configure renders and their file paths.
        node_tree = context.scene.compositing_node_group

        # Create a new node tree if there is no existing one.
        if not node_tree:
            self.report({'INFO'}, "No compositor active. Creating a new node group...")
            node_tree = bpy.data.node_groups.new("Addon_Compositor", "CompositorNodeTree")
            scene.compositing_node_group = node_tree
            
        nodes = node_tree.nodes

        # Find an existing File Output node, or generate a fresh one.
        output_node = None
        for node in nodes:
            if node.type == 'OUTPUT_FILE':
                output_node = node
                break
        
        # Create output and render layers node.
        if not output_node:
            self.report({'INFO'}, "Creating a new File Output Node...")
            output_node = nodes.new(type="CompositorNodeOutputFile")
            output_node.location = (500, 200)
            output_node.format.media_type = 'IMAGE'

            render_layers = node_tree.nodes.new(type='CompositorNodeRLayers')
            render_layers.location = (0, 200)

        render_layers = nodes['Render Layers']
            
        # Set user selected folder as the file output directory.
        output_node.directory = saveDirectory
        output_node.file_name = f'{prefix}_'

        # Clear existing file output node sockets.
        output_node.file_output_items.clear()

        # Configure compositor by using a table of possible layer passes with their appropriate save settings.
        # Format: ('ViewLayer Attribute', 'Output Node Socket Type', 'Bit Depth', 'Output Node Label', 'File Save Suffix', 'Needs Alpha').
        pass_settings = [
            ('use_pass_combined', 'RGBA', '8', 'Combined', 'Image', True),
            ('use_pass_normal', 'RGBA', '16', 'Normal', 'Normal', False),   
            ('use_pass_diffuse_direct', 'FLOAT', '16', 'Diffuse', 'Diffuse Direct', False),
            ('use_pass_diffuse_color', 'RGBA', '8', 'Albedo', 'Diffuse Color', True),
            ('use_pass_glossy_direct', 'FLOAT', '16', 'Glossy', 'Glossy Direct', False),
            ('use_pass_glossy_color', 'RGBA', '8', 'GlossyColor', 'Glossy Color', False),
            ('use_pass_emit', 'FLOAT', '16', 'Emissive', 'Emission', False),
        ]
        
        # Loop through the table
        current_slot = 0
        for attr, socket_type, bit_depth, out_name, socket_name, needs_alpha in pass_settings:
            
            # Check what render passes from the list are selected; If it isn't found, returns False. 
            if getattr(view_layer, attr, False): # This false isn't attr = False, but a safety fallback in case the attribute isn't found.
                
                # Create the slot and save it to a variable.
                item = output_node.file_output_items.new(socket_type, out_name)
                item.override_node_format = True # Allows each pass to have its render settings by overriding the node settings.
                item.format.color_depth = bit_depth
                
                if needs_alpha:
                    unique_node_name = f"Alpha_{out_name}"
                    # Look for alpha node with exact same name in case it doesn't need to be created.
                    alpha_node = nodes.get(unique_node_name)

                    if not alpha_node:
                        alpha_node = nodes.new(type="CompositorNodeSetAlpha")
                        alpha_node.name = unique_node_name
                        alpha_node.label = unique_node_name # Name and label the node to ensure there isn't one already for that particular render pass.
                        alpha_node.location = (300, 250 - (current_slot * 100))

                    # Create node connections.
                    node_tree.links.new(render_layers.outputs[socket_name], alpha_node.inputs['Image'])
                    node_tree.links.new(render_layers.outputs['Alpha'], alpha_node.inputs['Alpha'])
                    node_tree.links.new(alpha_node.outputs['Image'], output_node.inputs[current_slot])
                else:
                    node_tree.links.new(render_layers.outputs[socket_name], output_node.inputs[current_slot])
                
                current_slot += 1

        self.report({'INFO'}, f"Configured File Output node with prefix: '{prefix}_'")
        
        # Ensure render uses the compositing tree.
        context.scene.render.use_compositing = True
        # Disable dithering for 8 bit images to save on file size.
        context.scene.render.dither_intensity = 0.0
        
        # Trigger the render and save it to the output node directory.
        bpy.ops.render.render('INVOKE_DEFAULT') # 'INVOKE_DEFAULT' opens the render window.

        self.report({'INFO'}, f"Rendering and saving to: {saveDirectory}")
        return {'FINISHED'}

classes = (
    OBJECT_OT_save_renders,
    PROPERTIES_PT_render_export_panel,
)

# Upon loading the add-on, register every class in the list.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Scene Name variable, description appears if you hover over its entry box.
    bpy.types.ViewLayer.input_scene_name = bpy.props.StringProperty(
        name="Scene Name",
        description="The prefix applied to render files. Will be followed by an underscore and the selected render pass.",
        default="Scene_Name"
        )

# Unregister classes upon disabling add-on.
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)