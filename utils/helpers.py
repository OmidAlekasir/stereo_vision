import cv2
import numpy as np
import yaml

def get_calibration_maps(path_left, path_right):

    # Load the stereo-vision setup configuration
    calib_left, calib_right, img_shape = __load_camera_config(path_left, path_right)

    # Analyze configuration
    dist_coeffs_left, dist_coeffs_right, intrinsics_left, intrinsics_right, R, T = (
        __get_calibration_matrices(calib_left, calib_right)
    )

    # This matrix shows the 3D rotation of the right-side camera to the left-side camera
    R = np.eye(3) # NO ROTATION

    # Stereo rectification
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
        intrinsics_left,
        dist_coeffs_left,
        intrinsics_right,
        dist_coeffs_right,
        img_shape,
        R,
        T,
    )

    # Compute the undistortion and rectification transformation map
    map1_x, map1_y = cv2.initUndistortRectifyMap(
        intrinsics_left, dist_coeffs_left, R1, P1, img_shape, cv2.CV_32FC1
    )
    map2_x, map2_y = cv2.initUndistortRectifyMap(
        intrinsics_right, dist_coeffs_right, R2, P2, img_shape, cv2.CV_32FC1
    )

    return map1_x, map2_x, map1_y, map2_y

def __load_camera_config(path_left, path_right):

    with open(path_left, 'r') as file:
        calib_left = yaml.safe_load(file)
    with open(path_right, 'r') as file:
        calib_right = yaml.safe_load(file)

    img_shape = np.array(calib_left['resolution'])

    return calib_left, calib_right, img_shape

def __get_calibration_matrices(calib_left, calib_right):
    intrinsics0 = np.array(calib_left['intrinsics'])
    intrinsics1 = np.array(calib_right['intrinsics'])
    dist_coeffs_left = np.array(calib_left['distortion_coefficients'])
    dist_coeffs_right = np.array(calib_right['distortion_coefficients'])

    intrinsics_left = np.array(
        [
            [intrinsics0[0], 0.0, intrinsics0[2]],
            [0.0, intrinsics0[1], intrinsics0[3]],
            [0.0, 0.0, 1.0],
        ]
    )

    intrinsics_right = np.array(
        [
            [intrinsics1[0], 0.0, intrinsics1[2]],
            [0.0, intrinsics1[1], intrinsics1[3]],
            [0.0, 0.0, 1.0],
        ]
    )

    transformation_left = np.array(calib_left['T_BS']['data']).reshape((4, 4))
    transformation_right = np.array(calib_right['T_BS']['data']).reshape((4, 4))

    # this matrix shows the transformation matrix of the right-side camera, according to the left-side camera
    transform_R2L = __relative_transformation(transformation_left, transformation_right)

    R = transform_R2L[0:3, 0:3]
    T = transform_R2L[0:3, 3]

    return dist_coeffs_left, dist_coeffs_right, intrinsics_left, intrinsics_right, R, T

def __relative_transformation(A, B):
    # A is the transformation matrix of the 1st point that you want to consider it as the new origin (leftside camera)
    # B is the transformation matrix of the 2nd point that you want to transform it, according to the firts point (rightside camera)

    R = A[0:3, 0:3]
    T = A[0:3, 3]

    W = np.zeros((4, 4))
    W[:3, :3] = R.T
    W[:3, 3] = np.dot(-R.T, T)
    W[3, 3] = 1

    return np.dot(W, B)

def disparity_to_colormap(disparity_map):
    disparity_map = (
        disparity_map - np.min(disparity_map)
    ) * 1.5
    colormap = cv2.applyColorMap(
        (disparity_map * 255).astype(np.uint8), cv2.COLORMAP_JET
    )

    return colormap