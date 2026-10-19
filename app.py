import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import urllib.request
import urllib.error
import json
import threading
import queue
import time
import webbrowser


# ============================================================
# SMARTBIN - WASTE COLLECTOR DESKTOP APPLICATION
# WI-FI VERSION
# ============================================================


# ============================================================
# ESP32 WI-FI SETTINGS
# ============================================================

ESP32_URL = "http://10.201.95.216/data"
# How often Python asks the ESP32 for new data
POLL_INTERVAL = 1.0


# ============================================================
# COLORS
# ============================================================

BG = "#F4F7FB"
CARD = "#FFFFFF"
BLUE = "#2563EB"
DARK = "#172033"
TEXT = "#263238"
GREY = "#718096"
GREEN = "#16A34A"
YELLOW = "#F59E0B"
RED = "#DC2626"


# ============================================================
# GLOBAL VARIABLES
# ============================================================

data_queue = queue.Queue()

wifi_running = False
wifi_thread = None

waste_level = 0
waste_distance = None
object_distance = None

latitude = None
longitude = None

gps_valid = False
lid_status = "CLOSED"

last_update = "--"

collected_override = False

dashboard_active = False


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()

window.title("SmartBin")
window.geometry("1000x650")
window.configure(bg=BG)

window.resizable(False, False)


# ============================================================
# DASHBOARD WIDGET VARIABLES
# ============================================================

connection_label = None

percentage_label = None
progress = None
status_label = None

sensor_value = None
lid_label = None
last_update_label = None

alert_label = None

gps_label = None
latitude_label = None
longitude_label = None
location_button = None


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login():

    global dashboard_active

    dashboard_active = False

    stop_wifi_thread()

    # Clear current screen

    for widget in window.winfo_children():
        widget.destroy()


    # --------------------------------------------------------
    # LOGIN FRAME
    # --------------------------------------------------------

    login_frame = tk.Frame(
        window,
        bg=BG
    )

    login_frame.pack(
        expand=True
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = tk.Label(
        login_frame,
        text="SMART BIN",
        font=("Arial", 30, "bold"),
        fg=BLUE,
        bg=BG
    )

    title.pack(
        pady=(20, 5)
    )


    # --------------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------------

    subtitle = tk.Label(
        login_frame,
        text="Smart Waste Management System",
        font=("Arial", 12),
        fg=GREY,
        bg=BG
    )

    subtitle.pack(
        pady=(0, 30)
    )


    # --------------------------------------------------------
    # LOGIN CARD
    # --------------------------------------------------------

    card = tk.Frame(
        login_frame,
        bg=CARD,
        width=380,
        height=300
    )

    card.pack()

    card.pack_propagate(False)


    # --------------------------------------------------------
    # LOGIN TITLE
    # --------------------------------------------------------

    tk.Label(
        card,
        text="Login",
        font=("Arial", 22, "bold"),
        fg=DARK,
        bg=CARD
    ).pack(
        pady=(25, 20)
    )


    # --------------------------------------------------------
    # USERNAME
    # --------------------------------------------------------

    tk.Label(
        card,
        text="Username",
        font=("Arial", 11, "bold"),
        fg=TEXT,
        bg=CARD
    ).pack(
        anchor="w",
        padx=40
    )


    username_entry = tk.Entry(
        card,
        font=("Arial", 12),
        width=28
    )

    username_entry.pack(
        padx=40,
        pady=(5, 15)
    )


    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    tk.Label(
        card,
        text="Password",
        font=("Arial", 11, "bold"),
        fg=TEXT,
        bg=CARD
    ).pack(
        anchor="w",
        padx=40
    )


    password_entry = tk.Entry(
        card,
        font=("Arial", 12),
        width=28,
        show="*"
    )

    password_entry.pack(
        padx=40,
        pady=(5, 20)
    )


    # --------------------------------------------------------
    # LOGIN FUNCTION
    # --------------------------------------------------------

    def login():

        username = username_entry.get()
        password = password_entry.get()

        if username == "admin" and password == "1234":

            show_dashboard()

        else:

            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )


    # --------------------------------------------------------
    # LOGIN BUTTON
    # --------------------------------------------------------

    login_button = tk.Button(
        card,
        text="LOGIN",
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg="white",
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        width=20,
        height=2,
        command=login
    )

    login_button.pack()


    # --------------------------------------------------------
    # ENTER KEY
    # --------------------------------------------------------

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )

    username_entry.focus()


