import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Traffic Surveillance Dashboard",
    page_icon="🚦",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🚦 Traffic Surveillance Dashboard")
st.caption("Real-Time Traffic Monitoring System")

# =========================================================
# READ JSON DATA
# =========================================================

def read_traffic_data():

    file_path = "traffic_data.json"

    if not os.path.exists(file_path):
        return {
            "cars": 0,
            "buses": 0,
            "bikes": 0,
            "persons": 0,
            "total": 0,
            "unique": 0,
            "traffic_status": "LOW"
        }

    try:

        with open(file_path, "r") as file:
            return json.load(file)

    except Exception as e:

        st.error(f"Unable to read traffic_data.json: {e}")

        return {
            "cars": 0,
            "buses": 0,
            "bikes": 0,
            "persons": 0,
            "total": 0,
            "unique": 0,
            "traffic_status": "LOW"
        }


# =========================================================
# READ CSV HISTORY
# =========================================================

def read_traffic_history():

    csv_file = "traffic_counts.csv"

    if not os.path.exists(csv_file):
        return pd.DataFrame()

    try:

        df = pd.read_csv(csv_file)

        return df

    except Exception as e:

        st.error(f"Unable to read traffic_counts.csv: {e}")

        return pd.DataFrame()


# =========================================================
# REFRESH BUTTON
# =========================================================

st.subheader("🔄 Dashboard Control")

col1, col2 = st.columns([1, 4])

with col1:

    refresh = st.button(
        "🔄 Refresh Data",
        key="refresh_data",
        use_container_width=True
    )

with col2:

    if refresh:
        st.success("✅ Dashboard refreshed successfully!")


# =========================================================
# LOAD DATA
# =========================================================

data = read_traffic_data()

cars = data.get("cars", 0)
buses = data.get("buses", 0)
bikes = data.get("bikes", 0)
persons = data.get("persons", 0)

total = data.get("total", 0)
unique = data.get("unique", 0)

traffic_status = data.get(
    "traffic_status",
    "LOW"
)


# =========================================================
# LIVE TRAFFIC COUNTS
# =========================================================

st.subheader("🚗 Live Traffic Counts")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🚗 Cars", cars)

with col2:
    st.metric("🚌 Buses", buses)

with col3:
    st.metric("🏍️ Bikes", bikes)

with col4:
    st.metric("👤 Persons", persons)


# =========================================================
# VEHICLE SUMMARY
# =========================================================

st.subheader("📊 Vehicle Summary")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🚘 Total Vehicles",
        total
    )

with col2:

    st.metric(
        "🔢 Unique Vehicles",
        unique
    )


# =========================================================
# TRAFFIC STATUS
# =========================================================

st.subheader("🚦 Traffic Status")

if traffic_status == "LOW":

    st.success("🟢 LOW TRAFFIC")

elif traffic_status == "MEDIUM":

    st.warning("🟡 MEDIUM TRAFFIC")

elif traffic_status == "HIGH":

    st.error("🔴 HIGH TRAFFIC")

else:

    st.info(f"Traffic Status: {traffic_status}")


# =========================================================
# ACCIDENT STATUS
# =========================================================

st.subheader("⚠️ Accident Status")


def read_accident_data():

    file_path = "accident_data.json"

    if not os.path.exists(file_path):

        return {
            "accident_detected": False,
            "alert_message": "No Accident Detected",
            "time": ""
        }

    try:

        with open(file_path, "r") as file:
            return json.load(file)

    except Exception as e:

        st.error(
            f"Unable to read accident_data.json: {e}"
        )

        return {
            "accident_detected": False,
            "alert_message": "No Accident Detected",
            "time": ""
        }


accident_data = read_accident_data()

accident_detected = accident_data.get(
    "accident_detected",
    False
)

alert_message = accident_data.get(
    "alert_message",
    "No Accident Detected"
)

accident_time = accident_data.get(
    "time",
    ""
)


if accident_detected:

    st.error(
        f"🚨 ACCIDENT DETECTED\n\n"
        f"{alert_message}"
    )

    if accident_time:

        st.write(
            f"🕒 Detection Time: **{accident_time}**"
        )

else:

    st.success(
        "✅ No Accident Detected"
    )




# =========================================================
# DAY 8 - TRAFFIC HISTORY
# =========================================================

st.subheader("📈 Traffic History")

history = read_traffic_history()

if not history.empty:

    # -----------------------------------------------------
    # TRAFFIC TREND CHART
    # -----------------------------------------------------

    st.write("### 🚗 Vehicle Count Over Time")

    chart_data = history.set_index("Time")[
        ["Cars", "Buses", "Bikes"]
    ]

    st.line_chart(chart_data)


    # -----------------------------------------------------
    # TOTAL VEHICLES CHART
    # -----------------------------------------------------

    st.write("### 📊 Total Vehicles Over Time")

    total_chart = history.set_index("Time")[
        ["Total"]
    ]

    st.line_chart(total_chart)


    # -----------------------------------------------------
    # HISTORY TABLE
    # -----------------------------------------------------

    st.write("### 📋 Traffic History Records")

    st.dataframe(
        history,
        use_container_width=True
    )

