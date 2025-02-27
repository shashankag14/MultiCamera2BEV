# MultiCamera2BEV
A classicial computer vision based approach to transform images from multi-camera sensors to a single bird's-eye view (BEV) image.
It provides a simple implementation for performing bird's-eye view (BEV) transformation using homography. It involves selecting points manually on the images, computing homographies, and transforming the images to a bird's-eye view perspective.

## Steps
1. Load and resize images.
2. Manually select points on images for the BEV transformation.
3. Compute homographies using selected points.
4. Warp images to the bird's-eye view perspective.
5. Stitch the warped images together to create a final BEV image.

## Usage
Run the following command form the root directory:
```
python main.py
```

## Side Notes
- The ``selected_points.json`` file is used to save the points you manually select. If you already have this file, the script skips the manual selection and use the saved points.
- The images should be correctly oriented and the selected points should correspond to the desired region for the bird's-eye view.