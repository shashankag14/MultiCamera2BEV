import os
import cv2
import numpy as np
from pathlib import Path
from src.points_manager import load_points, save_points
from src.bev_processor import BirdEyeViewProcessor

stitch_err_dict = {
    cv2.STITCHER_OK: "STITCHER_OK",
    cv2.STITCHER_ERR_NEED_MORE_IMGS: "STITCHER_ERR_NEED_MORE_IMGS",
    cv2.STITCHER_ERR_HOMOGRAPHY_EST_FAIL: "STITCHER_ERR_HOMOGRAPHY_EST_FAIL",
    cv2.STITCHER_ERR_CAMERA_PARAMS_ADJUST_FAIL: "STITCHER_ERR_CAMERA_PARAMS_ADJUST_FAIL",
}

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

def get_manual_points(image_path):
    """Opens an image, lets the user click 4 points, and overlays them with labels."""
    global selected_points
    selected_points = []
    print('-------------')
    print(f"Image: {image_path}")
    img = cv2.imread(image_path)
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

    return np.array(selected_points, dtype=np.float32)

def main():
    # image paths for calibration and stitching
    base_path = "./data/resized_calib_images/"
    cam_views = ["1L", "2L", "M", "1R", "2R"]
    image_paths = [base_path + cam_view + ".jpg" for cam_view in cam_views]

    # Load previously saved points for calibration
    points_file = "./data/selected_points.json"
    src_pts_list = load_points(points_file) or []

    # If no points found, let the user select them manually and save
    if not src_pts_list:
        print("No points found. Please manually select points.")
        for image_path in image_paths:
            src_pts = get_manual_points(image_path)
            src_pts_list.append(src_pts)
        save_points(points_file, src_pts_list)

    # Destination bird's-eye view coordinates
    dst_pts = np.float32([[0, 0], [500, 0], [500, 300], [0, 300]])

    # Process images for BEV
    bev_processor = BirdEyeViewProcessor(image_paths, dst_pts, "./data/warped_images")
    warped_images = bev_processor.process(src_pts_list)

    # Stitch images
    stitcher = cv2.Stitcher_create()
    status, stitched_image = stitcher.stitch(warped_images)
    
    if status == cv2.Stitcher_OK:
        cv2.imwrite("stitched_top_view.jpg", stitched_image)
        print("Stitched image saved successfully!")
    else:
        print(f"Stitching failed with error code {status} : {stitch_err_dict[status]}")

if __name__ == "__main__":
    main()
