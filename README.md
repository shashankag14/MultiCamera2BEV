# MultiCamera2BEV
A classicial computer vision based approach to transform images from multi-camera sensors to a single bird's-eye view (BEV) image. It provides a simple implementation for performing bird's-eye view (BEV) transformation using homography. It involves selecting points manually on the images, computing homographies, and transforming the images to a bird's-eye view perspective.

> The code implementation is in progress.

![Source: https://www.researchgate.net/figure/Birds-eye-view-vision-system-Images-F-f-F-l-F-r-F-b-are-captured-from-the-front_fig4_273596538](image.png)
*Source: [Automatic Parking based on a Bird's Eye View System](https://www.researchgate.net/figure/Birds-eye-view-vision-system-Images-F-f-F-l-F-r-F-b-are-captured-from-the-front_fig4_273596538)*

## Steps
1. Load and resize images.
2. Manually select points on images for the BEV transformation.
3. Compute homographies using selected points.
4. Warp images to the bird's-eye view perspective.
5. Stitch the warped images together to create a final BEV image.

## Install
Follow these steps to get your project set up.
```
git clone https://github.com/shashankag14/MultiCamera2BEV.git
cd MultiCamera2BEV
conda env create -f environment.yml
conda activate bev
```

## Usage
Run the following command form the root directory:
```
python main.py
```

## Side Notes
- The ``calib_points.json`` file is used to save the points you manually select. If you already have this file, the script skips the manual selection and use the saved points.
- The images should be correctly oriented and the selected points should correspond to the desired region for the bird's-eye view.
- The final shape of the BEV output matters how the input images are warped and how much overlap they share with each other. Fine-tuning the final output shape always helps.
- Make sure that you have enough features in each warped image after applying the homography. These features are used for feature matching and image stitching at the end.

## ToDo:
&#9744;  Analyze different feature detection techniques - OBR, SIFT
&#9744; Investigate on enhacing the warped images, if there aren't enough features available for feature matching
&#9744; Choose the best shape for BEV output. It affects the warped images generated after applying the homography
&#9744; Use a logger for the repository
&#9744; Improve error handling
&#9744; Refactor main.py