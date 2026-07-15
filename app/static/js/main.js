document.addEventListener('DOMContentLoaded', () => {
    // Animated Counters
    const animateCounters = () => {
        const counters = document.querySelectorAll('.kpi-value');
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            if(isNaN(target)) return;
            const duration = 1500; // 1.5s
            const step = target / (duration / 16); // 60fps
            
            let current = 0;
            const updateCounter = () => {
                current += step;
                if (current < target) {
                    counter.innerText = Math.ceil(current).toLocaleString();
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.innerText = target.toLocaleString();
                }
            };
            
            // Only animate once it's in view (optional, here we just animate on load)
            updateCounter();
        });
    };

    animateCounters();

    // Auto Refresh Dashboard (Bonus Feature)
    // Checks if there's a meta tag or something, or just unconditionally refresh every 60s
    const REFRESH_INTERVAL = 60000;
    setTimeout(() => {
        // Skip refresh if we're interacting with a datatable or input
        if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'SELECT') {
            window.location.reload();
        }
    }, REFRESH_INTERVAL);

    // Global Date Picker (Flatpickr)
    const datePickerEl = document.getElementById('global-date-range');
    if (datePickerEl && typeof flatpickr !== 'undefined') {
        flatpickr(datePickerEl, {
            mode: "range",
            dateFormat: "Y-m-d",
            theme: "dark",
            onChange: function(selectedDates, dateStr, instance) {
                // In a real app, this would append to URL and reload
                console.log("Date range changed to:", dateStr);
            }
        });
    }
});

// Toast Notification functionality
window.showToast = (message, type = 'success') => {
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            background: 'var(--bg-panel)',
            color: 'var(--text-primary)',
            didOpen: (toast) => {
              toast.onmouseenter = Swal.stopTimer;
              toast.onmouseleave = Swal.resumeTimer;
            }
        });
        Toast.fire({
            icon: type,
            title: message
        });
    } else {
        alert(message);
    }
};