else:

    st.info(
        "📄 No traffic history available yet. "
        "Run video_detection.py to generate traffic data."
    )
# =========================================================
# DAY 9 - TRAFFIC ANALYTICS
# =========================================================

st.subheader("📊 Traffic Analytics")

history = read_traffic_history()

if not history.empty:

    # =====================================================
    # AVERAGE VEHICLES
    # =====================================================

    average_vehicles = history["Total"].mean()


    # =====================================================
    # PEAK TRAFFIC
    # =====================================================

    peak_vehicles = history["Total"].max()

    peak_row = history.loc[
        history["Total"].idxmax()
    ]

    peak_time = peak_row["Time"]


    # =====================================================
    # MOST COMMON VEHICLE
    # =====================================================

    vehicle_totals = {
        "Cars": history["Cars"].sum(),
        "Buses": history["Buses"].sum(),
        "Bikes": history["Bikes"].sum()
    }

    most_common_vehicle = max(
        vehicle_totals,
        key=vehicle_totals.get
    )


    # =====================================================
    # ANALYTICS METRICS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📊 Average Vehicles",
            f"{average_vehicles:.1f}"
        )

    with col2:

        st.metric(
            "🔥 Peak Vehicles",
            int(peak_vehicles)
        )

    with col3:

        st.metric(
            "🕒 Peak Time",
            peak_time
        )

    with col4:

        st.metric(
            "🚗 Most Common",
            most_common_vehicle
        )


    # =====================================================
    # TRAFFIC STATUS ANALYSIS
    # =====================================================

    st.write("### 🚦 Traffic Status Analysis")

    status_counts = history[
        "Traffic_Status"
    ].value_counts()

    st.bar_chart(status_counts)


    # =====================================================
    # VEHICLE DISTRIBUTION
    # =====================================================

    st.write("### 🚗 Vehicle Distribution")

    vehicle_chart = pd.DataFrame(
        {
            "Vehicle Type": [
                "Cars",
                "Buses",
                "Bikes"
            ],
            "Count": [
                history["Cars"].sum(),
                history["Buses"].sum(),
                history["Bikes"].sum()
            ]
        }
    )

    st.bar_chart(
        vehicle_chart.set_index("Vehicle Type")
    )

    # =====================================================
    # PEAK TRAFFIC RECORDS
    # =====================================================

    st.write("### 🔥 Peak Traffic Records")

    peak_records = history.sort_values(
        by="Total",
        ascending=False
    ).head(5)

    st.dataframe(
        peak_records,
        use_container_width=True
    )

    # =====================================================
    # TRAFFIC STATUS SUMMARY
    # =====================================================

    st.write("### 🚦 Traffic Status Summary")

    low_count = (
        history["Traffic_Status"] == "LOW"
    ).sum()

    medium_count = (
        history["Traffic_Status"] == "MEDIUM"
    ).sum()

    high_count = (
        history["Traffic_Status"] == "HIGH"
    ).sum()


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🟢 LOW Records",
            low_count
        )

    with col2:

        st.metric(
            "🟡 MEDIUM Records",
            medium_count
        )

    with col3:

        st.metric(
            "🔴 HIGH Records",
            high_count
        )

    # =====================================================
    # TRAFFIC TREND
    # =====================================================

    st.write("### 📈 Traffic Trend")

    trend_data = history.set_index("Time")[["Total"]]

    st.line_chart(
        trend_data
    )

    # =====================================================
    # TOTAL VEHICLE TYPE COUNTS
    # =====================================================

    st.write("### 🚘 Total Detected Vehicles")

    total_cars = int(history["Cars"].sum())
    total_buses = int(history["Buses"].sum())
    total_bikes = int(history["Bikes"].sum())

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🚗 Total Cars",
            total_cars
        )

    with col2:
        st.metric(
            "🚌 Total Buses",
            total_buses
        )

    with col3:
        st.metric(
            "🏍️ Total Bikes",
            total_bikes
        )

else:

    st.info(
        "📄 No historical traffic data available."
    )

# =========================================================
# LAST UPDATE INFORMATION
# =========================================================

st.subheader("🕒 Dashboard Information")

if os.path.exists("traffic_data.json"):

    modified_time = os.path.getmtime(
        "traffic_data.json"
    )

    update_time = datetime.fromtimestamp(
        modified_time
    ).strftime("%H:%M:%S")

    st.write(
        f"📄 Last traffic data update: **{update_time}**"
    )

else:

    st.write(
        "📄 traffic_data.json not found."
    )