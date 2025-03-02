import numpy as np
import trimesh
import cv2

class MeshGenerator:
    def generate(self, contours, depth_map, colors):
        height, width = depth_map.shape
        
        # Create vertex grid
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        vertices = np.stack([x, y, depth_map * 10], axis=-1)  # Scale depth for better visibility
        vertices = vertices.reshape(-1, 3)
        
        # Create faces (triangles)
        faces = []
        for i in range(height - 1):
            for j in range(width - 1):
                v0 = i * width + j
                v1 = v0 + 1
                v2 = (i + 1) * width + j
                v3 = v2 + 1
                
                # Create two triangles for each quad
                faces.append([v0, v1, v2])
                faces.append([v1, v3, v2])
        
        faces = np.array(faces)
        
        # Create mesh
        mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            process=True
        )
        
        # Smooth mesh
        mesh = mesh.smoothed()
        
        # Apply vertex colors
        vertex_colors = self._compute_vertex_colors(depth_map, colors)
        mesh.visual.vertex_colors = vertex_colors
        
        # Export as GLB
        output_path = "temp/output.glb"
        mesh.export(output_path)
        
        return output_path
    
    def _compute_vertex_colors(self, depth_map, colors):
        # Create a simple color gradient based on depth
        height, width = depth_map.shape
        vertex_colors = np.zeros((height * width, 4), dtype=np.uint8)
        
        # Convert depth to colors
        normalized_depth = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
        color_map = cv2.applyColorMap((normalized_depth * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
        
        # Reshape color map to match vertex array
        vertex_colors[:, :3] = color_map.reshape(-1, 3)
        vertex_colors[:, 3] = 255  # Alpha channel
        
        return vertex_colors 