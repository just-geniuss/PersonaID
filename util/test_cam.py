import cv2

def init_camera(camera_index=0):
    """Initialize camera with proper backend and fallback mechanisms"""
    # Try with DirectShow backend first (Windows/OBS compatibility)
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Any available")
    ]
    
    camera_indices = [camera_index, 0, 1, 2]  # Try specified index first, then common defaults
    
    cap = None
    for backend_id, backend_name in backends:
        for cam_idx in camera_indices:
            try:
                print(f"Trying camera {cam_idx} with {backend_name} backend...")
                test_cap = cv2.VideoCapture(cam_idx, backend_id)
                if test_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, frame = test_cap.read()
                    if ret and frame is not None:
                        cap = test_cap
                        print(f"Successfully opened camera {cam_idx} with {backend_name} backend")
                        break
                    else:
                        test_cap.release()
                else:
                    test_cap.release()
            except Exception as e:
                print(f"Failed to open camera {cam_idx} with {backend_name}: {e}")
                if test_cap is not None:
                    test_cap.release()
        if cap is not None:
            break
    
    if cap is None or not cap.isOpened():
        raise RuntimeError("Cannot open any camera. Please check camera connection and permissions.")
    
    return cap

vid = init_camera(camera_index=0)

while (True):
    ret, frame = vid.read()
    if not ret:
        print("Failed to read frame. Exiting...")
        break
    cv2.imshow('frame', frame)
    # cv2.imwrite("./img.png", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()
