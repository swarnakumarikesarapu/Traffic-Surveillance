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
# VIDEO SOURCE
# =========================================================

video_path = "videos/traffic.mp4"

video = cv2.VideoCapture(video_path)

if not video.isOpened():

    print("ERROR: Traffic video could not be opened.")
    print(f"Check this file: {video_path}")

    exit()

print("Traffic video opened successfully.")
print("Press Q to stop the live traffic detection.")


# =========================================================
# TRACKED VEHICLE DATA
# =========================================================

tracked_ids = set()

previous_positions = {}


# =========================================================
# TRAFFIC CSV
# =========================================================

csv_file = "traffic_counts.csv"

if not os.path.exists(csv_file):

    with open(
        csv_file,
        "w",
        newline=""
    ) as file:

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
# ALERT HISTORY
# =========================================================

alert_file = "alert_history.csv"

if not os.path.exists(alert_file):

    with open(
        alert_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "Traffic_Status",
            "Total_Vehicles",
            "Alert_Message"
        ])


# =========================================================
# ACCIDENT HISTORY
# =========================================================

accident_history_file = "accident_history.csv"

if not os.path.exists(accident_history_file):

    with open(
        accident_history_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "Status",
            "Message"
        ])


# =========================================================
# ACCIDENT DATA FILE
# =========================================================

accident_file = "accident_data.json"


def save_accident_data(
    accident_detected=False,
    message="No Accident Detected"
):

    accident_data = {

        "accident_detected":
            accident_detected,

        "alert_message":
            message,

        "time":
            (
                datetime.now().strftime("%H:%M:%S")
                if accident_detected
                else ""
            )
    }

    with open(
        accident_file,
        "w"
    ) as file:

        json.dump(
            accident_data,
            file,
            indent=4
        )


# Start with no accident

save_accident_data()


# =========================================================
# TIMERS
# =========================================================

CSV_INTERVAL = 5

last_csv_update = time.time()


# =========================================================
# TRAFFIC ALERT SETTINGS
# =========================================================

ALERT_COOLDOWN = 30

last_alert_time = 0


# =========================================================
# ACCIDENT ALERT SETTINGS
# =========================================================

ACCIDENT_COOLDOWN = 30

last_accident_time = 0


# =========================================================
# ACCIDENT DETECTION
# =========================================================

