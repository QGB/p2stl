import cv2
import numpy as np
def process_image_with_green_background(image_path, output_path):
    image = cv2.imread(image_path) # Read the image
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Convert image to HSV color space for better color segmentation
    lower_green = np.array([35, 40, 40]) # Define range for green color in HSV
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green) # Create a mask for the green background
    object_mask = cv2.bitwise_not(mask) # Invert the mask to get the object
    kernel = np.ones((5,5),np.uint8) # Use morphological opening to remove small noise
    object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, kernel, iterations = 2)
    contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Find contours in the object mask
    if contours:
        largest_contour = max(contours, key=cv2.contourArea) # Find the largest contour by area
        result_image = image.copy() # Create a copy of the original image to draw on
        cv2.drawContours(result_image, [largest_contour], -1, (0, 0, 255), 2, cv2.LINE_AA) # Draw the largest contour in red with anti-aliasing
        cv2.imwrite(output_path, result_image) # Save the result
        print(f"Processed image saved to {output_path}")
    else:
        print("No contours found in the image.")
if __name__ == '__main__':
    input_jpeg_path = '/home/qgb/test/p2stl/v2-c41b37b6beee52d9bb6135b03b7dd662.jpeg'
    output_png_path = '/home/qgb/test/p2stl/r.png'
    process_image_with_green_background(input_jpeg_path, output_png_path)