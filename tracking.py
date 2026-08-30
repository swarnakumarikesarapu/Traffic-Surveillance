from ultralytics import YOLO
import cv2
import csv
from collections import defaultdict

# ==========================================
# LOAD YOLO MODEL
# ==========================================

model = YOLO("yolo11m.pt")

# ==========================================
# OPEN VIDEO
# ==========================================

video = cv2.VideoCapture("videos/traffic.mp4")

if not video.isOpened():
    print("ERROR: Cannot open video")
    exit()

# ==========================================
# VEHICLE CLASSES
# ==========================================

vehicle_classes = {
    "car",
    "motorcycle",
    "bus",
    "truck"
}

# ==========================================
# UNIQUE TRACKING IDs
# ==========================================

counted_ids = defaultdict(set)

# ==========================================
# PROCESS VIDEO
# ==========================================

while True:

    ret, frame = video.read()

    if not ret:
        print("Video finished")
        break

    # Resize 4K video
    frame = cv2.resize(frame, (960, 540))

    # ======================================
    # YOLO + BYTETRACK
    # ======================================

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        conf=0.35,
        iou=0.5,
        classes=[2, 3, 5, 7],
        verbose=False
    )

    result = results[0]

    # ======================================
    # CREATE OUTPUT FRAME
    # ======================================

    annotated_frame = frame.copy()

    # ======================================
    # GET TRACKING INFORMATION
    # ======================================

    if result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().numpy()

        track_ids = result.boxes.id.int().cpu().tolist()

        class_ids = result.boxes.cls.int().cpu().tolist()

        confidences = result.boxes.conf.cpu().numpy()

        # ==================================
        # PROCESS EACH VEHICLE
        # ==================================

        for box, track_id, class_id, confidence in zip(
            boxes,
            track_ids,
            class_ids,
            confidences
        ):

            class_name = model.names[class_id]

            # Ignore non-vehicles
            if class_name not in vehicle_classes:
                continue

            # Store unique ID
            counted_ids[class_name].add(track_id)

            # Coordinates
            x1, y1, x2, y2 = map(int, box)

            # Draw bounding box
            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Label
            label = f"ID:{track_id} {class_name} {confidence:.2f}"

            cv2.putText(
                annotated_frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    # ==========================================
    # CALCULATE COUNTS
    # ==========================================

    car_count = len(counted_ids["car"])

    motorcycle_count = len(counted_ids["motorcycle"])

    bus_count = len(counted_ids["bus"])

    truck_count = len(counted_ids["truck"])

    total_count = (
        car_count
        + motorcycle_count
        + bus_count
        + truck_count
    )

    # ==========================================
    # DISPLAY COUNTS
    # ==========================================

    cv2.putText(
        annotated_frame,
        f"Cars: {car_count}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Motorcycles: {motorcycle_count}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Buses: {bus_count}",
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Trucks: {truck_count}",
        (20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated_frame,
        f"TOTAL VEHICLES: {total_count}",
        (20, 165),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    # ==========================================
    # DISPLAY VIDEO
    # ==========================================

    cv2.namedWindow(
        "Traffic Surveillance",
        cv2.WINDOW_NORMAL
    )

    cv2.imshow(
        "Traffic Surveillance",
        annotated_frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==========================================
# RELEASE
# ==========================================

video.release()
cv2.destroyAllWindows()

# ==========================================
# SAVE CSV
# ==========================================

with open(
    "traffic_counts.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow(["Vehicle Type", "Count"])

    writer.writerow(["Car", car_count])

    writer.writerow(["Motorcycle", motorcycle_count])

    writer.writerow(["Bus", bus_count])

    writer.writerow(["Truck", truck_count])

    writer.writerow(["Total", total_count])

# ==========================================
# FINAL OUTPUT
# ==========================================

print()
print("======================================")
print("       FINAL TRAFFIC COUNT")
print("======================================")

print("Cars        :", car_count)
print("Motorcycles :", motorcycle_count)
print("Buses       :", bus_count)
print("Trucks      :", truck_count)
print("TOTAL       :", total_count)

print("======================================")
print("Saved to traffic_counts.csv")
print("======================================")