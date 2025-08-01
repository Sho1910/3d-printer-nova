# api/print.py
"""
Vercel serverless function for /print command
Each endpoint is a separate file in the /api folder
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Dummy printer data (same as before)
DUMMY_PRINTERS = [
    {
        "id": "printer_1",
        "name": "Bambu X1 #1",
        "model": "X1 Carbon",
        "status": "available",
        "ip": "192.168.1.101",
        "current_job": None,
        "progress": 0,
        "time_remaining": 0,
        "last_job": "phone_case.3mf"
    },
    {
        "id": "printer_2", 
        "name": "Bambu X1 #2",
        "model": "X1 Carbon",
        "status": "printing",
        "ip": "192.168.1.102",
        "current_job": "testslide1f",
        "progress": 45,
        "time_remaining": 135,
        "started_by": "@shobhit"
    },
    {
        "id": "printer_3",
        "name": "Bambu X1 #3", 
        "model": "X1 Carbon",
        "status": "available",
        "ip": "192.168.1.103",
        "current_job": None,
        "progress": 0,
        "time_remaining": 0,
        "last_job": "benchy_test.3mf"
    },
    {
        "id": "printer_4",
        "name": "Bambu X1 #4",
        "model": "X1 Carbon", 
        "status": "offline",
        "ip": "192.168.1.104",
        "current_job": None,
        "progress": 0,
        "time_remaining": 0,
        "error": "Network connection lost"
    }
]

def get_status_emoji(status):
    """Get emoji for printer status"""
    status_emojis = {
        "available": "✅",
        "printing": "🔒", 
        "paused": "⏸️",
        "offline": "⚠️",
        "maintenance": "🔧",
        "error": "❌"
    }
    return status_emojis.get(status, "❓")

def format_time_remaining(minutes):
    """Format time remaining in readable format"""
    if minutes <= 0:
        return ""
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"

def create_printer_dashboard():
    """Create the main printer dashboard Slack message"""
    
    # Header
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🏭 3D Printer Farm Status"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Each printer status
    for printer in DUMMY_PRINTERS:
        status_emoji = get_status_emoji(printer["status"])
        
        # Main printer info
        if printer["status"] == "printing":
            status_text = f"*{printer['name']}* {status_emoji} Printing\n" \
                         f"📄 Job: {printer['current_job']}\n" \
                         f"📊 Progress: {printer['progress']}%\n" \
                         f"⏱️ Remaining: {format_time_remaining(printer['time_remaining'])}\n" \
                         f"👤 Started by: {printer.get('started_by', 'Unknown')}"
            
            button_text = "View Progress"
            button_style = "primary"
            
        elif printer["status"] == "available":
            status_text = f"*{printer['name']}* {status_emoji} Available\n" \
                         f"🔧 Model: {printer['model']}\n" \
                         f"📁 Last job: {printer.get('last_job', 'None')}"
            
            button_text = "Start Print"
            button_style = "primary"
            
        elif printer["status"] == "offline":
            status_text = f"*{printer['name']}* {status_emoji} Offline\n" \
                         f"❌ Error: {printer.get('error', 'Unknown error')}\n" \
                         f"🌐 IP: {printer['ip']}"
            
            button_text = "Check Status"
            button_style = "danger"
            
        else:
            status_text = f"*{printer['name']}* {status_emoji} {printer['status'].title()}"
            button_text = "View Details"
            button_style = "default"
        
        # Add printer block
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": status_text
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": button_text
                },
                "style": button_style,
                "action_id": f"printer_action_{printer['id']}",
                "value": printer['id']
            }
        })
        
        blocks.append({"type": "divider"})
    
    # Footer with actions
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🔄 Refresh Status"
                },
                "action_id": "refresh_status",
                "style": "primary"
            },
            {
                "type": "button", 
                "text": {
                    "type": "plain_text",
                    "text": "📋 View Queue"
                },
                "action_id": "view_queue"
            }
        ]
    })
    
    # Timestamp
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Last updated: {datetime.now().strftime('%I:%M %p')}"
            }
        ]
    })
    
    return {
        "response_type": "ephemeral",
        "blocks": blocks
    }

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_POST(self):
        """Handle POST requests from Slack"""
        try:
            # Parse the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Slack sends form-encoded data
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Get Slack data
            channel_name = parsed_data.get('channel_name', [''])[0]
            user_name = parsed_data.get('user_name', [''])[0]
            
            # Only allow in your test channel
            if channel_name != '3d-printer-automation-test':
                response = {
                    "text": "❌ This command only works in #3d-printer-automation-test channel"
                }
            else:
                # Return the printer dashboard
                response = create_printer_dashboard()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"text": f"❌ Error: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_GET(self):
        """Handle GET requests (for testing)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Slack 3D Printer Bot is running on Vercel!')