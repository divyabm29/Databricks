-- Lakebase Database Schema for Support Ticket System
-- Run this script to initialize the database tables

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS ticket_messages CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;

-- Create tickets table
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_status CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    CONSTRAINT check_priority CHECK (priority IN ('low', 'medium', 'high'))
);

-- Create ticket_messages table
CREATE TABLE ticket_messages (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX idx_tickets_created_by ON tickets(created_by);
CREATE INDEX idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
CREATE INDEX idx_ticket_messages_created_at ON ticket_messages(created_at);

-- Insert sample data for testing
INSERT INTO tickets (subject, description, status, priority, created_by) VALUES
('Database connection timeout', 'Unable to connect to production database. Getting timeout errors after 30 seconds.', 'open', 'high', 'alice@example.com'),
('Feature request: Dark mode', 'It would be great to have a dark mode option in the UI for better readability at night.', 'open', 'low', 'bob@example.com'),
('Cannot upload files larger than 10MB', 'When trying to upload files larger than 10MB, I get an error message.', 'in_progress', 'medium', 'charlie@example.com'),
('Dashboard not loading', 'The analytics dashboard shows a blank page when I try to access it.', 'resolved', 'high', 'diana@example.com'),
('Password reset email not received', 'Requested a password reset but never received the email.', 'closed', 'medium', 'eve@example.com');

-- Insert sample messages
INSERT INTO ticket_messages (ticket_id, message, created_by) VALUES
(1, 'I can confirm this issue. Experiencing the same timeout errors.', 'frank@example.com'),
(1, 'We are investigating the issue. It seems to be related to network configuration.', 'support@example.com'),
(3, 'This is being worked on by the development team. We will update you soon.', 'support@example.com'),
(3, 'Thank you for the update!', 'charlie@example.com'),
(4, 'Cleared the browser cache and it is working now. Thank you!', 'diana@example.com'),
(5, 'Please check your spam folder. If still not there, let us know.', 'support@example.com'),
(5, 'Found it in spam. All good now!', 'eve@example.com');

-- Display table information
SELECT 'Tickets table created with ' || COUNT(*) || ' sample records' as status FROM tickets;
SELECT 'Messages table created with ' || COUNT(*) || ' sample records' as status FROM ticket_messages;