# ============================================================
# GET DATA FROM ESP32
# ============================================================

def get_esp32_data():

    try:

        # Request data from ESP32

        with urllib.request.urlopen(
            ESP32_URL,
            timeout=2
        ) as response:

            # Read response

            raw_data = response.read().decode(
                "utf-8"
            )

            # Convert JSON to Python dictionary

            data = json.loads(
                raw_data
            )

            return data


    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        ConnectionError,
        json.JSONDecodeError,
        OSError
    ):

        return None


# ============================================================
# WI-FI BACKGROUND THREAD
# ============================================================

def wifi_reader():

    global wifi_running

    while wifi_running:

        # Ask ESP32 for current data

        data = get_esp32_data()


        if data is not None:

            data_queue.put(
                (
                    "connected",
                    data
                )
            )

        else:

            data_queue.put(
                (
                    "disconnected",
                    None
                )
            )


        # Wait before next request

        time.sleep(
            POLL_INTERVAL
        )


# ============================================================
# START WI-FI THREAD
# ============================================================

def start_wifi_thread():

    global wifi_running
    global wifi_thread

    if wifi_running:
        return


    wifi_running = True


    wifi_thread = threading.Thread(
        target=wifi_reader,
        daemon=True
    )

    wifi_thread.start()


# ============================================================
# STOP WI-FI THREAD
# ============================================================

def stop_wifi_thread():

    global wifi_running

    wifi_running = False


# ============================================================
# PROCESS WI-FI DATA
# ============================================================

def process_wifi_data():

    # Do not update dashboard if user is on login page

    if dashboard_active:

        while not data_queue.empty():

            try:

                data_type, data = data_queue.get_nowait()

            except queue.Empty:

                break


            # ------------------------------------------------
            # CONNECTED
            # ------------------------------------------------

            if data_type == "connected":

                update_from_esp32(data)


            # ------------------------------------------------
            # DISCONNECTED
            # ------------------------------------------------

            elif data_type == "disconnected":

                show_disconnected()


    # Check again after 100 ms

    window.after(
        100,
        process_wifi_data
    )


# ============================================================
# UPDATE DASHBOARD FROM ESP32
# ============================================================

def update_from_esp32(data):

    global waste_level
    global waste_distance
    global object_distance
    global latitude
    global longitude
    global gps_valid
    global lid_status
    global last_update
    global collected_override


    # ========================================================
    # CONNECTION
    # ========================================================

    connection_label.config(
        text="● ESP32 CONNECTED",
        fg=GREEN
    )


    # ========================================================
    # WASTE LEVEL
    # ========================================================

    value = data.get(
        "wasteLevel",
        0
    )


    try:

        waste_level = int(value)

    except (
        ValueError,
        TypeError
    ):

        waste_level = 0


    # Keep between 0 and 100

    waste_level = max(
        0,
        min(
            100,
            waste_level
        )
    )


    # New ESP32 reading means we should
    # remove the temporary collection override

    collected_override = False


    # ========================================================
    # WASTE DISTANCE
    # ========================================================

    value = data.get(
        "wasteDistance"
    )


    try:

        if value is not None:

            waste_distance = float(value)

        else:

            waste_distance = None

    except (
        ValueError,
        TypeError
    ):

        waste_distance = None


    # ========================================================
    # OBJECT DISTANCE
    # ========================================================

    value = data.get(
        "objectDistance"
    )


    try:

        if value is not None:

            object_distance = float(value)

        else:

            object_distance = None

    except (
        ValueError,
        TypeError
    ):

        object_distance = None


    # ========================================================
    # LID STATUS
    # ========================================================

    lid_status = data.get(
        "lidStatus",
        "CLOSED"
    )


    # ========================================================
    # GPS VALID
    # ========================================================

    gps_valid = data.get(
        "gpsValid",
        False
    )


    # ========================================================
    # LATITUDE
    # ========================================================

    value = data.get(
        "latitude"
    )


    try:

        if value is not None:

            latitude = float(value)

        else:

            latitude = None

    except (
        ValueError,
        TypeError
    ):

        latitude = None


    # ========================================================
    # LONGITUDE
    # ========================================================

    value = data.get(
        "longitude"
    )


    try:

        if value is not None:

            longitude = float(value)

        else:

            longitude = None

    except (
        ValueError,
        TypeError
    ):

        longitude = None


    # ========================================================
    # LAST UPDATED
    # ========================================================

    last_update = datetime.now().strftime(
        "%d-%m-%Y  %I:%M:%S %p"
    )


    # ========================================================
    # UPDATE ALL DASHBOARD ITEMS
    # ========================================================

    update_dashboard()

    update_lid_display()

    update_gps_display()


