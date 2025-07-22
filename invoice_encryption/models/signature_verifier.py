from odoo import models, fields, api
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import base64


class SignatureVerifier(models.Model):
    _name = 'signature.verifier'
    _description = 'Signature Verifier'

    name = fields.Char(string='Verifier Name')
    move_id = fields.Many2one('account.move', string='Invoice', required=True)
    txt_file = fields.Binary(string='TXT File', required=True)
    txt_filename = fields.Char(string="TXT File Name")
    sha_file = fields.Binary(string='SHA1 File', required=True)
    sha_filename = fields.Char(string="SHA1 File Name")
    public_key = fields.Text(string='Public Key')
    private_key = fields.Text(string='Private Key')
    content_message = fields.Text(string="Decoded Content", readonly=True)
    verification_result = fields.Char(string="Verification Result", readonly=True)
    signature_string = fields.Text(string="Signature String", readonly=True)

    @api.model
    def create(self, vals):
        encryption = self.env['report.encryption'].search([], limit=1)
        if encryption:
            vals.setdefault('private_key', encryption.private_key or '')
            vals.setdefault('public_key', encryption.public_key or '')
        return super(SignatureVerifier, self).create(vals)

    def action_view_content(self):
        for rec in self:
            try:
                if not rec.txt_file:
                    rec.content_message = "No TXT file uploaded."
                    continue

                decoded_bytes = base64.b64decode(rec.txt_file)
                try:
                    rec.content_message = decoded_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    rec.content_message = decoded_bytes.hex()
            except Exception as e:
                rec.content_message = f"Error decoding: {str(e)}"

    def action_verify_signature(self):
        for rec in self:
            try:
                public_key = serialization.load_pem_public_key(
                    rec.public_key.encode("utf-8"),
                    backend=default_backend()
                )

                txt_content = base64.b64decode(rec.txt_file)
                signature = base64.b64decode(rec.sha_file)

                public_key.verify(
                    signature,
                    txt_content,
                    padding.PKCS1v15(),
                    hashes.SHA1()
                )

                rec.verification_result = "✅ Verified Successfully"

            except InvalidSignature:
                rec.verification_result = "❌ Verification Failed: Invalid Signature"
            except Exception as e:
                rec.verification_result = f"Error: {str(e)}"
