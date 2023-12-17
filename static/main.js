document.addEventListener('DOMContentLoaded', function () {
    var moveToNextMeetingButton = document.getElementById('moveToNextMeetingButton');
    if (moveToNextMeetingButton) {
        moveToNextMeetingButton.addEventListener('click', function () {
            window.location.href = '/next_meeting';
        });
    }
});
