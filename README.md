# CIA Threat Intelligence Dashboard

A production-ready internal dashboard used by the Cyber Intelligence Analyst team to monitor Brand Protection, Account Leaks, and Card Leaks. It features a modern SOC, glassmorphism, dark-themed UI, offline functionality (no CDN dependencies), and an automated MongoDB ingestion pipeline via Excel uploads.

## Project Overview

This dashboard allows analysts to visualize critical data related to threat intelligence. 
Features include:
- Brand Protection Dashboard (Website, Document, Social Media, Instant Messenger)
- Card Leak Dashboard (Aggregations, Validation Status, Block Status, Datatable)
- Account Leak Dashboard (Validation, Reset Status, Domain Summary, Detail drill-down)
- Admin Portal (TOTP Authentication, Excel Upload)

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Async using `motor`)
- **Frontend**: Jinja2 Templates, Vanilla JavaScript, HTML5, CSS3
- **Data Processor**: Pandas (for dynamic Excel mapping)

## Folder Structure

```
TIP-BRI/
│
├── app/
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Pydantic environment configurations
│   ├── database.py               # MongoDB Async Motor client
│   ├── auth.py                   # TOTP and Session authentication logic
│   ├── routers/                  # API and Frontend route definitions
│   │   ├── pages.py              # Main dashboard routes
│   │   └── admin.py              # GodCIA admin routes
│   ├── services/                 # Business logic and MongoDB aggregations
│   │   └── dashboard_service.py
│   ├── importers/                # Data ingestion modules
│   │   └── excel_parser.py       # Pandas Excel to MongoDB parser
│   ├── templates/                # Jinja2 HTML templates
│   └── static/                   # Offline static assets (CSS, JS, Vendor libs)
│       ├── css/
│       ├── js/
│       └── vendor/               # Downloaded Bootstrap, ChartJS, etc.
│
├── resource/                     # Initial Excel seed files
├── scripts/
│   ├── download_assets.py        # Script to download vendor libs offline
│   └── initial_import.py         # Script to seed DB from /resource/
├── upload/                       # Temporary folder for admin uploads
├── .env.example                  # Environment variables template
├── requirements.txt              # Pinned Python dependencies
└── README.md                     # You are here
```

## MongoDB Connection

The application connects to MongoDB using the `AsyncIOMotorClient`.
- **Host**: `172.18.170.203` (Configurable in `.env`)
- **Database**: `cia_dashboard`
- **Collections**: `brand_protection`, `card_leak`, `account_leak`, `import_history`

## Environment Variables

Copy `.env.example` to `.env` and adjust the variables:

```
MONGO_HOST=172.18.170.203
MONGO_PORT=27017
MONGO_DATABASE=cia_dashboard
SECRET_KEY=supersecretkey_change_in_production
SESSION_KEY=session_secret_change_in_production
UPLOAD_PATH=./upload
TOTP_SECRET=4L7NVTH6QT37TWRTGHDFH62H5FNUR66C
```

## How to Install

1. Ensure Python 3.9+ is installed.
2. Clone or navigate to the project directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download offline assets (Required before running!):
   ```bash
   python scripts/download_assets.py
   ```
5. Seed initial data (Ensure MongoDB is reachable):
   ```bash
   python scripts/initial_import.py
   ```

## How to Run

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Navigate to `http://localhost:8000` in your browser.

## Admin Flow

1. Navigate to `http://localhost:8000/godcia`
2. Enter the 6-digit TOTP code generated using the secret `4L7NVTH6QT37TWRTGHDFH62H5FNUR66C`.
3. Select the target collection and upload a `.xlsx` file (Max 100MB).
4. The system will clear the old collection, import the new data, and log the operation in the history panel.

## How to Deploy

### Linux Deployment (Systemd + Nginx)

1. Create a Systemd service file (`/etc/systemd/system/cia-dashboard.service`):
```ini
[Unit]
Description=CIA Dashboard Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/TIP-BRI
Environment="PATH=/path/to/TIP-BRI/venv/bin"
ExecStart=/path/to/TIP-BRI/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

2. Enable and start: `systemctl enable --now cia-dashboard`

3. Nginx Reverse Proxy (`/etc/nginx/sites-available/cia-dashboard`):
```nginx
server {
    listen 80;
    server_name dashboard.cia.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Windows Deployment

For Windows, you can use `waitress` or run `uvicorn` using NSSM (Non-Sucking Service Manager) to run it as a background service.

## Backup & Restore MongoDB

**Backup**:
```bash
mongodump --host 172.18.170.203 --port 27017 --db cia_dashboard --out /backup/cia_dashboard_$(date +%F)
```

**Restore**:
```bash
mongorestore --host 172.18.170.203 --port 27017 --db cia_dashboard /backup/cia_dashboard_2026-07-15/cia_dashboard
```

## Security Notes

- **TOTP**: Ensure the TOTP secret is replaced and secured in production.
- **Sessions**: Change `SESSION_KEY` and `SECRET_KEY` in `.env` to strong, random values.
- **Offline Assets**: Since CDN is strictly forbidden, all libraries are loaded locally. Do not inject external scripts.
- **No SQLi**: Motor driver and FastAPI inherently protect against traditional SQL injection.

## Troubleshooting / FAQ

- **Assets missing or 404?** Run `python scripts/download_assets.py` to populate `/static/vendor`.
- **Upload fails?** Check `/upload` directory permissions and ensure file size is under 100MB.
- **Charts not rendering?** Ensure data exists in MongoDB. Run `initial_import.py`.

## Future Improvements

- Add WebSocket support for real-time dashboard updates (currently auto-refreshes every 60s).
- Add PDF/PNG Export buttons functionality (UI buttons exist, backend generation could use Playwright/Weasyprint).
- Add RBAC (Role-Based Access Control) for different analyst levels.
