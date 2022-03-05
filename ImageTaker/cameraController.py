# This python script is responsible for taking images, adding meta-data, and storing them in a shared folder
# https://www.amazon.com/gp/product/B07C1M86V5/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1
# this is the camera module used
import cv2
import numpy as np
import os
import glob
import shutil

# path variables!
data_path = '../data'
calibration_path = data_path + '/calibration_data'
camera_matrices_path = calibration_path + '/camera_matrices'
calibration_images_path = calibration_path + '/calibration_image_sets'
runtime_images_path = data_path + '/runtime_image_data'

camera_object_array = []


def initialize_camera(camera_index_array):
    if not os.path.exists(data_path):
        print("no data folder, making one")
        os.makedirs(data_path)

    if not os.path.exists(calibration_path):
        print("no camera calibration_data folder, making one")
        os.makedirs(calibration_path)

    if not os.path.exists(camera_matrices_path):
        print("no camera_matrices folder, making one")
        os.makedirs(camera_matrices_path)

    if not os.path.exists(calibration_images_path):
        print("no calibration_images folder, making one")
        os.makedirs(calibration_images_path)

    if not os.path.exists(runtime_images_path):
        print("no runtime_images folder, making one")
        os.makedirs(runtime_images_path)

    for index in camera_index_array:
        camera_object_array.append(cameraObject(index, camera_matrices_path, calibration_images_path))


class cameraObject:
    calib_matrix_path = None
    calib_images_path = None
    camera_no = None
    camera_no_str = None

    def __init__(self, given_no, base_calib_matrix_path, base_calib_images_path):
        self.camera_no = given_no
        self.camera_no_str = str(given_no)

        self.calib_matrix_path = base_calib_matrix_path + '/camera' + self.camera_no_str + '_matrices.txt'
        self.calib_images_path = base_calib_images_path + '/camera' + self.camera_no_str + '_calibration_images'

        if not os.path.exists(self.calib_matrix_path):
            print("no camera calibration matrix, making one for camera: ", given_no)
            # os.makedirs(self.calib_matrix_path)
            f = open(self.calib_matrix_path, "w")
            f.close()

            if not os.path.exists(self.calib_images_path):
                print("no camera calibration images folder exists, making one for camera: ", given_no)
                os.makedirs(self.calib_images_path)

        calibrate_camera(self)
        # np.loadtxt(self.calib_matrix_path, delimiter=',')


def calibrate_camera(camera):
    images = glob.glob(camera.calib_images_path + "/*.png")
    if len(images) < 10:
        clear_folder(camera.calib_images_path)
        take_calibration_images(camera.camera_no, camera.calib_images_path)
        images = glob.glob(camera.calib_images_path + "/*.png")

    checkerboard_size = [6, 9]
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[1], 0:checkerboard_size[0]].T.reshape(-1, 2)
    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    test_img = None

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, checkerboard_size, corners2, ret)
            test_img = gray

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, test_img.shape[::-1], None, None)

    write_calib_matrices(camera.calib_matrix_path, mtx, dist)

    # print("Camera matrix : \n", mtx)
    # print("dist : \n", dist)
    # print("rvecs : \n", rvecs)
    # print("tvecs : \n", tvecs)


# takes and stores calibration images
def take_calibration_images(cam_no, img_folder_path):
    result_img_array = []
    checkerboard_size = [6, 9]
    cam = cv2.VideoCapture(cam_no)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    cv2.namedWindow("test")

    img_counter = 0
    while len(result_img_array) < 14:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "calibration_image_{}.png".format(img_counter)
            cv2.imwrite(os.path.join(img_folder_path, img_name), frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
            if ret:
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                cv2.drawChessboardCorners(frame, checkerboard_size, corners2, ret)
                cv2.imshow("test", frame)
                result_img_array.append(frame)
                img_counter += 1
                print("number: ", img_counter)
                cv2.waitKey(500)
            else:
                print("ERROR")

    cam.release()

    cv2.destroyAllWindows()

    return result_img_array


def clear_folder(folder_dir):
    print("clearing", folder_dir)
    folder = folder_dir
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def write_calib_matrices(path, mtx, dist):
    np.savetxt(path, mtx, delimiter=',')


