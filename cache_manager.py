import json
import os
from datetime import datetime, timedelta
import threading

class CacheManager:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.lock = threading.Lock()
    
    def _get_cache_path(self, key):
        """Get the cache file path for a given key"""
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key, max_age_minutes=60):
        """Get cached data if it exists and is not expired"""
        with self.lock:
            cache_path = self._get_cache_path(key)
            
            if not os.path.exists(cache_path):
                return None
            
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is expired
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > timedelta(minutes=max_age_minutes):
                    return None
                
                return cache_data['data']
            except Exception as e:
                print(f"Error reading cache for {key}: {e}")
                return None
    
    def set(self, key, data):
        """Store data in cache"""
        with self.lock:
            cache_path = self._get_cache_path(key)
            
            try:
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }
                
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f)
            except Exception as e:
                print(f"Error writing cache for {key}: {e}")
    
    def clear_expired(self, max_age_minutes=60):
        """Clear expired cache files"""
        with self.lock:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.cache_dir, filename)
                        
                        with open(file_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        cached_time = datetime.fromisoformat(cache_data['timestamp'])
                        if datetime.now() - cached_time > timedelta(minutes=max_age_minutes):
                            os.remove(file_path)
            except Exception as e:
                print(f"Error clearing expired cache: {e}")
