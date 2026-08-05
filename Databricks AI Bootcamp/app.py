"""
Databricks App: Support Ticket System
- Serves a Flask API for managing support tickets
- Reads/writes to Lakebase (Databricks-managed Postgres) via lakebase.py
- Provides REST endpoints for ticket and message management

Features:
- View all support tickets
- Select a ticket and view its messages
- Create a new ticket
- Add a message to an existing ticket
- Update a ticket's status

Run locally:
    python app.py
Deploy as a Databricks App using app.yaml.
"""

import logging
import os
from datetime import datetime

from databricks.sdk import WorkspaceClient
from flask import Flask, jsonify, render_template, request

import lakebase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticket-app")

app = Flask(__name__)
_w = WorkspaceClient()

TICKETS_TABLE_NAME = os.environ.get("TICKETS_TABLE_NAME", "tickets")
TICKET_MESSAGES_TABLE_NAME = os.environ.get("TICKET_MESSAGES_TABLE_NAME", "ticket_messages")


def _current_user_email() -> str:
    """
    Resolve the current user's email for personalization.

    Databricks Apps inject the logged-in user's identity via the
    X-Forwarded-Email header on every request. Fall back to the Databricks
    SDK's current_user API for local development where that header isn't set.
    """
    header_email = request.headers.get("X-Forwarded-Email")
    if header_email:
        return header_email
    return _w.current_user.me().user_name


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.errorhandler(Exception)
def handle_exception(err):
    """Ensure all unhandled errors return JSON (not an HTML error page),
    so the frontend's resp.json() call never chokes on HTML."""
    logger.exception("Unhandled exception while processing request")
    status_code = getattr(err, "code", 500)
    if not isinstance(status_code, int):
        status_code = 500
    return jsonify({"error": str(err)}), status_code


@app.route("/")
def index():
    """Serve the support ticket management UI."""
    return render_template("index.html")


# ==================== TICKET ROUTES ====================

@app.route("/tickets", methods=["GET"])
def list_tickets():
    """View all support tickets."""
    status_filter = request.args.get("status")
    limit = int(request.args.get("limit", 100))
    
    if status_filter:
        query = f"""
            SELECT id, subject, description, status, priority, created_by, created_at, updated_at
            FROM {TICKETS_TABLE_NAME}
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = lakebase.run_query(query, (status_filter, limit))
    else:
        query = f"""
            SELECT id, subject, description, status, priority, created_by, created_at, updated_at
            FROM {TICKETS_TABLE_NAME}
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = lakebase.run_query(query, (limit,))
    
    return jsonify(rows)


@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    """Get a specific ticket by ID."""
    query = f"""
        SELECT id, subject, description, status, priority, created_by, created_at, updated_at
        FROM {TICKETS_TABLE_NAME}
        WHERE id = %s
    """
    rows = lakebase.run_query(query, (ticket_id,))
    
    if not rows:
        return jsonify({"error": "Ticket not found"}), 404
    
    return jsonify(rows[0])


@app.route("/tickets", methods=["POST"])
def create_ticket():
    """Create a new support ticket."""
    data = request.get_json()
    
    if not data or not data.get("subject"):
        return jsonify({"error": "Subject is required"}), 400
    
    subject = data.get("subject")
    description = data.get("description", "")
    priority = data.get("priority", "medium")
    created_by = _current_user_email()
    
    query = f"""
        INSERT INTO {TICKETS_TABLE_NAME} (subject, description, status, priority, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, subject, description, status, priority, created_by, created_at, updated_at
    """
    
    rows = lakebase.run_query(query, (subject, description, "open", priority, created_by))
    
    if not rows:
        return jsonify({"error": "Failed to create ticket"}), 500
    
    logger.info(f"Created ticket {rows[0]['id']} by {created_by}")
    return jsonify(rows[0]), 201


@app.route("/tickets/<int:ticket_id>/status", methods=["PUT", "PATCH"])
def update_ticket_status(ticket_id):
    """Update a ticket's status."""
    data = request.get_json()
    
    if not data or not data.get("status"):
        return jsonify({"error": "Status is required"}), 400
    
    new_status = data.get("status")
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
    
    query = f"""
        UPDATE {TICKETS_TABLE_NAME}
        SET status = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id, subject, description, status, priority, created_by, created_at, updated_at
    """
    
    rows = lakebase.run_query(query, (new_status, ticket_id))
    
    if not rows:
        return jsonify({"error": "Ticket not found"}), 404
    
    logger.info(f"Updated ticket {ticket_id} status to {new_status}")
    return jsonify(rows[0])


# ==================== TICKET MESSAGES ROUTES ====================

@app.route("/tickets/<int:ticket_id>/messages", methods=["GET"])
def get_ticket_messages(ticket_id):
    """View all messages for a specific ticket."""
    # First verify the ticket exists
    ticket_query = f"SELECT id FROM {TICKETS_TABLE_NAME} WHERE id = %s"
    ticket_rows = lakebase.run_query(ticket_query, (ticket_id,))
    
    if not ticket_rows:
        return jsonify({"error": "Ticket not found"}), 404
    
    # Get messages for the ticket
    query = f"""
        SELECT id, ticket_id, message, created_by, created_at
        FROM {TICKET_MESSAGES_TABLE_NAME}
        WHERE ticket_id = %s
        ORDER BY created_at ASC
    """
    
    rows = lakebase.run_query(query, (ticket_id,))
    return jsonify(rows)


@app.route("/tickets/<int:ticket_id>/messages", methods=["POST"])
def add_ticket_message(ticket_id):
    """Add a message to an existing ticket."""
    # First verify the ticket exists
    ticket_query = f"SELECT id FROM {TICKETS_TABLE_NAME} WHERE id = %s"
    ticket_rows = lakebase.run_query(ticket_query, (ticket_id,))
    
    if not ticket_rows:
        return jsonify({"error": "Ticket not found"}), 404
    
    data = request.get_json()
    
    if not data or not data.get("message"):
        return jsonify({"error": "Message is required"}), 400
    
    message = data.get("message")
    created_by = _current_user_email()
    
    query = f"""
        INSERT INTO {TICKET_MESSAGES_TABLE_NAME} (ticket_id, message, created_by, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING id, ticket_id, message, created_by, created_at
    """
    
    rows = lakebase.run_query(query, (ticket_id, message, created_by))
    
    if not rows:
        return jsonify({"error": "Failed to add message"}), 500
    
    # Update the ticket's updated_at timestamp
    update_query = f"UPDATE {TICKETS_TABLE_NAME} SET updated_at = NOW() WHERE id = %s"
    lakebase.run_query(update_query, (ticket_id,))
    
    logger.info(f"Added message to ticket {ticket_id} by {created_by}")
    return jsonify(rows[0]), 201


if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    app.run(debug=True, host=host, port=port)
    logger.info(f"Flask app running on http://{host}:{port}")