# main.py
from calendar_helper import authenticate_and_get_service, print_today_events_info

def main():
    service = authenticate_and_get_service()
    print_today_events_info(service)

if __name__ == "__main__":
    main()
