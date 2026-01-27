import requests
import json
import hashlib
import hmac
from app import db
from app.models import Webhook

class WebhookSender:
    @staticmethod
    def dispatch(university_id, event_type, payload):
        """
        Finds webhooks for this uni and event, and sends the payload.
        In production, this should be offloaded to a task queue (Celery/RQ).
        """
        hooks = Webhook.query.filter_by(
            university_id=university_id, 
            event_type=event_type, 
            is_active=True
        ).all()
        
        results = []
        for hook in hooks:
            try:
                # Sign payload if secret exists
                headers = {'Content-Type': 'application/json'}
                if hook.secret_key:
                    signature = hmac.new(
                        hook.secret_key.encode(),
                        json.dumps(payload).encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers['X-Hub-Signature-256'] = f"sha256={signature}"
                
                # Mocking the actual request for now to avoid network errors in dev
                # response = requests.post(hook.url, json=payload, headers=headers, timeout=5)
                # results.append({'url': hook.url, 'status': response.status_code})
                
                print(f"[Webhook] Dispatched {event_type} to {hook.url}")
                results.append({'url': hook.url, 'status': 'dispatched (mock)'})
                
            except Exception as e:
                print(f"[Webhook] Failed to send {event_type} to {hook.url}: {e}")
                results.append({'url': hook.url, 'status': 'failed'})
                
        return results

webhook_sender = WebhookSender()
