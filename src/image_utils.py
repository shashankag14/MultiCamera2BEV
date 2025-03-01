import cv2
import os


def resize_and_save_images(image_paths, output_dir, scale_factor=0.5):
    """Resizes images and saves them in a new folder. (if needed)"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    resized_paths = []
    for img_path in image_paths:
        img = cv2.imread(img_path)
        print(f"Loading image: {img_path}")
        print(f"Original Image Shape: {img.shape[:-1]}")

        if img is None:
            print(f"Error: Could not load {img_path}. Skipping.")
            continue

        # Resize image
        resized_img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor)
        print(f"Resized Image Shape: {resized_img.shape[:-1]}")

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
        cv2.putText(img_copy, f"Point {i+1}", (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    cv2.imwrite(output_img_path, img_copy)
    print(f"Saved image with points: {output_img_path}")


def visualize_keypoints(image, output_img_path, title="Keypoints"):
    """Detect and draw keypoints on an image."""
    img_copy = image.copy()
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create()  # TODO: try SIFT_create
    keypoints = orb.detect(gray, None)

    # Draw keypoints on the image
    output = cv2.drawKeypoints(img_copy, keypoints, None, color=(0, 255, 0))

    # Show the image
    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    cv2.imwrite(output_img_path, img_copy)
    cv2.imshow(title, output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(f"Saved image with features: {output_img_path}")


def enhance_contrast(image):
    """Apply adaptive histogram equalization to improve contrast."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    enhanced = cv2.merge((l, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
