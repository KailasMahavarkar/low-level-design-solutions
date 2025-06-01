import requests
import json
import time
import socketio
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

# Authentication token
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ3b3JrZXIiLCJwb3AiOiJldS13ZXN0LTMifQ.s0gkRkN1kq0hDacK5No80ZIJtiT9cxsmWiMwvLWH5kY"

def get_headers():
    """Get headers with authentication"""
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def create_pizza_order(name: str, region: str, tier: str) -> Dict[str, Any]:
    """Create a new pizza order"""
    url = f"{BASE_URL}/api/pizza/create"
    data = {
        "name": name,
        "version": "1.0",
        "region": region,
        "tier": tier,
        "extra_params": {},
        "channel": "api"
    }
    response = requests.post(url, json=data, headers=get_headers())
    if response.status_code != 200:
        print(f"Error creating pizza order: {response.text}")
        return {}
    return response.json()

def approve_rfa(rfa_id: str) -> Dict[str, Any]:
    """Approve the RFA (Request For Approval)"""
    url = f"{BASE_URL}/api/rfa/{rfa_id}"
    data = {
        "status": "approved",
        "channel": "api"
    }
    response = requests.post(url, json=data, headers=get_headers())
    if response.status_code != 200:
        print(f"Error approving RFA: {response.text}")
        return {}
    return response.json()

def get_rfa_status(rfa_id: str) -> Dict[str, Any]:
    """Get the current status of an RFA"""
    url = f"{BASE_URL}/api/rfa/{rfa_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code != 200:
        print(f"Error getting RFA status: {response.text}")
        return {}
    return response.json()

class PizzaWatcher:
    """Watches real-time pizza operation updates via WebSockets"""
    
    def __init__(self):
        self.sio = socketio.Client()
        self.setup_event_handlers()
        self.connected = False
        self.updates = []
        
    def setup_event_handlers(self):
        @self.sio.event
        def connect():
            print("[OK] Connected to WebSocket server")
            self.connected = True
            
        @self.sio.event
        def disconnect():
            print("[X] Disconnected from WebSocket server")
            self.connected = False
            
        @self.sio.event
        def connect_error(data):
            print(f"[ERROR] Connection error: {data}")
            self.connected = False
        
        @self.sio.on('task_update')
        def on_task_update(data):
            print(f"\n[TASK] Task Update: {json.dumps(data, indent=2)}")
            self.updates.append(('task', data))
        
        @self.sio.on('operation_update')
        def on_operation_update(data):
            print(f"\n[OPERATION] Operation Update: {json.dumps(data, indent=2)}")
            self.updates.append(('operation', data))
        
        @self.sio.on('pizza_update')
        def on_pizza_update(data):
            print(f"\n[PIZZA] Pizza Update: {json.dumps(data, indent=2)}")
            self.updates.append(('pizza', data))
            
        @self.sio.on('customer')
        def on_customer_event(data):
            print(f"\n[CUSTOMER] Customer Event: {json.dumps(data, indent=2)}")
            self.updates.append(('customer', data))
    
    def connect(self):
        try:
            # Connect with authentication
            self.sio.connect(
                f'{BASE_URL}',
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                auth={'token': AUTH_TOKEN},
                transports=['websocket'],
                socketio_path='ws/socket.io',
                wait_timeout=5
            )
            return True
        except Exception as e:
            print(f"Failed to connect to WebSocket server: {e}")
            return False
    
    def disconnect(self):
        if self.connected:
            self.sio.disconnect()
            print("WebSocket client disconnected")

def main():
    # Create a WebSocket client to watch for updates
    watcher = PizzaWatcher()
    connected = watcher.connect()
    
    if not connected:
        print("[WARNING] Could not connect to WebSocket for real-time updates.")
        print("Continuing with REST API only...")
    
    try:
        print("\n=== Starting Pizza Order Simulation ===\n")
        
        # Step 1: Create a pizza order
        print("1. Creating pizza order...")
        order = create_pizza_order(
            name="Margherita",
            region="us-east-2",
            tier="premium"
        )
        
        if not order:
            print("Failed to create pizza order. Exiting...")
            return
            
        rfa_id = order.get('rfa_id')
        if not rfa_id:
            print("No RFA ID received. Response:", order)
            return
            
        print(f"Order created with RFA ID: {rfa_id}")
        
        # Step 2: Approve the RFA
        print("\n2. Approving RFA...")
        approval = approve_rfa(rfa_id)
        if not approval:
            print("Failed to approve RFA. Exiting...")
            return
        print("RFA approved")
        
        # Step 3: Monitor status (both via REST and WebSockets)
        print("\n3. Monitoring pizza making status...")
        print("   (Watching for WebSocket updates and polling via REST API)")
        
        # Monitor for 30 seconds
        start_time = time.time()
        last_poll = 0
        
        while time.time() - start_time < 30:
            current_time = time.time()
            
            # Poll RFA status via REST every 3 seconds
            if current_time - last_poll >= 3:
                rfa_status = get_rfa_status(rfa_id)
                if rfa_status:
                    print(f"\n[STATUS] RFA Status (via REST): {json.dumps(rfa_status, indent=2)}")
                last_poll = current_time
            
            # Small delay to avoid CPU spinning
            time.sleep(0.1)
        
        print("\n=== Simulation Complete ===")
        print(f"Received {len(watcher.updates)} real-time updates")
        
    finally:
        if connected:
            watcher.disconnect()

if __name__ == "__main__":
    main()