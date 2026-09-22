import streamlit as st
import json
import os
import pandas as pd
import time
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

st.caption(
    "YOLO + ByteTrack Real-Time Traffic Monitoring System"
)


# =========================================================
# READ TRAFFIC DATA
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
            "traffic_status": "LOW",
            "traffic_reason": "",
            "alert_message": "",
            "driver_alert_active": False,
            "accident_detected": False,
            "accident_message": "No Accident Detected"

        }


    try:

        with open(
            file_path,
            "r"
        ) as file:

            return json.load(file)


    except Exception as e:

        st.error(
            f"Unable to read traffic_data.json: {e}"
        )

        return {}


# =========================================================
# READ TRAFFIC HISTORY
# =========================================================

def read_traffic_history():

    csv_file = "traffic_counts.csv"

    if not os.path.exists(csv_file):

        return pd.DataFrame()


    try:

        return pd.read_csv(csv_file)


    except Exception as e:

        st.error(
            f"Unable to read traffic_counts.csv: {e}"
        )

        return pd.DataFrame()


# =========================================================
# READ ACCIDENT DATA
# =========================================================

def read_accident_data():

    file_path = "accident_data.json"

    if not os.path.exists(file_path):

        return {

            "accident_detected": False,

            "alert_message":
                "No Accident Detected",

            "time": ""

        }


    try:

        with open(
            file_path,
            "r"
        ) as file:

            return json.load(file)


    except Exception:

        return {

            "accident_detected": False,

            "alert_message":
                "No Accident Detected",

            "time": ""

        }


# =========================================================
# REFRESH CONTROL
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

        st.success(
            "✅ Dashboard refreshed successfully!"
        )

        time.sleep(0.5)

        st.rerun()


# =========================================================
# LOAD CURRENT DATA
# =========================================================

data = read_traffic_data()


cars = data.get(
    "cars",
    0
)

buses = data.get(
    "buses",
    0
)

bikes = data.get(
    "bikes",
    0
)

persons = data.get(
    "persons",
    0
)

total = data.get(
    "total",
    0
)

unique = data.get(
    "unique",
    0
)

traffic_status = data.get(
    "traffic_status",
    "LOW"
)

traffic_reason = data.get(
    "traffic_reason",
    ""
)

alert_message = data.get(
    "alert_message",
    ""
)

driver_alert_active = data.get(
    "driver_alert_active",
    False
)


# =========================================================
# LIVE TRAFFIC COUNTS
# =========================================================

st.subheader("🚗 Live Traffic Counts")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🚗 Cars",
        cars
    )


with col2:

    st.metric(
        "🚌 Buses",
        buses
    )


with col3:

    st.metric(
        "🏍️ Bikes",
        bikes
    )


with col4:

    st.metric(
        "👤 Persons",
        persons
    )


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

    st.success(
        "🟢 LOW TRAFFIC"
    )


elif traffic_status == "MEDIUM":

    st.warning(
        "🟡 MEDIUM TRAFFIC"
    )


elif traffic_status == "HIGH":

    st.error(
        "🔴 HIGH TRAFFIC"
    )


else:

    st.info(
        f"Traffic Status: {traffic_status}"
    )


# =========================================================
# TRAFFIC REASON
# =========================================================

if traffic_reason:

    st.info(
        f"💡 **Why?** {traffic_reason}"
    )


# =========================================================
# DRIVER TRAFFIC ALERT
# =========================================================

st.subheader("🔔 Driver Traffic Alert")


if driver_alert_active:

    st.error(
        "🚨 HIGH TRAFFIC AHEAD"
    )

    st.warning(
        alert_message
    )

else:

    st.success(
        "✅ No driver traffic alert"
    )


# =========================================================
# ACCIDENT STATUS
# =========================================================

st.subheader("⚠️ Accident Status")


accident_data = read_accident_data()


accident_detected = accident_data.get(
    "accident_detected",
    False
)

accident_message = accident_data.get(
    "alert_message",
    "No Accident Detected"
)

accident_time = accident_data.get(
    "time",
    ""
)


if accident_detected:

    st.error(
        "🚨 POSSIBLE ACCIDENT DETECTED"
    )

    st.warning(
        accident_message
    )

    if accident_time:

        st.write(
            f"🕒 Detection Time: **{accident_time}**"
        )


else:

    st.success(
        "✅ No Possible Accident Detected"
    )


# =========================================================
# ACCIDENT HISTORY
# =========================================================

st.subheader("📋 Accident History")


accident_history_file = "accident_history.csv"


if os.path.exists(
    accident_history_file
):

    try:

        accident_history = pd.read_csv(
            accident_history_file
        )


        if not accident_history.empty:

            st.dataframe(
                accident_history,
                use_container_width=True
            )

        else:

            st.info(
                "No accident history available."
            )


    except Exception as e:

        st.error(
            f"Unable to read accident history: {e}"
        )


else:

    st.info(
        "No accident history file available yet."
    )


# =========================================================
# TRAFFIC HISTORY
# =========================================================

st.subheader("📈 Traffic History")


history = read_traffic_history()


