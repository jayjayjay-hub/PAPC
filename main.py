from calendar_helper import authenticate_and_get_service, find_next_meeting_url

def main():
    service = authenticate_and_get_service()
    meeting_url = find_next_meeting_url(service)
    print(f'Next meeting URL: {meeting_url}')

if __name__ == "__main__":
    main()
