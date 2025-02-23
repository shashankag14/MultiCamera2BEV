import cv2
import numpy as np
from .image_utils import resize_and_save_images, save_image_with_points

class BirdEyeViewProcessor:
    def __init__(self, image_paths, dst_pts, output_dir):
        self.image_paths = image_paths
        self.dst_pts = dst_pts
        self.output_dir = output_dir
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
        dst_width, dst_height = 500, 300  # Scale for better visualization
        warped_images = [
            cv2.warpPerspective(cv2.imread(img), H, (dst_width, dst_height))
            for img, H in zip(self.image_paths, homographies)
        ]
        return warped_images

    def process(self, src_pts_list):
        homographies = self.compute_homographies(src_pts_list)
        warped_images = self.warp_images(homographies)

        for i, warped_image in enumerate(warped_images):
            if warped_image is None or warped_image.size == 0:
                print(f"Error: Warped image {i} is empty. Skipping stitching.")
                continue
            warped_image_path = f"{self.output_dir}/warped_image_{i}.jpg"
            save_image_with_points(warped_image, [], warped_image_path)

        return warped_images
