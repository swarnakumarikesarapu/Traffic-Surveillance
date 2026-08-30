import json
import csv
import os
import time
from datetime import datetime

from ultralytics import YOLO
import cv2


# =========================================================
# LOAD YOLO MODEL
# =========================================================

model = YOLO("yolo11n.pt")


# =========================================================
# OPEN VIDEO
# =========================================================

video = cv2.VideoCapture("videos/traffic.mp4")

if not video.isOpened():
    print("ERROR: Video could not be opened.")
    exit()

print("Video opened successfully")


# =========================================================
# STORE UNIQUE TRACKED VEHICLE IDs
# =========================================================

tracked_ids = set()

# =========================================================
# ACCIDENT DATA
# =========================================================

accident_file = "accident_data.json"


def save_accident_data(
    accident_detected=False,
    message="No Accident Detected"
):

    accident_data = {
        "accident_detected": accident_detected,
        "alert_message": message,
        "time": (
            datetime.now().strftime("%H:%M:%S")
            if accident_detected
            else ""
        )
    }

    with open(accident_file, "w") as file:

        json.dump(
            accident_data,
            file,
            indent=4
        )


# Start with no accident
save_accident_data()


# =========================================================
# CSV TRAFFIC LOG
# =========================================================

csv_file = "traffic_counts.csv"

if not os.path.exists(csv_file):

    with open(csv_file, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "Cars",
            "Buses",
            "Bikes",
            "Persons",
            "Total",
            "Unique",
            "Traffic_Status"
        ])


# =========================================================
# CSV UPDATE TIMER
# =========================================================

last_csv_update = time.time()

CSV_INTERVAL = 5


# =========================================================
# MAIN VIDEO LOOP
# =========================================================

# =========================================================
# ACCIDENT DETECTION FUNCTION
# =========================================================

def detect_accident(frame):
    """
    Placeholder for accident detection.

    Returns:
        True  -> Accident detected
        False -> No accident
    """

    # Actual accident detection model
    # will be connected here later.

    return False
while True:

    ret, frame = video.read()

    if not ret:
        print("Video ended")
        break


    # =====================================================
    # RESIZE FRAME
    # =====================================================

    frame = cv2.resize(frame, (640, 360))


    # =====================================================
    # YOLO TRACKING
    # =====================================================

    results = model.track(
        frame,
        persist=True,
        verbose=False
    )


    # =====================================================
    # COUNTERS
    # =====================================================

    car_count = 0
    bus_count = 0
    bike_count = 0
    person_count = 0


    # =====================================================
    # PROCESS TRACKED OBJECTS
    # =====================================================

    if results[0].boxes.id is not None:

        ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(results[0].boxes, ids):

            cls = int(box.cls[0])

            # Save unique tracking ID
            tracked_ids.add(int(track_id))


            # Person
            if cls == 0:
                person_count += 1


            # Car
            elif cls == 2:
                car_count += 1


            # Motorcycle
            elif cls == 3:
                bike_count += 1


            # Bus
            elif cls == 5:
                bus_count += 1


    # =====================================================
    # TOTAL VEHICLES
    # =====================================================

    total_vehicles = (
        car_count +
        bus_count +
        bike_count
    )


    # =====================================================
    # UNIQUE VEHICLES
    # =====================================================

    unique_vehicle_count = len(tracked_ids)


    # =====================================================
    # TRAFFIC DENSITY
    # =====================================================

    if total_vehicles <= 10:

        traffic_status = "LOW"

    elif total_vehicles <= 20:

        traffic_status = "MEDIUM"

    else:

        traffic_status = "HIGH"


    # =====================================================
    # SAVE CURRENT DATA TO JSON
    # =====================================================

    data = {

        "cars": car_count,

        "buses": bus_count,

        "bikes": bike_count,

        "persons": person_count,

        "total": total_vehicles,

        "unique": unique_vehicle_count,

        "traffic_status": traffic_status
    }


    with open("traffic_data.json", "w") as file:

        json.dump(data, file, indent=4)


    # =====================================================
    # SAVE TRAFFIC HISTORY TO CSV
    # EVERY 5 SECONDS
    # =====================================================

    current_time = time.time()

    if current_time - last_csv_update >= CSV_INTERVAL:

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        with open(
            csv_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                timestamp,
                car_count,
                bus_count,
                bike_count,
                person_count,
                total_vehicles,
                unique_vehicle_count,
                traffic_status
            ])

        last_csv_update = current_time

        print(
            f"CSV Updated: {timestamp} | "
            f"Cars={car_count}, "
            f"Buses={bus_count}, "
            f"Bikes={bike_count}, "
            f"Total={total_vehicles}, "
            f"Status={traffic_status}"
        )


    # =====================================================
    # DRAW DETECTION BOXES
    # =====================================================

    frame = results[0].plot()


    # =====================================================
    # DISPLAY COUNTS
    # =====================================================

    cv2.putText(
        frame,
        f"Cars: {car_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"Buses: {bus_count}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"Bikes: {bike_count}",
        (20, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"Persons: {person_count}",
        (20, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"Total Vehicles: {total_vehicles}",
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )


    cv2.putText(
        frame,
        f"Unique Vehicles: {unique_vehicle_count}",
        (20, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"Traffic Status: {traffic_status}",
        (20, 220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )


    # =====================================================
    # SHOW VIDEO
    # =====================================================

    cv2.imshow(
        "Traffic Detection and Tracking",
        frame
    )


    # =====================================================
    # PRESS Q TO QUIT
    # =====================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# =========================================================
# RELEASE RESOURCES
# =========================================================

video.release()

cv2.destroyAllWindows()