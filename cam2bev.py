import os
import cv2
from pathlib import Path
import numpy as np
import json

# Function to resize images
def resize_and_save_images(image_paths, output_dir, scale_factor=0.5):
    """Resizes images permanently and saves them in a new folder."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    resized_paths = []
    for img_path in image_paths:
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Error: Could not load {img_path}. Skipping.")
            continue
        
        # Resize permanently
        resized_img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor)

        # Save to new directory
        filename = os.path.basename(img_path)
        new_path = os.path.join(output_dir, filename)
        cv2.imwrite(new_path, resized_img)
        resized_paths.append(new_path)

        print(f"Saved resized image: {new_path}")

    return resized_paths  # Return new paths to use in BEV processing

# Load saved points from JSON
def load_points(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            print(f"Loading points from {file_path}")
            points_data = json.load(file)
            np_points_data = [np.array(pt, dtype=np.float32) for pt in points_data]
            print(f"Loaded: {np_points_data}")
            return np_points_data
    else:
        print("No saved points found.")
        return None

# Save points to a JSON file
def save_points(file_path, points_data):
    points_data_as_lists = [pt.tolist() for pt in points_data]
    with open(file_path, 'w') as file:
        json.dump(points_data_as_lists, file)
    print(f"Saved points to {file_path}")

# Function to overlay points and save the image
def get_manual_points(image_path, points_data=None):
    """Opens an image, lets the user click 4 points, and overlays them with labels."""
    global selected_points
    selected_points = points_data if points_data else []  # Load existing points or initialize an empty list
    print('-------------')
    print(f"Image: {image_path}")
    img = cv2.imread(image_path)
    img_copy = img.copy()

    if not selected_points:  # If no points are loaded, ask for user input
        cv2.imshow("Click 4 taped corners", img)
        cv2.setMouseCallback("Click 4 taped corners", mouse_callback)
        cv2.waitKey(0)

    # Overlay selected points onto the image
    for i, (x, y) in enumerate(selected_points):
        cv2.circle(img_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(img_copy, f"Point {i+1}", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Save the image with overlaid selected points
    output_img_path = Path(Path(image_path).parent, "overlay_points", Path(image_path).name)
    os.makedirs(output_img_path.parent, exist_ok=True)
    cv2.imwrite(output_img_path, img_copy)
    print(f"Saved image with points: {output_img_path}")

    return np.array(selected_points, dtype=np.float32), output_img_path

# Global variables
selected_points = []

# Callback function for mouse events to select points
def mouse_callback(event, x, y, flags, param):
    """Callback function to capture points on mouse click"""
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_points.append((x, y))
        print(f"Point selected: {x}, {y}")

        if len(selected_points) == 4:
            cv2.destroyAllWindows()

# Main processing
base_path = "./data/raw_images/"
cam_views = ["1L", "2L", "M", "1R", "2R"]
raw_image_paths = [base_path + cam_view + ".jpg" for cam_view in cam_views]

output_dir = "./data/resized_calib_images"
image_paths = resize_and_save_images(raw_image_paths, output_dir, scale_factor=0.25)

# Load points data if available
points_file = "./data/selected_points.json"

src_pts_list = []
output_img_paths = []
# Try to load previously saved points
points_data = load_points(points_file)
if points_data is not None:
    src_pts_list = points_data
else:
    for img_path in image_paths:
        src_pts, output_img_path = get_manual_points(img_path, points_data)
        src_pts_list.append(src_pts)
        output_img_paths.append(output_img_path)
    # Save the points after all images are processed
    save_points(points_file, src_pts_list)

# Step 2: Define the destination (bird's-eye view) coordinates
dst_width, dst_height = 500, 300  # Scale for better visualization
dst_pts = np.float32([
    [0, 0], 
    [dst_width, 0], 
    [dst_width, dst_height], 
    [0, dst_height]
])

# Step 3: Compute homography matrices for all cameras
homographies = []
for src in src_pts_list:
    H, status = cv2.findHomography(src, dst_pts)
    homographies.append(H)
print(f"Homographies: {homographies}")

# Step 4: Warp each image to a bird's-eye view
warped_images = [
    cv2.warpPerspective(cv2.imread(img), H, (dst_width, dst_height))
    for img, H in zip(image_paths, homographies)
]

for i, warped_image in enumerate(warped_images):
    if warped_image is None or warped_image.size == 0:
        print(f"Error: Warped image {i} is empty. Skipping stitching.")
        continue
    # Save the valid warped images
    warped_image_path = f"./data/wraped_images/warped_image_{i}.jpg"
    os.makedirs(os.path.dirname(warped_image_path), exist_ok=True)
    cv2.imwrite(warped_image_path, warped_image)
    print(f"Saved warped image {i} as {warped_image_path}")

stitcher = cv2.Stitcher_create()
status, stitched_image = stitcher.stitch(warped_images)

if status == cv2.Stitcher_OK:
    cv2.imshow("Final Bird's-Eye View", stitched_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("stitched_top_view.jpg", stitched_image)
    print("Stitched image saved successfully!")
else:
    print(f"Error during stitching: {status}")
    if status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Stitching requires more images.")
    elif status == cv2.Stitcher_ERR_HOMOGRAPHY_ESTIMATION_FAILED:
        print("Homography estimation failed. This may happen if the images do not overlap well.")

# Save the final stitched output
cv2.imwrite("stitched_top_view.jpg", stitched_image)
print("Bird's-eye view image saved as 'stitched_top_view.jpg'")
