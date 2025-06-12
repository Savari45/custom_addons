import json
import os
from odoo import models

EXPORT_PATH = '/tmp/res_partner_export.jsonl'
BATCH_SIZE = 10000

class ResPartnerExport(models.Model):
    _inherit = 'res.partner'

    def export_partner_data_to_file(self):
        domain = []
        fields = [
            'name', 'email', 'phone', 'mobile', 'street', 'city', 'zip',
            'state_id', 'country_id', 'company_type', 'is_company',
            'customer_rank', 'supplier_rank',
        ]

        offset = 0
        total = self.search_count(domain)
        print(f"Exporting {total} res.partner records...")

        with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
            while True:
                records = self.search_read(domain, fields, offset=offset, limit=BATCH_SIZE)
                if not records:
                    break

                for rec in records:
                    if rec['state_id']:
                        state = self.env['res.country.state'].browse(rec['state_id'][0])
                        rec['state_code'] = state.name
                        rec['state_id'] = None
                    if rec['country_id']:
                        country = self.env['res.country'].browse(rec['country_id'][0])
                        rec['country_code'] = country.code
                        rec['country_id'] = None

                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

                offset += BATCH_SIZE
                print(f"Exported: {offset}/{total}")
