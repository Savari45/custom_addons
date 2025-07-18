from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(required=False)

    @api.constrains('phone')
    def _check_phone_required_and_format(self):
        pattern = re.compile(r'^(?:\+91|91)?[6-9]\d{9}$')  # Strict Indian mobile number format
        for partner in self:
            if not partner.phone and not partner.parent_id:
                raise ValidationError("Phone number is required for a customer.")
            if partner.phone:
                phone_clean = re.sub(r'\s|\-|\(|\)', '', partner.phone)  # clean formatting
                if not pattern.match(phone_clean):
                    raise ValidationError(
                        "Enter a valid 10-digit Indian mobile number (with optional +91 or 91 prefix).")

    @api.constrains('mobile')
    def _check_duplicate_mobile(self):
        pattern = re.compile(r'^(?:\+91|91)?([6-9]\d{9})$')  # capture actual 10-digit part
        for partner in self:
            if partner.mobile:
                mobile_clean = re.sub(r'\s|\-|\(|\)', '', partner.mobile)
                match = pattern.match(mobile_clean)
                if not match:
                    continue  # skip invalid mobile numbers

                base_mobile = match.group(1)  # get just the 10-digit number

                existing = self.env['res.partner'].search([
                    ('id', '!=', partner.id),
                    ('mobile', '!=', False)
                ])

                for other in existing:
                    other_clean = re.sub(r'\s|\-|\(|\)', '', other.mobile or '')
                    other_match = pattern.match(other_clean)
                    if other_match and other_match.group(1) == base_mobile:
                        raise ValidationError(
                            f"The mobile number '{partner.mobile}' is already used by '{other.name}'.")

    @api.model
    def create(self, vals):
        phone = vals.get('phone')
        if phone:
            phone_clean = re.sub(r'\D', '', phone)
            if len(phone_clean) == 10 or (phone_clean.startswith('91') and len(phone_clean) == 12):
                vals['mobile'] = phone
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        for partner in self:
            phone = vals.get('phone') or partner.phone
            if phone:
                phone_clean = re.sub(r'\D', '', phone)
                if len(phone_clean) == 10 or (phone_clean.startswith('91') and len(phone_clean) == 12):
                    vals['mobile'] = phone
        return super(ResPartner, self).write(vals)