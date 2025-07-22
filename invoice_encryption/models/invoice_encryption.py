from odoo import models, fields
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import base64
import logging

_logger = logging.getLogger(__name__)


class ReportEncryption(models.Model):
    _name = 'report.encryption'
    _description = 'Report Encryption'

    public_key = fields.Text(string='Public Key')
    private_key = fields.Text(string='Private Key')


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_sign = fields.Text(string='Invoice Digital Signature')
    signature_code = fields.Text(string='Signature Code')
    invoice_hash = fields.Text(string='Hash')
    signed_content = fields.Text(string='Signed Content')

    def action_report(self):
        """Generate digital signatures for invoices following SAF-T (PT) requirements."""
        try:
            previous_hash = None

            last_signed = self.env['account.move'].search([
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('invoice_hash', '!=', False)
            ], order='create_date desc', limit=1)

            if last_signed:
                previous_hash = last_signed.invoice_hash.strip()
                _logger.debug("Using previous hash: %s", previous_hash)

            encryption = self.env['report.encryption'].search([], limit=1)
            if not encryption or not encryption.private_key:
                raise ValueError("No encryption keys found in report.encryption model.")

            try:
                private_key = serialization.load_pem_private_key(
                    encryption.private_key.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            except Exception as e:
                raise ValueError(f"Failed to load private key: {str(e)}")

            for move in self:
                if move.invoice_sign or move.move_type not in ['out_invoice', 'out_refund']:
                    continue

                system_date_str = move.create_date.strftime('%Y-%m-%dT%H:%M:%S')
                amount_str = "{:.2f}".format(move.amount_total)

                content_parts = [
                    str(move.invoice_date),
                    system_date_str,
                    move.name,
                    amount_str,
                    ""
                ]
                if previous_hash:
                    content_parts.insert(-1, previous_hash)

                content = ";".join(content_parts)
                out_content = content.encode('utf-8')

                try:
                    signature = private_key.sign(
                        out_content,
                        padding.PKCS1v15(),
                        hashes.SHA1()
                    )
                except Exception as e:
                    raise ValueError(f"Failed to sign content for invoice {move.name}: {str(e)}")

                signature_b64 = base64.b64encode(signature).decode('utf-8')
                signature_string = self._generate_signature_code(signature)

                move.write({
                    'invoice_sign': signature_b64,
                    'signature_code': signature_string,
                    'invoice_hash': signature_b64,
                    'signed_content': content
                })

                # Save in Signature Verifier
                safe_name = move.name.replace('/', '_')
                self.env['signature.verifier'].create({
                    'move_id': move.id,
                    'txt_file': base64.b64encode(content.encode('utf-8')),
                    'txt_filename': f"{safe_name}_registry.txt",
                    'sha_file': base64.b64encode(signature),
                    'sha_filename': f"{safe_name}_registry.sha1",
                    'signature_string': signature_string,
                })

                previous_hash = signature_b64

        except Exception as e:
            _logger.exception("Error in invoice signing process")
            raise

    def _generate_signature_code(self, signature):
        try:
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            if len(signature_b64) < 31:
                raise ValueError("Base64 signature too short (minimum 31 chars required)")

            extracted_chars = [
                signature_b64[0],
                signature_b64[10],
                signature_b64[20],
                signature_b64[30]
            ]
            return f"{''.join(extracted_chars)}-Processed by validated program no."
        except Exception as e:
            _logger.error("Failed to generate signature code: %s", str(e))
            raise ValueError(f"Signature code generation failed: {str(e)}")
