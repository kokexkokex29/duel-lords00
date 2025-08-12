import threading
import time
import requests
import logging
import os

logger = logging.getLogger(__name__)

def keep_alive():
    """Start the keep alive system"""
    
    def ping_server():
        """Ping the server to keep it alive"""
        while True:
            try:
                # Wait 25 minutes between pings
                time.sleep(1500)  # 25 minutes
                
                # Get the app URL from environment or use localhost
                app_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
                
                # Ping the keep-alive endpoint
                response = requests.get(f"{app_url}/keep-alive", timeout=30)
                
                if response.status_code == 200:
                    logger.info("Keep alive ping successful")
                else:
                    logger.warning(f"Keep alive ping failed with status: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Keep alive ping error: {e}")
    
    # Start the ping thread
    ping_thread = threading.Thread(target=ping_server, daemon=True)
    ping_thread.start()
    
    logger.info("Keep alive system started")
