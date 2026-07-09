import time
import datetime
import firebase_admin
from firebase_admin import credentials, db

import gspread
from google.oauth2.service_account import Credentials

# ==========================================================
# CONFIGURATION
# ==========================================================

FIREBASE_CREDENTIALS = "serviceAccountKey.json"

DATABASE_URL = "https://crop-protection-6f8ca-default-rtdb.asia-southeast1.firebasedatabase.app/"

GOOGLE_CREDENTIALS = "google_sheets_cred.json"

SPREADSHEET = "Crop Predator Data"

WORKSHEET = "Data"

CHECK_INTERVAL = 2

# ==========================================================
# FIREBASE
# ==========================================================

cred = credentials.Certificate(FIREBASE_CREDENTIALS)

firebase_admin.initialize_app(
    cred,
    {"databaseURL": DATABASE_URL}
)

# ==========================================================
# GOOGLE SHEETS
# ==========================================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS,
    scopes=scope
)

client = gspread.authorize(creds)

SPREADSHEET_ID = "1BwgR26GuGRVk_bsDtAft1yhdXLx8uqj-poOKWzGO7a8"

sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Data")

# ==========================================================
# HEADER
# ==========================================================

headers = [

    "Logged Time",

    "Animal",

    "Confidence",

    "Action",

    "Detection Time",

    "Temperature",

    "Humidity",

    "Soil Moisture",

    "Gas Concentration",

    "Distance",

    "Motion"

]

if sheet.cell(1, 1).value is None:
    sheet.append_row(headers)

# ==========================================================
# FUNCTIONS
# ==========================================================

def get_latest_prediction():

    latest = db.reference("crop_predator/latest").get()
    sensors = db.reference("crop_predator/sensors").get()

    if latest is None:
        latest = {}

    if sensors is None:
        sensors = {}

    return {

        "animal": latest.get("class", ""),

        "confidence": latest.get("confidence", ""),

        "action": latest.get("action", ""),

        "detection_time": latest.get("time", ""),

        "temperature": sensors.get("Temperature", ""),

        "humidity": sensors.get("Humidity", ""),

        "soil": sensors.get("Soil_Moisture", ""),

        "gas": sensors.get("Gas_Concentration", ""),

        "distance": sensors.get("Distance", ""),

        "motion": sensors.get("Motion", "")

    }

# ==========================================================
# MAIN
# ==========================================================

print("=" * 60)
print("Crop Predator Detection Logger")
print("=" * 60)

last_detection_time = None

while True:

    try:

        data = get_latest_prediction()

        detection_time = data["detection_time"]

        if detection_time != "" and detection_time != last_detection_time:

            logged_time = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            row = [

                logged_time,

                data["animal"],

                data["confidence"],

                data["action"],

                data["detection_time"],

                data["temperature"],

                data["humidity"],

                data["soil"],

                data["gas"],

                data["distance"],

                data["motion"]

            ]

            sheet.append_row(
                row,
                value_input_option="USER_ENTERED"
            )

            print("\nNew Detection Logged")
            print("--------------------------------")

            for k, v in data.items():
                print(f"{k:20}: {v}")

            last_detection_time = detection_time

        time.sleep(CHECK_INTERVAL)

    except Exception as e:

        print("Error:", e)

        time.sleep(5)