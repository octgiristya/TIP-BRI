#!/bin/bash
cd app/static/vendor

# Bootstrap
curl -sL "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" -o bootstrap.min.css &
curl -sL "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" -o bootstrap.bundle.min.js &

# FontAwesome
curl -sL "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" -o all.min.css &
mkdir -p webfonts
curl -sL "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/webfonts/fa-solid-900.woff2" -o webfonts/fa-solid-900.woff2 &
curl -sL "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/webfonts/fa-regular-400.woff2" -o webfonts/fa-regular-400.woff2 &
curl -sL "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/webfonts/fa-brands-400.woff2" -o webfonts/fa-brands-400.woff2 &

# Chart.js
curl -sL "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js" -o chart.umd.js &

# ApexCharts
curl -sL "https://cdn.jsdelivr.net/npm/apexcharts" -o apexcharts.min.js &
curl -sL "https://cdn.jsdelivr.net/npm/apexcharts/dist/apexcharts.css" -o apexcharts.css &

# DataTables (Vanilla JS version - simple-datatables)
curl -sL "https://cdn.jsdelivr.net/npm/simple-datatables@9.0.0/dist/style.css" -o simple-datatables.css &
curl -sL "https://cdn.jsdelivr.net/npm/simple-datatables@9.0.0/dist/umd/simple-datatables.js" -o simple-datatables.js &

# Flatpickr
curl -sL "https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css" -o flatpickr.min.css &
curl -sL "https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.js" -o flatpickr.min.js &

# SweetAlert2
curl -sL "https://cdn.jsdelivr.net/npm/sweetalert2@11.10.5/dist/sweetalert2.min.css" -o sweetalert2.min.css &
curl -sL "https://cdn.jsdelivr.net/npm/sweetalert2@11.10.5/dist/sweetalert2.min.js" -o sweetalert2.min.js &

# Animate.css
curl -sL "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" -o animate.min.css &

wait
echo "All downloads completed."
