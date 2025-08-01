# api/actions.py
"""
Vercel serverless function for handling button clicks and interactions
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import urllib.parse

def create_start_print_dialog(printer_id):
    """Create start print job dialog"""
    return {
        "response_type": "ephemeral",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🖨️ Start Print Job - Bambu X1 #{printer_id[-1]}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📁 Select File to Print:*"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Choose a file..."
                        },
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "benchy_test.3mf"},
                                "value": "benchy_test.3mf"
                            },
                            {
                                "text": {"type": "plain_text", "text": "phone_case.3mf"},
                                "value": "phone_case.3mf"
                            },
                            {
                                "text": {"type": "plain_text", "text": "custom_part.3mf"},
                                "value": "custom_part.3mf"
                            }
                        ],
                        "action_id": "select_file"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📋 Job Details:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Client Type:"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select client type..."
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Internal"},
                            "value": "internal"
                        },
                        {
                            "text": {"type": "plain_text", "text": "External"},
                            "value": "external"
                        }
                    ],
                    "action_id": "client_type"
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter project name..."
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Project Name"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🚀 Start Print"
                        },
                        "style": "primary",
                        "action_id": f"confirm_print_{printer_id}",
                        "value": printer_id
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Cancel"
                        },
                        "action_id": "cancel_print"
                    }
                ]
            }
        ]
    }

def create_printing_status(printer_id):
    """Show detailed printing status"""
    return {
        "response_type": "ephemeral",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🖨️ Bambu X1 #{printer_id[-1]} - Live Status"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*📊 Progress:* 45% complete\n" \
                           f"*⏱️ Time Remaining:* 2h 15m\n" \
                           f"*📄 Current Job:* testslide1f\n" \
                           f"*👤 Started by:* @shobhit\n" \
                           f"*💰 Estimated Cost:* $12.50"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Progress Bar:*\n" + "█" * 9 + "░" * 11 + " 45%"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "⏸️ Pause"
                        },
                        "action_id": f"pause_print_{printer_id}",
                        "style": "danger"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text", 
                            "text": "🛑 Cancel Print"
                        },
                        "action_id": f"cancel_print_{printer_id}",
                        "style": "danger"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📹 Live Feed"
                        },
                        "action_id": f"live_feed_{printer_id}",
                        "url": f"http://192.168.1.10{printer_id[-1]}:8080/stream"
                    }
                ]
            }
        ]
    }

# api/actions.py
"""
Vercel serverless function for handling button clicks and interactions
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Duplicate the dashboard function here (since Vercel can't import between files easily)
def create_printer_dashboard():
    """Create the main printer dashboard Slack message"""
    
    # Dummy printer data 
    DUMMY_PRINTERS = [
        {
            "id": "printer_1",
            "name": "Bambu X1 #1",
            "model": "X1 Carbon",
            "status": "available",
            "last_job": "phone_case.3mf"
        },
        {
            "id": "printer_2", 
            "name": "Bambu X1 #2",
            "model": "X1 Carbon",
            "status": "printing",
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
            "last_job": "benchy_test.3mf"
        },
        {
            "id": "printer_4",
            "name": "Bambu X1 #4",
            "model": "X1 Carbon", 
            "status": "offline",
            "error": "Network connection lost"
        }
    ]
    
    def get_status_emoji(status):
        status_emojis = {
            "available": "✅",
            "printing": "🔒", 
            "offline": "⚠️"
        }
        return status_emojis.get(status, "❓")

    def format_time_remaining(minutes):
        if minutes <= 0:
            return ""
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"
    
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
                         f"❌ Error: {printer.get('error', 'Unknown error')}"
            button_text = "Check Status"
            button_style = "danger"
        
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
    """Vercel serverless function handler for button interactions"""
    
    def do_POST(self):
        """Handle POST requests from Slack button interactions"""
        try:
            # Parse the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Slack sends form-encoded data for interactions
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Get the payload (Slack sends interaction data as 'payload')
            payload_str = parsed_data.get('payload', [''])[0]
            payload = json.loads(payload_str)
            
            action_id = payload['actions'][0]['action_id']
            user = payload['user']['name']
            
            if action_id == 'refresh_status':
                response = create_printer_dashboard()
            
            elif action_id.startswith('printer_action_'):
                printer_id = action_id.replace('printer_action_', '')
                
                # Check what action to take based on printer status
                if printer_id == "printer_1" or printer_id == "printer_3":  # Available printers
                    response = create_start_print_dialog(printer_id)
                elif printer_id == "printer_2":  # Printing printer
                    response = create_printing_status(printer_id)
                else:  # Offline printer
                    response = {
                        "text": f"ℹ️ Bambu X1 #{printer_id[-1]} is currently offline. Check network connection."
                    }
            
            elif action_id.startswith('confirm_print_'):
                printer_id = action_id.replace('confirm_print_', '')
                response = {
                    "text": f"🚀 Print job started on Bambu X1 #{printer_id[-1]}! Check status with `/print`"
                }
            
            elif action_id == 'view_queue':
                response = {
                    "text": "📋 Print queue is currently empty. All jobs are processed immediately."
                }
            
            elif action_id == 'cancel_print':
                response = {
                    "text": "❌ Print job cancelled."
                }
            
            else:
                response = {"text": f"👍 Action '{action_id}' received"}
            
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
            error_response = {"text": f"❌ Error processing action: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_GET(self):
        """Handle GET requests (for testing)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Slack Actions Handler is running on Vercel!')