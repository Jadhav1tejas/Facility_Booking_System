document.addEventListener("DOMContentLoaded", function () {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });

    // Initialize 12-hour AM/PM Time Picker on all type="time" inputs
    if (typeof flatpickr !== 'undefined') {
        flatpickr("input[type=time]", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i", // Send 24-hr format to Django
            altInput: true,
            altFormat: "h:i K" // Display AM/PM to user
        });
    }

    const facilitySelect = document.getElementById("facility_id");
    const dateInput = document.getElementById("Booking_date");
    const resultsDiv = document.getElementById("availability-results");

    if (dateInput) {
        // Prevent picking past dates in the calendar picker
        const todayStr = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', todayStr);
    }

    function checkAvailability() {
        if (!facilitySelect || !dateInput || !resultsDiv) return;

        const facilityId = facilitySelect.value;
        const dateStr = dateInput.value;

        if (!facilityId || !dateStr) {
            resultsDiv.style.display = 'none';
            return;
        }

        const todayStr = new Date().toISOString().split('T')[0];
        if (dateStr < todayStr) {
            resultsDiv.innerHTML = `<span style="color:red; font-weight:600;">⚠️ Cannot check availability or book for a past date.</span>`;
            resultsDiv.style.display = 'block';
            return;
        }

        fetch(`/api/availability/?facility_id=${facilityId}&date=${dateStr}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
                    resultsDiv.style.display = 'block';
                    return;
                }

                let html = `<strong>${data.facility_name} Availability for ${data.date}</strong><br><br>`;

                if (data.timeline && data.timeline.length > 0) {
                    html += `<table style="width: 100%; border-collapse: collapse;">`;
                    data.timeline.forEach(slot => {
                        let color = "inherit";
                        if (slot.status === "Available") color = "green";
                        if (slot.status === "Booked") color = "red";
                        if (slot.status === "Buffer") color = "gray";

                        html += `
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 8px 0; width: 40%; font-family: monospace;">${slot.start} - ${slot.end}</td>
                            <td style="padding: 8px 0; color: ${color};">
                                ${slot.icon} ${slot.status}
                            </td>
                        </tr>`;
                    });
                    html += `</table>`;
                } else {
                    html += `<span style="color:green;">No bookings yet! All slots are available.</span>`;
                }

                resultsDiv.innerHTML = html;
                resultsDiv.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching availability:', error);
            });
    }

    if (facilitySelect) {
        facilitySelect.addEventListener("change", checkAvailability);
    }
    if (dateInput) {
        dateInput.addEventListener("change", checkAvailability);
    }

    // Call on load in case inputs are pre-filled
    checkAvailability();
});
