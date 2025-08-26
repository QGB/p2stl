
import cv2
import numpy as np
from stl import mesh

def process_and_export_contour(image_path, svg_path, stl_path, stl_thickness=10):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    object_mask = cv2.bitwise_not(mask)
    kernel = np.ones((5, 5), np.uint8)
    object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        # --- SVG Export ---
        svg_header = f'<svg width="{image.shape[1]}" height="{image.shape[0]}" xmlns="http://www.w3.org/2000/svg">'
        svg_path_data = "M" + " L".join([f"{p[0][0]},{p[0][1]}" for p in largest_contour]) + " Z"
        svg_element = f'<path d="{svg_path_data}" fill="none" stroke="red" stroke-width="2"/>'
        svg_footer = '</svg>'
        with open(svg_path, 'w') as f:
            f.write(svg_header + svg_element + svg_footer)
        print(f"Contour saved to {svg_path}")

        # --- STL Export ---
        contour_points = largest_contour.reshape(-1, 2)
        
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
        
        the_mesh.save(stl_path)
        print(f"Contour saved to {stl_path}")

    else:
        print("No contours found in the image.")

if __name__ == '__main__':
    input_jpeg_path = '/home/qgb/test/p2stl/v2-c41b37b6beee52d9bb6135b03b7dd662.jpeg'
    output_svg_path = '/home/qgb/test/p2stl/r.svg'
    output_stl_path = '/home/qgb/test/p2stl/r.stl'
    process_and_export_contour(input_jpeg_path, output_svg_path, output_stl_path)
