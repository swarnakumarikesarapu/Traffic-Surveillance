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
# UNIQUE TRACKED VEHICLE IDs
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

    with open(
        accident_file,
        "w"
    ) as file:

        json.dump(
            accident_data,
            file,
            indent=4
        )


save_accident_data()


# =========================================================
# ACCIDENT DETECTION FUNCTION
# =========================================================

def detect_accident(frame):

    # Placeholder for future accident detection model

    return False


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
# ALERT HISTORY CSV
# =========================================================

alert_history_file = "alert_history.csv"


if not os.path.exists(
    alert_history_file
):

    with open(
        alert_history_file,
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
# CSV UPDATE SETTINGS
# =========================================================

CSV_INTERVAL = 5

last_csv_update = time.time()


# =========================================================
# SUSTAINED HIGH TRAFFIC SETTINGS
# =========================================================

HIGH_REQUIRED_READINGS = 3

high_traffic_count = 0


# =========================================================
# ALERT COOLDOWN
# =========================================================

ALERT_COOLDOWN = 30

last_alert_time = 0


# =========================================================
# MAIN VIDEO LOOP
# =========================================================

while True:

    ret, frame = video.read()


    if not ret:

        print("Video ended")

        break


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
    # PROCESS OBJECTS
    # =====================================================

    if results[0].boxes.id is not None:

        ids = results[0].boxes.id.cpu().numpy()


        for box, track_id in zip(

            results[0].boxes,

            ids

        ):

            cls = int(box.cls[0])


            tracked_ids.add(
                int(track_id)
            )


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

    unique_vehicle_count = len(
        tracked_ids
    )


    # =====================================================
    # TRAFFIC LEVEL
    # =====================================================

    if total_vehicles <= 10:

        traffic_status = "LOW"

    elif total_vehicles <= 20:

        traffic_status = "MEDIUM"

    else:

        traffic_status = "HIGH"


    # =====================================================
    # SUSTAINED HIGH TRAFFIC
    # =====================================================

    if traffic_status == "HIGH":

        high_traffic_count += 1

    else:

        high_traffic_count = 0


    # =====================================================
    # TRAFFIC REASON
    # =====================================================

    if traffic_status == "LOW":

        traffic_reason = (

            f"Traffic is LOW. "

            f"Only {total_vehicles} "

            f"vehicles detected."

        )

    elif traffic_status == "MEDIUM":

        traffic_reason = (

            f"Traffic is MEDIUM. "

            f"{total_vehicles} "

            f"vehicles detected."

        )

    else:

        traffic_reason = (

            f"Traffic is HIGH. "

            f"{total_vehicles} vehicles "

            f"detected, which is above "

            f"the high-traffic threshold."

        )


    # =====================================================
    # DRIVER ALERT
    # =====================================================

    current_time = time.time()

    driver_alert_active = False

    alert_message = ""


    if (

        high_traffic_count

        >= HIGH_REQUIRED_READINGS

    ):

        driver_alert_active = True


        alert_message = (

            "High traffic ahead. "

            "Please consider an "

            "alternative route."

        )


        # =================================================
        # ALERT COOLDOWN
        # =================================================

        if (

            current_time - last_alert_time

            >= ALERT_COOLDOWN

        ):

            alert_time = datetime.now().strftime(
                "%H:%M:%S"
            )


            # =============================================
            # PRINT ALERT
            # =============================================

            print()

            print(
                "======================================"
            )

            print(
                "🔔 DRIVER TRAFFIC ALERT"
            )

            print(
                alert_message
            )

            print(
                "======================================"
            )

            print()


            # =============================================
            # SAVE ALERT HISTORY
            # =============================================

            with open(

                alert_history_file,

                "a",

                newline=""

            ) as file:

                writer = csv.writer(file)


                writer.writerow([

                    alert_time,

                    traffic_status,

                    total_vehicles,

                    alert_message

                ])


            print(
                f"📝 Alert saved: {alert_time}"
            )


            last_alert_time = current_time


    # =====================================================
    # SAVE JSON DATA
    # =====================================================

    data = {

        "cars": car_count,

        "buses": bus_count,

        "bikes": bike_count,

        "persons": person_count,

        "total": total_vehicles,

        "unique": unique_vehicle_count,

        "traffic_status": traffic_status,

        "traffic_reason": traffic_reason,

        "alert_message": alert_message,

        "high_traffic_readings":
            high_traffic_count,

        "required_high_readings":
            HIGH_REQUIRED_READINGS,

        "driver_alert_active":
            driver_alert_active

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
    # TRAFFIC HISTORY CSV
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


        if traffic_status == "HIGH":

            print(

                f"⚠️ HIGH traffic reading: "

                f"{high_traffic_count}/"

                f"{HIGH_REQUIRED_READINGS}"

            )


    # =====================================================
    # DRAW DETECTIONS
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
    # HIGH TRAFFIC PROGRESS
    # =====================================================

    if traffic_status == "HIGH":

        cv2.putText(

            frame,

            f"High Traffic: "

            f"{high_traffic_count}/"

            f"{HIGH_REQUIRED_READINGS}",

            (20, 250),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 0, 255),

            2

        )


    # =====================================================
    # DRIVER ALERT ON VIDEO
    # =====================================================

    if driver_alert_active:

        cv2.putText(

            frame,

            "ALERT: HIGH TRAFFIC AHEAD!",

            (20, 280),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.75,

            (0, 0, 255),

            2

        )


        cv2.putText(

            frame,

            "Consider an alternative route.",

            (20, 310),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

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
    # QUIT
    # =====================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# =========================================================
# RELEASE
# =========================================================

video.release()

cv2.destroyAllWindows()