# ============================================================
# SHOW DISCONNECTED
# ============================================================

def show_disconnected():

    if connection_label is not None:

        connection_label.config(
            text="● ESP32 NOT CONNECTED",
            fg=RED
        )


# ============================================================
# UPDATE DASHBOARD
# ============================================================

def update_dashboard():

    if percentage_label is None:
        return


    # ========================================================
    # DISPLAY LEVEL
    # ========================================================

    if collected_override:

        display_level = 0

    else:

        display_level = waste_level


    # ========================================================
    # WASTE PERCENTAGE
    # ========================================================

    percentage_label.config(
        text=f"{display_level}%"
    )


    # ========================================================
    # PROGRESS BAR
    # ========================================================

    progress["value"] = display_level


    # ========================================================
    # WASTE SENSOR DISTANCE
    # ========================================================

    if waste_distance is None:

        sensor_value.config(
            text="No reading"
        )

    else:

        sensor_value.config(
            text=f"{waste_distance:.2f} cm"
        )


    # ========================================================
    # WASTE STATUS
    # ========================================================

    if display_level >= 80:

        status_label.config(
            text="FULL",
            fg=RED
        )

        alert_label.config(
            text="⚠ Bin is full. Collection required.",
            fg=RED
        )


    elif display_level >= 50:

        status_label.config(
            text="FILLING",
            fg=YELLOW
        )

        alert_label.config(
            text="● Bin is filling. Collection not required yet.",
            fg=YELLOW
        )


    else:

        status_label.config(
            text="EMPTY",
            fg=GREEN
        )

        alert_label.config(
            text="● Bin does not require collection.",
            fg=GREEN
        )


    # ========================================================
    # LAST UPDATED
    # ========================================================

    last_update_label.config(
        text=last_update
    )


# ============================================================
# UPDATE LID DISPLAY
# ============================================================

def update_lid_display():

    if lid_label is None:
        return


    if lid_status.upper() == "OPEN":

        lid_label.config(
            text="OPEN",
            fg=GREEN
        )


    else:

        lid_label.config(
            text="CLOSED",
            fg=GREY
        )


# ============================================================
# UPDATE GPS DISPLAY
# ============================================================

def update_gps_display():

    if gps_label is None:
        return


    # ========================================================
    # GPS NOT AVAILABLE
    # ========================================================

    if (
        not gps_valid
        or latitude is None
        or longitude is None
    ):

        gps_label.config(
            text="Waiting for GPS fix...",
            fg=YELLOW
        )


        latitude_label.config(
            text="Latitude: --"
        )


        longitude_label.config(
            text="Longitude: --"
        )


        location_button.config(
            state="disabled"
        )

        return


    # ========================================================
    # GPS AVAILABLE
    # ========================================================

    gps_label.config(
        text="GPS FIXED",
        fg=GREEN
    )


    latitude_label.config(
        text=f"Latitude: {latitude:.6f}"
    )


    longitude_label.config(
        text=f"Longitude: {longitude:.6f}"
    )


    location_button.config(
        state="normal"
    )


# ============================================================
# OPEN GPS LOCATION
# ============================================================

def open_location():

    if (
        latitude is None
        or longitude is None
    ):

        messagebox.showwarning(
            "GPS",
            "GPS location is not available yet."
        )

        return


    url = (
        "https://www.google.com/maps/search/"
        f"?api=1&query={latitude},{longitude}"
    )


    webbrowser.open(
        url
    )


# ============================================================
# MARK AS COLLECTED
# ============================================================

def mark_collected():

    global collected_override


    answer = messagebox.askyesno(
        "Mark as Collected",
        "Has the waste been collected?"
    )


    if answer:

        collected_override = True


        # ----------------------------------------------------
        # SHOW 0%
        # ----------------------------------------------------

        percentage_label.config(
            text="0%"
        )


        progress["value"] = 0


        # ----------------------------------------------------
        # SHOW EMPTY
        # ----------------------------------------------------

        status_label.config(
            text="EMPTY",
            fg=GREEN
        )


        # ----------------------------------------------------
        # SHOW SUCCESS ALERT
        # ----------------------------------------------------

        alert_label.config(
            text="● Waste collected successfully.",
            fg=GREEN
        )


        messagebox.showinfo(
            "Collection",
            "Bin marked as collected."
        )


