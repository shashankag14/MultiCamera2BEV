import cv2
import numpy as np
from .image_utils import (
    save_image_with_points, visualize_keypoints, enhance_contrast)


class BirdEyeViewProcessor:
    def __init__(self, image_paths, dst_pts, output_dir, use_sift=True):
        self.image_paths = image_paths
        self.dst_pts = dst_pts
        self.output_dir = output_dir
        self.use_sift = use_sift
        self.src_pts_list = []

    def compute_homographies(self, src_pts_list):
        """Compute homographies for each camera."""
        homographies = []
        for src in src_pts_list:
            H, status = cv2.findHomography(src, self.dst_pts)
            homographies.append(H)
        print(f"Homographies computed: {len(homographies)}")
        return homographies

    def warp_images(self, homographies):
        """Warp each image to bird's-eye view."""
        # TODO: pass width and height of dst points using config
        dst_width, dst_height = 500, 300  # Scale for better visualization
        warped_images = [
            cv2.warpPerspective(cv2.imread(img), H, (dst_width, dst_height))
            for img, H in zip(self.image_paths, homographies)
        ]
        return warped_images

    def vis_detected_features(self, images):
        """Visualize detected features in each warped image."""
        for i, warped_image in enumerate(images):
            path_to_save = f"{self.output_dir}/detected_features/warped_image_{i}.jpg"
            visualize_keypoints(
                warped_image, path_to_save, self.use_sift, title=f"Keypoints in Image {i}")

    def process(self, src_pts_list, feature_enhancement=False):
        homographies = self.compute_homographies(src_pts_list)
        warped_images = self.warp_images(homographies)

        for i, warped_image in enumerate(warped_images):
            if warped_image is None or warped_image.size == 0:
                print(f"Error: Warped image {i} is empty. Skipping stitching.")
                continue
            warped_image_path = f"{self.output_dir}/warped_image_{i}.jpg"
            save_image_with_points(warped_image, [], warped_image_path)

        # Enahnce the contrast of warped images to boost the feature selection
        if feature_enhancement:
            warped_images = [enhance_contrast(img) for img in warped_images]

        # Visualize all warped image side by side to verify the overlap
        combined = np.hstack(warped_images)
        cv2.imwrite(f"{self.output_dir}/warped_images_combined.jpg", combined)
        cv2.imshow("Warped Images Combined", combined)
        cv2.waitKey(0)

        # Visualise detected features in each warped image
        self.vis_detected_features(warped_images)

        return warped_images
