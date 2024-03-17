import cv2
from pyueye import ueye
import numpy as np
from meshing_script import meshing_proces


h_cam = ueye.HIDS(0)
ret = ueye.is_InitCamera(h_cam, None)

if ret != ueye.IS_SUCCESS:
    print(f"Error initializing camera. Error code: {ret}")
else:
    print("Camera initialization successful.")

    try:
        # Set display mode to DIB
        ret = ueye.is_SetDisplayMode(h_cam, ueye.IS_SET_DM_DIB)
        if ret != ueye.IS_SUCCESS:
            print(f"Error setting display mode. Error code: {ret}")
        else:
            # Set color mode to BGR8
            ret = ueye.is_SetColorMode(h_cam, ueye.IS_CM_BGR8_PACKED)
            if ret != ueye.IS_SUCCESS:
                print(f"Error setting color mode. Error code: {ret}")
            else:
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
                else:
                    # Allocate memory for the image
                    mem_ptr = ueye.c_mem_p()
                    mem_id = ueye.int()
                    ret = ueye.is_AllocImageMem(h_cam, width, height, 24, mem_ptr, mem_id)
                    if ret != ueye.IS_SUCCESS:
                        print(f"Error allocating image memory. Error code: {ret}")
                    else:
                        # Set the image memory for the camera
                        ret = ueye.is_SetImageMem(h_cam, mem_ptr, mem_id)
                        if ret != ueye.IS_SUCCESS:
                            print(f"Error setting image memory. Error code: {ret}")
                        else:
                            # Capture video
                            ret = ueye.is_CaptureVideo(h_cam, ueye.IS_WAIT)
                            if ret != ueye.IS_SUCCESS:
                                print(f"Error capturing video. Error code: {ret}")
                            else:
                                cv2.namedWindow("Camera Output", cv2.WINDOW_NORMAL)

                                while True:
                                    # Capture a frame from the camera
                                    ret = ueye.is_FreezeVideo(h_cam, ueye.IS_WAIT)
                                    if ret == ueye.IS_SUCCESS:
                                        # Retrieve the pitch of the image
                                        pitch = ueye.INT()
                                        ueye.is_GetImageMemPitch(h_cam, pitch)

                                        # Copy the image data from camera memory to a NumPy array
                                        array = ueye.get_data(mem_ptr, width, height, 24, pitch, copy=True)

                                        # Reshape the NumPy array to a format compatible with OpenCV
                                        frame = np.reshape(array, (height, width, 3))

                                        # Flip the frame upside down
                                        frame = cv2.flip(frame, 0)

                                        # Display the frame
                                        cv2.imshow("Camera Output", frame)

                                        if cv2.waitKey(1) & 0xFF == ord('q'):
                                            break

                                    else:
                                        print(f"Error capturing video frame. Error code: {ret}")

                                cv2.destroyAllWindows()
                                ueye.is_FreeImageMem(h_cam, mem_ptr, mem_id)
                                ueye.is_ExitCamera(h_cam)
    finally:
        ueye.is_ExitCamera(h_cam)
