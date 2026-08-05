-- Lakebase Database Schema for Support Ticket System
-- Run this script to initialize the database tables

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS ticket_messages CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;

-- Create tickets table
CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Create ticket_messages table
CREATE TABLE ticket_messages (
    message_id INTEGER PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX idx_tickets_created_by ON tickets(created_by);
CREATE INDEX idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
CREATE INDEX idx_ticket_messages_created_at ON ticket_messages(created_at);

-- Insert sample data for testing
INSERT INTO tickets (ticket_id, title, status, created_by, created_at) VALUES
(101, 'Unable to reset user password', 'open', 'alex_smith', '2026-08-01 09:15:00'),
(102, 'Payment gateway error on checkout', 'in_progress', 'maria_garcia', '2026-08-02 11:30:00'),
(103, 'Dashboard metrics not loading', 'resolved', 'david_lee', '2026-08-03 14:00:00');

-- Insert sample messages
INSERT INTO ticket_messages (message_id, ticket_id, message_text, author, created_at) VALUES
(1, 101, 'I tried resetting my password using the email link...', 'alex_smith', '2026-08-01 09:15:00'),
(2, 101, 'Hello Alex, we are looking into the token expiration...', 'support_team', '2026-08-01 10:05:00'),
(3, 102, 'Customers are getting Error 502 when placing orders...', 'maria_garcia', '2026-08-02 11:30:00'),
(4, 102, 'Investigating logs with the payment processor now...', 'tech_lead', '2026-08-02 12:10:00'),
(5, 103, 'The analytics tab shows a blank screen since this morning.', 'david_lee', '2026-08-03 14:00:00'),
(6, 103, 'The cache issue has been resolved. Please clear...', 'support_team', '2026-08-03 15:45:00');

-- Display table information
SELECT 'Tickets table created with ' || COUNT(*) || ' sample records' as status FROM tickets;
SELECT 'Messages table created with ' || COUNT(*) || ' sample records' as status FROM ticket_messages;
