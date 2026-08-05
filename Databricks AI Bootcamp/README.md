# Support Ticket System

A comprehensive support ticket management system built with Flask and Lakebase (Databricks-managed Postgres).

## Features

* View all support tickets
* Select ticket and view messages
* Create new ticket
* Add messages to existing tickets
* Update ticket status

## Project Structure

```
.
├── app.py                  # Main Flask application
├── lakebase.py             # Database connection module
├── app.yaml                # App configuration
├── requirements.txt        # Python dependencies
├── init_db.sql            # Database schema
├── templates/
│   └── index.html         # Web UI
└── README.md
```

## Setup

1. Configure your Lakebase credentials in app.yaml
2. Run init_db.sql to create tables
3. Install dependencies: pip install -r requirements.txt
4. Run app.py locally or deploy as Databricks App

## API Endpoints

* GET /tickets - List all tickets
* GET /tickets/<id> - Get ticket details
* POST /tickets - Create ticket
* PUT /tickets/<id>/status - Update status
* GET /tickets/<id>/messages - Get messages
* POST /tickets/<id>/messages - Add message