# ============================================================
# LOGOUT
# ============================================================

def logout():

    answer = messagebox.askyesno(
        "Logout",
        "Do you want to logout?"
    )


    if answer:

        show_login()


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    global dashboard_active

    global connection_label

    global percentage_label
    global progress
    global status_label

    global sensor_value
    global lid_label
    global last_update_label

    global alert_label

    global gps_label
    global latitude_label
    global longitude_label
    global location_button


    dashboard_active = True


    # Clear login screen

    for widget in window.winfo_children():

        widget.destroy()


    # ========================================================
    # HEADER
    # ========================================================

    header = tk.Frame(
        window,
        bg=CARD,
        height=80
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(False)


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = tk.Label(
        header,
        text="SMART BIN",
        font=("Arial", 24, "bold"),
        fg=BLUE,
        bg=CARD
    )

    title.pack(
        side="left",
        padx=30
    )


    # --------------------------------------------------------
    # CONNECTION STATUS
    # --------------------------------------------------------

    connection_label = tk.Label(
        header,
        text="● CONNECTING...",
        font=("Arial", 11, "bold"),
        fg=YELLOW,
        bg=CARD
    )

    connection_label.pack(
        side="right",
        padx=30
    )


    # ========================================================
    # MAIN CONTENT
    # ========================================================

    main = tk.Frame(
        window,
        bg=BG
    )

    main.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=25
    )


    # ========================================================
    # BIN INFORMATION
    # ========================================================

    info_frame = tk.Frame(
        main,
        bg=CARD
    )

    info_frame.pack(
        fill="x",
        pady=(0, 20)
    )


    tk.Label(
        info_frame,
        text="BIN-001",
        font=("Arial", 20, "bold"),
        fg=DARK,
        bg=CARD
    ).pack(
        side="left",
        padx=20,
        pady=15
    )


    tk.Label(
        info_frame,
        text="General Waste",
        font=("Arial", 11),
        fg=GREY,
        bg=CARD
    ).pack(
        side="left",
        padx=10
    )


    # ========================================================
    # LEFT + RIGHT AREA
    # ========================================================

    content = tk.Frame(
        main,
        bg=BG
    )

    content.pack(
        fill="both",
        expand=True
    )


    # ========================================================
    # WASTE CARD
    # ========================================================

    waste_card = tk.Frame(
        content,
        bg=CARD
    )

    waste_card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 10)
    )


    # --------------------------------------------------------
    # WASTE LEVEL TITLE
    # --------------------------------------------------------

    tk.Label(
        waste_card,
        text="WASTE LEVEL",
        font=("Arial", 12, "bold"),
        fg=GREY,
        bg=CARD
    ).pack(
        pady=(25, 5)
    )


    # --------------------------------------------------------
    # PERCENTAGE
    # --------------------------------------------------------

    percentage_label = tk.Label(
        waste_card,
        text="0%",
        font=("Arial", 48, "bold"),
        fg=BLUE,
        bg=CARD
    )

    percentage_label.pack(
        pady=5
    )


    # --------------------------------------------------------
    # PROGRESS BAR
    # --------------------------------------------------------

    progress = ttk.Progressbar(
        waste_card,
        orient="horizontal",
        length=350,
        mode="determinate",
        maximum=100
    )

    progress.pack(
        pady=10
    )

    progress["value"] = 0


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_label = tk.Label(
        waste_card,
        text="EMPTY",
        font=("Arial", 18, "bold"),
        fg=GREEN,
        bg=CARD
    )

    status_label.pack(
        pady=10
    )


    # ========================================================
    # SENSOR INFORMATION
    # ========================================================

    sensor_frame = tk.Frame(
        waste_card,
        bg=BG
    )

    sensor_frame.pack(
        fill="x",
        padx=30,
        pady=15
    )


    tk.Label(
        sensor_frame,
        text="Waste Sensor Distance",
        font=("Arial", 10, "bold"),
        fg=GREY,
        bg=BG
    ).pack(
        side="left"
    )


    sensor_value = tk.Label(
        sensor_frame,
        text="No reading",
        font=("Arial", 11, "bold"),
        fg=DARK,
        bg=BG
    )

    sensor_value.pack(
        side="right"
    )


    # ========================================================
    # LID STATUS
    # ========================================================

    lid_frame = tk.Frame(
        waste_card,
        bg=BG
    )

    lid_frame.pack(
        fill="x",
        padx=30,
        pady=5
    )


    tk.Label(
        lid_frame,
        text="Lid Status",
        font=("Arial", 10, "bold"),
        fg=GREY,
        bg=BG
    ).pack(
        side="left"
    )


    lid_label = tk.Label(
        lid_frame,
        text="CLOSED",
        font=("Arial", 11, "bold"),
        fg=GREY,
        bg=BG
    )

    lid_label.pack(
        side="right"
    )


    # ========================================================
    # LAST UPDATED
    # ========================================================

    update_frame = tk.Frame(
        waste_card,
        bg=BG
    )

    update_frame.pack(
        fill="x",
        padx=30,
        pady=5
    )


    tk.Label(
        update_frame,
        text="Last Updated",
        font=("Arial", 10, "bold"),
        fg=GREY,
        bg=BG
    ).pack(
        side="left"
    )


    last_update_label = tk.Label(
        update_frame,
        text="--",
        font=("Arial", 10),
        fg=DARK,
        bg=BG
    )

    last_update_label.pack(
        side="right"
    )


    # ========================================================
    # RIGHT CARD
    # ========================================================

    right_card = tk.Frame(
        content,
        bg=CARD,
        width=350
    )

    right_card.pack(
        side="right",
        fill="both",
        padx=(10, 0)
    )

    right_card.pack_propagate(False)


    # ========================================================
    # ALERT
    # ========================================================

    tk.Label(
        right_card,
        text="ALERT",
        font=("Arial", 12, "bold"),
        fg=GREY,
        bg=CARD
    ).pack(
        pady=(25, 5)
    )


    alert_label = tk.Label(
        right_card,
        text="● Waiting for sensor data...",
        font=("Arial", 11, "bold"),
        fg=YELLOW,
        bg=CARD,
        wraplength=290
    )

    alert_label.pack(
        pady=15
    )


    # ========================================================
    # GPS LOCATION
    # ========================================================

    tk.Label(
        right_card,
        text="GPS LOCATION",
        font=("Arial", 12, "bold"),
        fg=GREY,
        bg=CARD
    ).pack(
        pady=(20, 5)
    )


    gps_label = tk.Label(
        right_card,
        text="Waiting for GPS fix...",
        font=("Arial", 10, "bold"),
        fg=YELLOW,
        bg=CARD
    )

    gps_label.pack(
        pady=5
    )


    # --------------------------------------------------------
    # LATITUDE
    # --------------------------------------------------------

    latitude_label = tk.Label(
        right_card,
        text="Latitude: --",
        font=("Arial", 10),
        fg=DARK,
        bg=CARD
    )

    latitude_label.pack(
        pady=2
    )


    # --------------------------------------------------------
    # LONGITUDE
    # --------------------------------------------------------

    longitude_label = tk.Label(
        right_card,
        text="Longitude: --",
        font=("Arial", 10),
        fg=DARK,
        bg=CARD
    )

    longitude_label.pack(
        pady=2
    )


    # ========================================================
    # OPEN LOCATION
    # ========================================================

    location_button = tk.Button(
        right_card,
        text="OPEN LOCATION",
        font=("Arial", 10, "bold"),
        bg=BLUE,
        fg="white",
        relief="flat",
        width=22,
        state="disabled",
        command=open_location
    )

    location_button.pack(
        pady=12
    )


    # ========================================================
    # MARK AS COLLECTED
    # ========================================================

    collect_button = tk.Button(
        right_card,
        text="MARK AS COLLECTED",
        font=("Arial", 10, "bold"),
        bg=GREEN,
        fg="white",
        relief="flat",
        width=22,
        height=2,
        command=mark_collected
    )

    collect_button.pack(
        pady=15
    )


    # ========================================================
    # LOGOUT
    # ========================================================

    logout_button = tk.Button(
        right_card,
        text="LOGOUT",
        font=("Arial", 10, "bold"),
        bg=RED,
        fg="white",
        relief="flat",
        width=22,
        command=logout
    )

    logout_button.pack(
        pady=5
    )


    # ========================================================
    # START WI-FI
    # ========================================================

    start_wifi_thread()


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application():

    global wifi_running

    wifi_running = False

    window.destroy()


# ============================================================
# WINDOW CLOSE EVENT
# ============================================================

window.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# START DATA PROCESSING
# ============================================================

window.after(
    100,
    process_wifi_data
)


# ============================================================
# START APPLICATION
# ============================================================

show_login()

window.mainloop()