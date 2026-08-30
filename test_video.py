import cv2

video = cv2.VideoCapture("videos/traffic.mp4")

print("Opened:", video.isOpened())

ret, frame = video.read()

print("Frame read:", ret)

if ret:
    print("Frame size:", frame.shape)
    cv2.imwrite("test_frame.jpg", frame)

video.release()