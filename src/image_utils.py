import cv2
import os

def resize_and_save_images(image_paths, output_dir, scale_factor=0.5):
    """Resizes images and saves them in a new folder. (if needed)"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    resized_paths = []
    for img_path in image_paths:
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Error: Could not load {img_path}. Skipping.")
            continue
        
        # Resize image
        resized_img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor)

        # Save resized image
        filename = os.path.basename(img_path)
        new_path = os.path.join(output_dir, filename)
        cv2.imwrite(new_path, resized_img)
        resized_paths.append(new_path)

        print(f"Saved resized image: {new_path}")

    return resized_paths  # Return new paths to use in BEV processing

def save_image_with_points(image, points, output_img_path):
    """Overlay points on an image and save."""
    img_copy = image.copy()

    for i, (x, y) in enumerate(points):
        cv2.circle(img_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(img_copy, f"Point {i+1}", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    cv2.imwrite(output_img_path, img_copy)
    print(f"Saved image with points: {output_img_path}")
