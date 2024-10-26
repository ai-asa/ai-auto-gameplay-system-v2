# %%
import os
import requests
import configparser
from typing import Optional, Dict, Any
import json

class WebhookAdapter:
    def __init__(self, base_dir: str):
        config = configparser.ConfigParser()
        settings_path = os.path.join(base_dir, 'settings', 'settings.ini')
        config.read(settings_path, encoding='utf-8')
        self.webhook_url = config.get('SYSTEM', 'webhook_url')

    def post_http_event(self, type: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> bool:    
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'event': {
                'type': type if type is not None else '',
                'data': data if data is not None else ''
            }
        }
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers=headers,
                timeout=30
            )
            # レスポンスのステータスコードを確認
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            print(f"通知の送信に失敗しました: {str(e)}")
            return False
        
if __name__ == "__main__":
    base_dir = "C:/Users/pirok/ai-auto-gameplay-system"
    wa = WebhookAdapter(base_dir)
    print(wa.post_http_event())
# %%
