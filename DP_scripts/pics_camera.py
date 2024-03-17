import cv2
from pyueye import ueye
import numpy as np
import os
import re

# Global variables for folder and picture numbers
folder_number = 1
picture_number = 1
folder_prefix = "run"  # Add the desired prefix here


def initialize_camera():
    global folder_number  # Use the global variable
    folder_number = get_next_folder_number('pictures')  # Call the function to get the next folder number

    h_cam = ueye.HIDS(0)
    ret = ueye.is_InitCamera(h_cam, None)

    if ret != ueye.IS_SUCCESS:
        print(f"Error initializing camera. Error code: {ret}")
        return None, None, None
    else:
        print("Camera initialization successful.")

        mem_ptr = ueye.c_mem_p()
        mem_id = ueye.int()

        try:
            # Set display mode to DIB
            ret = ueye.is_SetDisplayMode(h_cam, ueye.IS_SET_DM_DIB)
            if ret != ueye.IS_SUCCESS:
                print(f"Error setting display mode. Error code: {ret}")
                return None, None, None

            # Set color mode to BGR8
            ret = ueye.is_SetColorMode(h_cam, ueye.IS_CM_BGR8_PACKED)
            if ret != ueye.IS_SUCCESS:
                print(f"Error setting color mode. Error code: {ret}")
                return None, None, None

            # Set the image size
            width = 1280
            height = 720
            rect_aoi = ueye.IS_RECT()
            rect_aoi.s32X = 0
            rect_aoi.s32Y = 0
            rect_aoi.s32Width = ueye.INT(width)
            rect_aoi.s32Height = ueye.INT(height)
            ret = ueye.is_AOI(h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))
            if ret != ueye.IS_SUCCESS:
                print(f"Error setting image size. Error code: {ret}")
                return None, None, None

            # Allocate memory for the image
            ret = ueye.is_AllocImageMem(h_cam, width, height, 24, mem_ptr, mem_id)
            if ret != ueye.IS_SUCCESS:
                print(f"Error allocating image memory. Error code: {ret}")
                return None, None, None

            # Set the image memory for the camera
            ret = ueye.is_SetImageMem(h_cam, mem_ptr, mem_id)
            if ret != ueye.IS_SUCCESS:
                print(f"Error setting image memory. Error code: {ret}")
                return None, None, None

        except:
            print("An error occurred during camera initialization.")
            return None, None, None

        return h_cam, mem_ptr, mem_id


def close_camera(h_cam, mem_ptr, mem_id):
    ueye.is_FreeImageMem(h_cam, mem_ptr, mem_id)
    ueye.is_ExitCamera(h_cam)
    print("Camera closed.")


def capture_and_save_image(h_cam, mem_ptr, width, height):
    global picture_number  # Use the global variable
    ret = ueye.is_FreezeVideo(h_cam, ueye.IS_WAIT)
    if ret == ueye.IS_SUCCESS:
        pitch = ueye.INT()
        ueye.is_GetImageMemPitch(h_cam, pitch)
        array = ueye.get_data(mem_ptr, width, height, 24, pitch, copy=True)
        frame = np.reshape(array, (height, width, 3))
        frame = cv2.flip(frame, 0)

        # Folder name for each run
        run_folder = f'{folder_prefix}{folder_number}'
        run_path = os.path.join('pictures', run_folder)

        # If the folder doesn't exist, create it
        if not os.path.exists(run_path):
            os.makedirs(run_path)

        # Unique name for each image
        unique_name = f'picture{picture_number}.png'
        image_path = os.path.join(run_path, unique_name)

        # Save the image
        create_image(frame, image_path)

        # Increment picture number for the next image
        picture_number += 1


def create_image(frame, path):
    # Code for saving the image to the specified path
    cv2.imwrite(path, frame)
    print(f"Image saved at {path}")
#
# def create_image(frame, path):
#     # Convert the frame to grayscale
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # Save the grayscale image
#     cv2.imwrite(path, gray_frame)
#     print(f"Grayscale Image saved at {path}")

def get_next_folder_number(base_path):
    folders = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder)) and folder.startswith(folder_prefix)]
    if not folders:
        return 1

    # Find the last number and add one
    last_number = max([int(re.search(rf'{folder_prefix}(\d+)', folder).group(1)) for folder in folders], default=0)
    return last_number + 1


if __name__ == "__main__":
    hCam, memPtr, memId = initialize_camera()

    # Add your main loop here, for example, a loop capturing and saving images
    for _ in range(5):  # Capture and save 5 images for example
        capture_and_save_image(hCam, memPtr, 1280, 720)

    close_camera(hCam, memPtr, memId)
