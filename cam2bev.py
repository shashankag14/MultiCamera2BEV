import os
import cv2
from pathlib import Path
import numpy as np

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

# Global variables
selected_points = []

def mouse_callback(event, x, y, flags, param):
    """Callback function to capture points on mouse click"""
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_points.append((x, y))
        print(f"Point selected: {x}, {y}")

        if len(selected_points) == 4:
            cv2.destroyAllWindows()

def get_manual_points(image_path):
    """Opens an image, lets the user click 4 points, and overlays them with labels"""
    global selected_points
    selected_points = []
    print('-------------')
    print(f"Image: {image_path}")
    img = cv2.imread(image_path)
    # a copy to overlay points without modifying original image
    img_copy = img.copy()

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

# Define image paths for the 5 cameras
base_path = "./data/raw_images/"
cam_views = ["1L", "2L", "M", "1R", "2R"]
raw_image_paths = [base_path + cam_view + ".jpg" for cam_view in cam_views]

output_dir = "./data/resized_calib_images"
image_paths = resize_and_save_images(raw_image_paths, output_dir, scale_factor=0.25)

# Step 1: Get manual points from each image and save images with overlaid points
src_pts_list = []
output_img_paths = []

for img_path in image_paths:
    src_pts, output_img_path = get_manual_points(img_path)
    src_pts_list.append(src_pts)
    output_img_paths.append(output_img_path)

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

# Step 4: Warp each image to a bird's-eye view
warped_images = [
    cv2.warpPerspective(cv2.imread(img), H, (dst_width, dst_height))
    for img, H in zip(image_paths, homographies)
]

# Step 5: Stitch images together (Simple max blending)
stitcher = cv2.createStitcher()  # Or use cv2.createStitcherCV()
status, stitched_image = stitcher.stitch(warped_images)

if status == cv2.Stitcher_OK:
    cv2.imshow("Final Bird's-Eye View", stitched_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("stitched_top_view.jpg", stitched_image)
else:
    print("Error during stitching:", status)

# Display results
cv2.imshow("Final Bird's-Eye View", stitched_view)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the final stitched output
cv2.imwrite("stitched_top_view.jpg", stitched_view)
print("Bird's-eye view image saved as 'stitched_top_view.jpg'")
