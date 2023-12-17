document.addEventListener('DOMContentLoaded', () => {
    const moveToNextMeetingButton = document.getElementById('moveToNextMeetingButton');
    
    if (moveToNextMeetingButton) {
        moveToNextMeetingButton.addEventListener('click', () => {
            window.location.href = '/next_meeting';
        });
    }
});