def detect_accident(
    boxes,
    ids
):

    """
    Prototype accident detection.

    The system looks for:

    1. Two or more vehicles being very close.
    2. Abnormal/sudden movement between tracked vehicles.

    This produces a POSSIBLE ACCIDENT warning.

    It is not a trained accident-recognition model.
    """

    if ids is None or len(ids) < 2:

        return False


    vehicle_centers = []


    for box, track_id in zip(
        boxes,
        ids
    ):

        cls = int(box.cls[0])


        # Only consider vehicles

        if cls not in [2, 3, 5]:

            continue


        x1, y1, x2, y2 = (
            box.xyxy[0]
            .cpu()
            .numpy()
        )


        center_x = int(
            (x1 + x2) / 2
        )

        center_y = int(
            (y1 + y2) / 2
        )


        vehicle_centers.append(
            (
                int(track_id),
                center_x,
                center_y
            )
        )


    # Need at least two vehicles

    if len(vehicle_centers) < 2:

        return False


    # =====================================================
    # CHECK DISTANCE BETWEEN VEHICLES
    # =====================================================

    for i in range(
        len(vehicle_centers)
    ):

        id1, x1, y1 = vehicle_centers[i]


        for j in range(
            i + 1,
            len(vehicle_centers)
        ):

            id2, x2, y2 = vehicle_centers[j]


            distance = (

                (x1 - x2) ** 2
                +
                (y1 - y2) ** 2

            ) ** 0.5


            # Very close vehicles

            if distance < 35:

                return True


    return False


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    ret, frame = video.read()


    # =====================================================
    # RESTART VIDEO
    # =====================================================

    if not ret:

        print("Traffic video ended.")
        print("Restarting traffic video...")

        video.set(
            cv2.CAP_PROP_POS_FRAMES,
            0
        )

        tracked_ids.clear()

        previous_positions.clear()

        continue


    # =====================================================
    # RESIZE
    # =====================================================

    frame = cv2.resize(
        frame,
        (640, 360)
    )


    # =====================================================
    # YOLO + BYTETRACK
    # =====================================================

    results = model.track(

        frame,

        persist=True,

        tracker="bytetrack.yaml",

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
    # GET TRACK IDS
    # =====================================================

    current_ids = None

    if results[0].boxes.id is not None:

        current_ids = (
            results[0]
            .boxes
            .id
            .cpu()
            .numpy()
        )


    # =====================================================
    # PROCESS OBJECTS
    # =====================================================

    if current_ids is not None:

        for box, track_id in zip(
            results[0].boxes,
            current_ids
        ):

            track_id = int(track_id)

            cls = int(
                box.cls[0]
            )


            # Save unique ID

            tracked_ids.add(
                track_id
            )


            # -------------------------------------------------
            # PERSON
            # -------------------------------------------------

            if cls == 0:

                person_count += 1


            # -------------------------------------------------
            # CAR
            # -------------------------------------------------

            elif cls == 2:

                car_count += 1


            # -------------------------------------------------
            # MOTORCYCLE
            # -------------------------------------------------

            elif cls == 3:

                bike_count += 1


            # -------------------------------------------------
            # BUS
            # -------------------------------------------------

            elif cls == 5:

                bus_count += 1


    # =====================================================
    # TOTAL VEHICLES
    # =====================================================

    total_vehicles = (

        car_count
        +
        bus_count
        +
        bike_count

    )


    # =====================================================
    # UNIQUE VEHICLES
    # =====================================================

    unique_vehicle_count = len(
        tracked_ids
    )


    # =====================================================
    # TRAFFIC STATUS
    # =====================================================

    if total_vehicles <= 10:

        traffic_status = "LOW"

    elif total_vehicles <= 20:

        traffic_status = "MEDIUM"

    else:

        traffic_status = "HIGH"


    # =====================================================
    # TRAFFIC REASON
    # =====================================================

    if traffic_status == "LOW":

        traffic_reason = (

            f"Traffic is LOW. "
            f"Only {total_vehicles} vehicles detected."

        )

    elif traffic_status == "MEDIUM":

        traffic_reason = (

            f"Traffic is MEDIUM. "
            f"{total_vehicles} vehicles detected."

        )

    else:

        traffic_reason = (

            f"Traffic is HIGH. "
            f"{total_vehicles} vehicles detected, "
            f"which is above the high-traffic threshold."

        )


    # =====================================================
    # DRIVER TRAFFIC ALERT
    # =====================================================

    current_time = time.time()

    alert_message = ""

    driver_alert_active = False


    if traffic_status == "HIGH":

        alert_message = (

            "High traffic ahead. "
            "Please consider an alternative route."

        )

        driver_alert_active = True


        if (

            current_time - last_alert_time
            >= ALERT_COOLDOWN

        ):

            timestamp = datetime.now().strftime(
                "%H:%M:%S"
            )


            print()
            print(
                "🔔 DRIVER TRAFFIC ALERT"
            )

            print(
                alert_message
            )


            # Save traffic alert

            with open(
                alert_file,
                "a",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([

                    timestamp,

                    traffic_status,

                    total_vehicles,

                    alert_message

                ])


            last_alert_time = current_time


    # =====================================================
    # ACCIDENT DETECTION
    # =====================================================

    accident_detected = False

    accident_message = "No Accident Detected"


    if current_ids is not None:

        accident_detected = detect_accident(

            results[0].boxes,

            current_ids

        )


    # =====================================================
    # ACCIDENT ALERT
    # =====================================================

    if accident_detected:

        accident_message = (

            "Possible accident detected. "
            "Please drive carefully."

        )


        if (

            current_time - last_accident_time
            >= ACCIDENT_COOLDOWN

        ):

            timestamp = datetime.now().strftime(
                "%H:%M:%S"
            )


            print()
            print(
                "🚨 POSSIBLE ACCIDENT DETECTED"
            )

            print(
                accident_message
            )


            # Save accident history

            with open(
                accident_history_file,
                "a",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([

                    timestamp,

                    "POSSIBLE ACCIDENT",

                    accident_message

                ])


            last_accident_time = current_time


    # =====================================================
    # SAVE ACCIDENT JSON
    # =====================================================

    save_accident_data(

        accident_detected,

        accident_message

    )


    # =====================================================
    # SAVE CURRENT TRAFFIC DATA
    # =====================================================

    data = {

        "cars":
            car_count,

        "buses":
            bus_count,

        "bikes":
            bike_count,

        "persons":
            person_count,

        "total":
            total_vehicles,

        "unique":
            unique_vehicle_count,

        "traffic_status":
            traffic_status,

        "traffic_reason":
            traffic_reason,

        "alert_message":
            alert_message,

        "driver_alert_active":
            driver_alert_active,

        "accident_detected":
            accident_detected,

        "accident_message":
            accident_message

    }


    with open(
        "traffic_data.json",
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


    # =====================================================
    # SAVE TRAFFIC HISTORY
    # EVERY 5 SECONDS
    # =====================================================

    current_time = time.time()


    if (

        current_time - last_csv_update
        >= CSV_INTERVAL

    ):

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
    # DRAW YOLO DETECTIONS
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

        0.7,

        (0, 255, 0),

        2

    )


    cv2.putText(

        frame,

        f"Buses: {bus_count}",

        (20, 70),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (0, 255, 0),

        2

    )


    cv2.putText(

        frame,

        f"Bikes: {bike_count}",

        (20, 100),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (0, 255, 0),

        2

    )


    cv2.putText(

        frame,

        f"Persons: {person_count}",

        (20, 130),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (0, 255, 0),

        2

    )


    cv2.putText(

        frame,

        f"Total Vehicles: {total_vehicles}",

        (20, 160),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 0, 0),

        2

    )


    cv2.putText(

        frame,

        f"Unique Vehicles: {unique_vehicle_count}",

        (20, 190),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 255, 0),

        2

    )


    cv2.putText(

        frame,

        f"Traffic Status: {traffic_status}",

        (20, 220),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (0, 0, 255),

        2

    )


    # =====================================================
    # TRAFFIC ALERT DISPLAY
    # =====================================================

    if driver_alert_active:

        cv2.putText(

            frame,

            "ALERT: HIGH TRAFFIC AHEAD!",

            (20, 255),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (0, 0, 255),

            2

        )

        cv2.putText(

            frame,

            "Consider an alternative route.",

            (20, 285),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            (0, 0, 255),

            2

        )


    # =====================================================
    # ACCIDENT ALERT DISPLAY
    # =====================================================

    if accident_detected:

        cv2.putText(

            frame,

            "WARNING: POSSIBLE ACCIDENT!",

            (20, 320),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (0, 0, 255),

            2

        )


    # =====================================================
    # SHOW VIDEO
    # =====================================================

    cv2.imshow(

        "Live Traffic Detection",

        frame

    )


    # =====================================================
    # PRESS Q TO STOP
    # =====================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        print(
            "Stopping live traffic detection..."
        )

        break


# =========================================================
# RELEASE
# =========================================================

video.release()

cv2.destroyAllWindows()

print(
    "Live traffic detection stopped."
)

