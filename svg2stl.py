''' 
shapr3d 不能直接编辑导入的 stl  。不能编辑网格实体
'''
import xml.etree.ElementTree as ET
import numpy as np
from stl import mesh

def svg_to_stl(input_svg_path, output_stl_path, stl_thickness=10):
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Remove namespace prefixes if any (from previous step)
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

    path_element = root.find('path')
    if path_element is None:
        print("Error: No path element found in SVG.")
        return

    path_data = path_element.get('d')

    # Parse path data into points
    # Assuming path data is in "M x,y L x,y L x,y ... Z" format
    points_str = path_data.replace('M', '').replace('Z', '').strip()
    points_str_list = points_str.split(' L')
    
    contour_points = []
    for p_str in points_str_list:
        coords = p_str.split(',')
        contour_points.append((float(coords[0]), float(coords[1])))
    
    contour_points = np.array(contour_points) # Convert to numpy array

    # --- STL Export (reusing logic from p2stl.py) ---
    vertices_bottom = np.hstack([contour_points, np.zeros((len(contour_points), 1))])
    vertices_top = np.hstack([contour_points, np.full((len(contour_points), 1), stl_thickness)])
    vertices = np.vstack([vertices_bottom, vertices_top])
    num_points = len(contour_points)
    
    faces = []
    # Side faces
    for i in range(num_points):
        p1 = i
        p2 = (i + 1) % num_points
        p3 = i + num_points
        p4 = (i + 1) % num_points + num_points
        faces.append([p1, p2, p4])
        faces.append([p1, p4, p3])

    # Bottom and Top faces (fan triangulation)
    for i in range(1, num_points - 1):
        faces.append([0, i, i + 1])
        faces.append([num_points, num_points + i + 1, num_points + i])

    the_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            the_mesh.vectors[i][j] = vertices[f[j],:]
    
    the_mesh.save(output_stl_path)
    print(f"STL saved to {output_stl_path}")

if __name__ == '__main__':
    input_svg = '/home/qgb/test/p2stl/simple.svg'
    output_stl = '/home/qgb/test/p2stl/simple.stl'
    svg_to_stl(input_svg, output_stl)
