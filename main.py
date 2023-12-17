# main.py
from calendar_helper import authenticate_and_get_service, save_today_events_to_csv

def main():
    service = authenticate_and_get_service()
    save_today_events_to_csv(service)
    print('Today\'s events have been saved to events.csv.')

if __name__ == "__main__":
    main()
