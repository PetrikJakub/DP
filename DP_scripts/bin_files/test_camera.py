import cv2
from pyueye import ueye
import numpy as np

mem_ptr = ueye.c_mem_p()  # Declare mem_ptr globally
mem_id = ueye.int()       # Declare mem_id globally

def main():
    global mem_ptr, mem_id  # Add these lines to access the global variables

    h_cam = ueye.HIDS(0)
    ret = ueye.is_InitCamera(h_cam, None)

    if ret != ueye.IS_SUCCESS:
        print(f"Error initializing camera. Error code: {ret}")
        return

    print("Camera initialization successful.")

    try:
        ret = ueye.is_SetDisplayMode(h_cam, ueye.IS_SET_DM_DIB)
        if ret != ueye.IS_SUCCESS:
            print(f"Error setting display mode. Error code: {ret}")
            return

        ret = ueye.is_SetColorMode(h_cam, ueye.IS_CM_BGR8_PACKED)
        if ret != ueye.IS_SUCCESS:
            print(f"Error setting color mode. Error code: {ret}")
            return

        width = 2592
        height = 1944
        rect_aoi = ueye.IS_RECT()
        rect_aoi.s32X = 0
        rect_aoi.s32Y = 0
        rect_aoi.s32Width = ueye.INT(width)
        rect_aoi.s32Height = ueye.INT(height)
        ret = ueye.is_AOI(h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))
        if ret != ueye.IS_SUCCESS:
            print(f"Error setting image size. Error code: {ret}")
            return

        ret = ueye.is_CaptureVideo(h_cam, ueye.IS_WAIT)
        if ret != ueye.IS_SUCCESS:
            print(f"Error capturing video. Error code: {ret}")
            return

        cv2.namedWindow("Camera Output", cv2.WINDOW_NORMAL)

        while True:
            _, frame = ueye_capture_frame(h_cam, width, height)
            if frame is not None:
                cv2.imshow("Camera Output", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Error capturing video frame.")
                break

    finally:
        cv2.destroyAllWindows()
        ueye.is_FreeImageMem(h_cam, mem_ptr, mem_id)
        ueye.is_ExitCamera(h_cam)

def ueye_capture_frame(h_cam, width, height):
    global mem_ptr, mem_id  # Add these lines to access the global variables

    ret = ueye.is_FreezeVideo(h_cam, ueye.IS_WAIT)

    if ret == ueye.IS_SUCCESS:
        pitch = ueye.INT()
        ueye.is_GetImageMemPitch(h_cam, pitch)

        bytes_per_pixel = int(24 / 8)
        image_data_size = width * height * bytes_per_pixel

        array = ueye.get_data(mem_ptr, image_data_size)
        frame = np.reshape(array, (height, width, 3))

        return True, frame
    else:
        print(f"Error capturing video frame. Error code: {ret}")
        return False, None

if __name__ == "__main__":
    main()
