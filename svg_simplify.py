import xml.etree.ElementTree as ET
import numpy as np

def distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def point_line_distance(point, start, end):
    if start == end:
        return distance(point, start)
    
    numerator = abs((end[1] - start[1]) * point[0] - \
                    (end[0] - start[0]) * point[1] + \
                    end[0] * start[1] - end[1] * start[0])
    denominator = distance(start, end)
    return numerator / denominator

def rdp(points, epsilon):
    if len(points) < 3:
        return points

    dmax = 0.0
    index = 0
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        recResults1 = rdp(points[:index+1], epsilon)
        recResults2 = rdp(points[index:], epsilon)
        result = recResults1[:-1] + recResults2
    else:
        result = [points[0], points[-1]]

    return result

def simplify_svg_path(input_svg_path, output_svg_path, epsilon):
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Remove namespace prefixes for easier manipulation and browser compatibility
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1] # Strip off namespace prefix

    path_element = root.find('path') # Now we can find without namespace prefix
    if path_element is None:
        print("Error: No path element found in SVG.")
        return

    path_data = path_element.get('d')

    points_str = path_data.replace('M', '').replace('Z', '').strip()
    points_str_list = points_str.split(' L')
    
    points = []
    for p_str in points_str_list:
        coords = p_str.split(',')
        points.append((float(coords[0]), float(coords[1])))

    simplified_points = rdp(points, epsilon)

    new_path_data = "M" + f"{simplified_points[0][0]},{simplified_points[0][1]}"
    for p in simplified_points[1:]:
        new_path_data += f" L{p[0]},{p[1]}"
    new_path_data += " Z"

    path_element.set('d', new_path_data)

    # Ensure the SVG namespace is correctly set on the root element for output
    root.set('xmlns', 'http://www.w3.org/2000/svg')

    # Write the XML. Use encoding='utf-8' and xml_declaration=True for standard output.
    tree.write(output_svg_path, encoding='utf-8', xml_declaration=True)
    print(f"Simplified SVG saved to {output_svg_path}")

if __name__ == '__main__':
    input_svg = '/home/qgb/test/p2stl/r.svg'
    output_svg = '/home/qgb/test/p2stl/simple.svg'
    epsilon_value = 5.0 # This value might need tuning for desired simplification level
    simplify_svg_path(input_svg, output_svg, epsilon_value)