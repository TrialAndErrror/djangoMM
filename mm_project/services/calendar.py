import datetime

from mm_project.log_utils import write_error_log


def handle_calendar_scroll(action, month, year):
    try:
        year_int = int(year)
        month_int = int(month)

        if action == "previous":
            if month == "1":
                return "12", str(year_int - 1)
            else:
                return str(month_int - 1), year

        elif action == "next":
            if month == "12":
                return "1", str(year_int + 1)
            else:
                return str(month_int + 1), year
        else:
            write_error_log("Calendar Scroll", f"Could not scroll calendar {action} for {month}/{year}; invalid action")
            return month, year

    except ValueError as e:
        write_error_log("Calendar Scroll", f"Could not scroll calendar {action} for {month}/{year}; {e}")
        return month, year


def get_month_choices():
    return [(str(i), datetime.datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]


def get_year_choices(today: datetime.datetime):
    return  [(str(year), year) for year in range(today.year - 10, today.year + 11)]