from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class TestWebhookController(http.Controller):

    @http.route('/test/webhook', type='json', auth='public', csrf=False)
    def test_webhook(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info('Test Webhook Received Data: %s', data)
            return {
                'success': True,
                'message': 'Webhook received!',
                'your_data': data
            }
        except Exception as e:
            _logger.error('Test Webhook Error: %s', str(e))
            return {
                'success': False,
                'error': str(e)
            }
