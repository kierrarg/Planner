import tkinter as tk
from tkinter import simpledialog as tk_simpledialog
import calendar
import datetime
import logging
from pages.goog import create_calendar_service, create_event, delete_custom_event_by_title

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the desired logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Define the scopes you need for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Specify fixed redirect URI
REDIRECT_URI = 'http://localhost:8090/oauth2callback'

# Create a Google Calendar service
calendar_service = create_calendar_service('credentials.json', 'token files', 'calendar', 'v3', SCOPES, prefix='')

class CalendarPage(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(bg="#ADD8E6")
        self.current_month = 8  # Set the initial month (e.g., August)
        self.current_year = 2023  # Set the initial year
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="This is the Calendar Page")
        label.pack(fill="both", expand=True)

        # Frame to contain grid buttons
        calendar_frame = tk.Frame(self)
        calendar_frame.pack()

        # List of weekday labels
        weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        # Calculate the weekday index for the first day of the month
        first_day = calendar.weekday(self.current_year, self.current_month, 1)

        # Adjust weekday labels based on the calculated index
        adjusted_weekdays = weekdays[first_day:] + weekdays[:first_day]

        # Weekday labels at the top
        for col, weekday in enumerate(adjusted_weekdays):
            weekday_label = tk.Label(calendar_frame, text=weekday)
            weekday_label.grid(row=0, column=col)

        # Create a grid of buttons for each day of the month
        self.buttons = []  # Store buttons in a list
        for row in range(1, 7):  # Rows for calendar grid (up to 6 rows)
            button_row = []
            for col in range(7):  # Columns for days of the week
                day_button = tk.Button(calendar_frame, text="", width=3, height=1)
                day_button.grid(row=row, column=col, padx=5, pady=5)
                button_row.append(day_button)
                #bind dialog method to button
                # 'bind' method in tkinter to bind day button and trigger when mouse button 1 is clicked
                # lambda is anonymous unnamed function _ is placeholder
                day_button.bind("<Button-1>", lambda _, col=col, row=row: self.show_event_dialog(col, row))
            self.buttons.append(button_row)

        # Creating arrow frames
        arrow_frame = tk.Frame(self)
        arrow_frame.pack()

        # Arrows for month navigation
        left_arrow = tk.Button(arrow_frame, text="<", command=self.prev_month)
        left_arrow.grid(row=0, column=0)
        right_arrow = tk.Button(arrow_frame, text=">", command=self.next_month)
        right_arrow.grid(row=0, column=6)

        # Initial month label
        self.month_label = tk.Label(arrow_frame, text="")
        self.update_month_label()
        self.month_label.grid(row=0, column=3)

        # Initialize the calendar grid
        self.update_calendar_grid()

    def prev_month(self):
        # Change to the previous month
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.clicked_day = None #reset clicked day
        self.clicked_month = None #reset clicked month
        self.update_month_label() 
        self.update_calendar_grid()

    def next_month(self):
        # Change to the next month
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.clicked_day = None #reset clicked day
        self.clicked_month = None #reset clicked month
        self.update_month_label()
        self.update_calendar_grid()

    def update_month_label(self):
        # Update the month label with the current month and year
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")

    def update_calendar_grid(self):
        # Clear existing text on all buttons
        for button_row in self.buttons:
            for button in button_row:
                button.config(text="")

        # Calculate the dates for the current month
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for row_num, week in enumerate(cal):
            for col_num, day in enumerate(week):
                if day != 0:
                    # Update the text on the corresponding button
                    button = self.buttons[row_num][col_num]
                    button.config(text=str(day))

    def show_event_dialog(self, col, row):
        day_text = self.buttons[row][col]["text"]
        if day_text:
            clicked_day = int(day_text)
            clicked_month = self.current_month

            # Add logging to inspect values
            logging.debug(f"Clicked Day: {clicked_day}, Clicked Month: {clicked_month}")

            # Use clicked_day and clicked_month as the day and month components of the event date
            event_date = f"{self.current_year}-{clicked_month:02d}-{clicked_day:02d}"  # Format as YYYY-MM-DD

            # Update text label of button to match day number
            self.buttons[row][col].config(text=str(clicked_day))

            # Add logging to inspect values
            logging.debug(f"Clicked Day: {clicked_day}, Clicked Month: {clicked_month}")

            # Show add event dialog
            event_title = tk_simpledialog.askstring("Event Details", f"Enter Event Title for {event_date}:")
            if event_title:
                event_description = tk_simpledialog.askstring("Event Details", "Enter Event Description:")
                event_time = tk_simpledialog.askstring("Event Details", "Enter Event Time (HH:MM):")
                if event_time:
                    event_datetime = datetime.datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")

                    # More logging to inspect event_datetime
                    logging.debug(f"Event Datetime: {event_datetime}")

                    self.add_event(event_title, event_description, event_datetime)

    def add_event(self, event_title, event_description, event_datetime):
        if self.clicked_day is not None and self.clicked_month is not None:
            date = f"{self.current_year}-{self.clicked_month:02d}-{self.clicked_day:02d}"  # Format as YYYY-MM-DD
            # retrieve event details from the user
            event = {
                'summary': event_title,
                'description': event_description,
                'start': {
                    'dateTime': event_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                    'timeZone': 'America/Edmonton',
                },
                'end': {
                    'dateTime': event_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                    'timeZone': 'America/Edmonton',
                },
            }

            # logging
            logging.debug(f"Adding event: {event_title} on {date} at {event_datetime.strftime('%H:%M')}")

            #use google calendar api to create event
            event = calendar_service.events().insert(calendarId='primary', body=event).execute()

            #logging
            logging.info(f'Event created: {event.get("htmlLink")}')
            #display a confirmation message to the user
            print(f'Event created: {event.get("htmlLink")}')

    #def remove_event(self, date):
        # retrieve events for selected date
        # if events exist, prompt the user to select event to remove
        #use google calendar api to delete selected event
        # display confirmation message