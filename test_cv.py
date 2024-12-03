import cv2

# Open the camera (0 is usually the default camera)
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Press 'q' to exit.")

while True:
    # Capture a frame
    ret, frame = camera.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Display the frame
    cv2.imshow("Camera Feed", frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
camera.release()
cv2.destroyAllWindows()