if not history.empty:


    # =====================================================
    # VEHICLE COUNT CHART
    # =====================================================

    st.write(
        "### 🚗 Vehicle Count Over Time"
    )


    chart_data = history.set_index(
        "Time"
    )[
        [
            "Cars",
            "Buses",
            "Bikes"
        ]
    ]


    st.line_chart(
        chart_data
    )


    # =====================================================
    # TOTAL VEHICLES
    # =====================================================

    st.write(
        "### 📊 Total Vehicles Over Time"
    )


    total_chart = history.set_index(
        "Time"
    )[
        [
            "Total"
        ]
    ]


    st.line_chart(
        total_chart
    )


    # =====================================================
    # TRAFFIC HISTORY TABLE
    # =====================================================

    st.write(
        "### 📋 Traffic History Records"
    )


    st.dataframe(
        history,
        use_container_width=True
    )


else:

    st.info(
        "📄 No traffic history available yet."
    )


# =========================================================
# TRAFFIC ANALYTICS
# =========================================================

st.subheader("📊 Traffic Analytics")


if not history.empty:


    # =====================================================
    # AVERAGE
    # =====================================================

    average_vehicles = history[
        "Total"
    ].mean()


    # =====================================================
    # PEAK
    # =====================================================

    peak_vehicles = history[
        "Total"
    ].max()


    peak_row = history.loc[
        history[
            "Total"
        ].idxmax()
    ]


    peak_time = peak_row[
        "Time"
    ]


    # =====================================================
    # MOST COMMON VEHICLE
    # =====================================================

    vehicle_totals = {

        "Cars":
            history[
                "Cars"
            ].sum(),

        "Buses":
            history[
                "Buses"
            ].sum(),

        "Bikes":
            history[
                "Bikes"
            ].sum()

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

    st.write(
        "### 🚦 Traffic Status Analysis"
    )


    status_counts = history[
        "Traffic_Status"
    ].value_counts()


    st.bar_chart(
        status_counts
    )


    # =====================================================
    # VEHICLE DISTRIBUTION
    # =====================================================

    st.write(
        "### 🚗 Vehicle Distribution"
    )


    vehicle_chart = pd.DataFrame({

        "Vehicle Type": [
            "Cars",
            "Buses",
            "Bikes"
        ],

        "Count": [

            history[
                "Cars"
            ].sum(),

            history[
                "Buses"
            ].sum(),

            history[
                "Bikes"
            ].sum()

        ]

    })


    st.bar_chart(
        vehicle_chart.set_index(
            "Vehicle Type"
        )
    )


    # =====================================================
    # PEAK RECORDS
    # =====================================================

    st.write(
        "### 🔥 Peak Traffic Records"
    )


    peak_records = history.sort_values(
        by="Total",
        ascending=False
    ).head(5)


    st.dataframe(
        peak_records,
        use_container_width=True
    )


    # =====================================================
    # STATUS SUMMARY
    # =====================================================

    st.write(
        "### 🚦 Traffic Status Summary"
    )


    low_count = (
        history[
            "Traffic_Status"
        ] == "LOW"
    ).sum()


    medium_count = (
        history[
            "Traffic_Status"
        ] == "MEDIUM"
    ).sum()


    high_count = (
        history[
            "Traffic_Status"
        ] == "HIGH"
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
    # TOTAL VEHICLE COUNTS
    # =====================================================

    st.write(
        "### 🚘 Total Detected Vehicles"
    )


    total_cars = int(
        history[
            "Cars"
        ].sum()
    )


    total_buses = int(
        history[
            "Buses"
        ].sum()
    )


    total_bikes = int(
        history[
            "Bikes"
        ].sum()
    )


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
# ALERT HISTORY
# =========================================================

st.subheader("🔔 Traffic Alert History")


if os.path.exists(
    "alert_history.csv"
):

    try:

        alert_history = pd.read_csv(
            "alert_history.csv"
        )


        if not alert_history.empty:

            st.dataframe(
                alert_history,
                use_container_width=True
            )

        else:

            st.info(
                "No traffic alerts recorded yet."
            )


    except Exception as e:

        st.error(
            f"Unable to read alert history: {e}"
        )


else:

    st.info(
        "No traffic alert history available yet."
    )


# =========================================================
# LAST UPDATE
# =========================================================

st.subheader("🕒 Dashboard Information")


if os.path.exists(
    "traffic_data.json"
):

    modified_time = os.path.getmtime(
        "traffic_data.json"
    )


    update_time = datetime.fromtimestamp(
        modified_time
    ).strftime(
        "%H:%M:%S"
    )


    st.write(
        f"📄 Last traffic data update: "
        f"**{update_time}**"
    )

else:

    st.write(
        "📄 traffic_data.json not found."
    )


# =========================================================
# TRAFFIC VIDEO
# =========================================================

st.subheader("🎥 Traffic Video")


video_path = os.path.join(
    "videos",
    "traffic.mp4"
)


if os.path.exists(
    video_path
):

    st.video(
        video_path
    )

else:

    st.error(
        f"❌ Traffic video not found: "
        f"{video_path}"
    )

