import cv2
import numpy as np
from utils.streamer import Streamer
from utils.video_writer import VideoWriter
from utils.helpers import get_calibration_maps, disparity_to_colormap

if __name__ == "__main__":

    # Define paths
    camera_left = 'dataset_40_3/Left_cam'
    camera_right = 'dataset_40_3/Right_cam'
    
    config_left = "dataset_40_3/config/left_camera.yaml"
    config_right = "dataset_40_3/config/right_camera.yaml"

    # Stereo-vision camera calibration
    map1_x, map2_x, map1_y, map2_y = get_calibration_maps(config_left, config_right)

    # Define instances
    recorder = VideoWriter('output_video.avi')
    s1 = Streamer(camera_left)
    s2 = Streamer(camera_right)
    stereo = cv2.StereoBM_create()

    # Setting the updated parameters before computing disparity map
    numDisparities = 16
    minDisparity = 0

    stereo.setNumDisparities(numDisparities)
    stereo.setBlockSize(63)
    stereo.setPreFilterType(1)
    stereo.setPreFilterSize(7)
    stereo.setPreFilterCap(62)
    stereo.setTextureThreshold(0)
    stereo.setUniquenessRatio(7)
    stereo.setSpeckleRange(0)
    stereo.setSpeckleWindowSize(0)
    stereo.setDisp12MaxDiff(1)
    stereo.setMinDisparity(minDisparity)
    
    # Main loop
    while 1:
        # Stream the stereo images
        img_L = s1.get()
        img_R = s2.get()

        # Check if any images are available
        if img_L is None:
            break

        # Calibrate the images.
        # Note that the cameras usually have distortions and need to be calibrated.
        # Also, stereo cameras need to be calibrated according to eachother.
        img_L = cv2.remap(img_L, map1_x, map1_y, cv2.INTER_LINEAR)
        img_R = cv2.remap(img_R, map2_x, map2_y, cv2.INTER_LINEAR)

        # grayscale images are needed
        imgR_gray = cv2.cvtColor(img_R, cv2.COLOR_BGR2GRAY)
        imgL_gray = cv2.cvtColor(img_L, cv2.COLOR_BGR2GRAY)

        # Compute the disparity using CV2
        disparity = stereo.compute(imgL_gray, imgR_gray)

        # Normalize the disparity to show the results
        disparity = disparity.astype(np.float32)
        disparity = (disparity / 16.0 - minDisparity) / numDisparities

        # A little color for a more understandable result
        disparity_jet = disparity_to_colormap(disparity)

        # combine the resulting frames
        result = cv2.hconcat([img_L, disparity_jet])

        cv2.imshow('Stereo-Vision', result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        recorder.record(result)