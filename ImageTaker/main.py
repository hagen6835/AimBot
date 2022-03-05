    # This python script is responsible for taking images, adding meta-data, and storing them in a shared folder
# https://www.amazon.com/gp/product/B07C1M86V5/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1
# this is the camera module used
import cameraController

if __name__ == '__main__':
    camera_index_array = [0, 1]
    cameraController.initialize_camera(camera_index_array)
    # cameraController.also_initialize_camera()



