from ultralytics import YOLO
import cv2
from collections import defaultdict
import csv

# Load YOLO model
model = YOLO("yolo11n.pt")

# Input video
video_path = "traffic.mp4"

# Open video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open traffic.mp4")
    exit()

# Store unique tracking IDs
counted_ids = defaultdict(set)

# COCO vehicle classes
vehicle_classes = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

frame_number = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_number += 1

    # Track objects
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    result = results[0]

    if result.boxes is not None and result.boxes.id is not None:

        track_ids = result.boxes.id.int().cpu().tolist()
        classes = result.boxes.cls.int().cpu().tolist()

        for track_id, class_id in zip(track_ids, classes):

            if class_id in vehicle_classes:
                vehicle_type = vehicle_classes[class_id]
                counted_ids[vehicle_type].add(track_id)

    if frame_number % 100 == 0:
        print(f"Processed {frame_number} frames...")

cap.release()

# Calculate counts
car_count = len(counted_ids["Car"])
motorcycle_count = len(counted_ids["Motorcycle"])
bus_count = len(counted_ids["Bus"])
truck_count = len(counted_ids["Truck"])

total_vehicles = (
    car_count
    + motorcycle_count
    + bus_count
    + truck_count
)

# Display results
print("\n========== TRAFFIC COUNT ==========")
print(f"Car: {car_count}")
print(f"Motorcycle: {motorcycle_count}")
print(f"Bus: {bus_count}")
print(f"Truck: {truck_count}")
print("-----------------------------------")
print(f"Total vehicles: {total_vehicles}")
print("===================================")

# Save results to CSV
with open("traffic_counts.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow(["Vehicle Type", "Count"])

    writer.writerow(["Car", car_count])
    writer.writerow(["Motorcycle", motorcycle_count])
    writer.writerow(["Bus", bus_count])
    writer.writerow(["Truck", truck_count])
    writer.writerow(["Total", total_vehicles])

print("\nTraffic data saved to traffic_counts.csv")