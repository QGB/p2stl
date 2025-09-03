import sys
import re
try:
    import cadquery as cq
    from lxml import etree
except ImportError:
    print("Error: Required libraries not found. Please install 'cadquery' and 'lxml'.")
    print(f"You can try running: {sys.executable} -m pip install cadquery==2.4.0 lxml")
    sys.exit(1)

def create_step_from_svg(svg_path, step_path):
    """
    Reads an SVG file, extracts the first path found, and converts it into a
    planar face (sheet body) in a STEP file.

    This script assumes the SVG path defines a single, closed, planar polygon.
    """
    try:
        # Parse the SVG file to find the path data string 'd'
        tree = etree.parse(svg_path)
        # Using xpath to find the 'd' attribute of the first path element, ignoring namespaces
        path_data_list = tree.xpath('//*[local-name()="path"]/@d')
        if not path_data_list:
            print(f"Error: No <path> element found in {svg_path}")
            return

        path_data = path_data_list[0]

        # Parse the path data string into a list of (x, y) points
        # This simplified parser handles 'M', 'L', and 'Z' for a single closed polyline.
        path_data = path_data.upper().replace('M', ' ').replace('L', ' ').replace('Z', ' ').strip()
        coords_str = re.split(r'[\s,]+', path_data)
        # Filter out empty strings that may result from splitting
        coords_str = [c for c in coords_str if c]

        if len(coords_str) % 2 != 0:
            print("Error: Path data contains an odd number of coordinates.")
            return

        points = [(float(coords_str[i]), float(coords_str[i+1])) for i in range(0, len(coords_str), 2)]

        if not points:
            print("Error: Could not extract any points from the SVG path.")
            return

        # Create a 2D wire from the points in CadQuery
        wire = cq.Workplane("XY").polyline(points).close()

        # Create a planar face from the wire
        # The wire needs to be a cq.Wire object for makeFromWires
        face = cq.Face.makeFromWires(wire.wires().val())

        # Export the face to a STEP file
        cq.exporters.export(face, step_path)

        print(f"Successfully converted '{svg_path}' to '{step_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Default file paths from user's context
    svg_input_default = "/home/qgb/test/p2stl/simple.svg"
    step_output_default = "/home/qgb/test/p2stl/output.step"

    if len(sys.argv) == 3:
        svg_input = sys.argv[1]
        step_output = sys.argv[2]
        create_step_from_svg(svg_input, step_output)
    elif len(sys.argv) == 1:
        print(f"No arguments provided. Running with default files:")
        print(f"Input: {svg_input_default}")
        print(f"Output: {step_output_default}")
        create_step_from_svg(svg_input_default, step_output_default)
    else:
        print("Usage: python svg2step.py <input_svg_file> <output_step_file>")
        print(f"Or run without arguments to use default files.")
        sys.exit(1)