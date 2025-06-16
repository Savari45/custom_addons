import math
from odoo import api, models


class ProductProduct(models.Model):
    """Inherit product_product model for adding EAN13 Standard Barcode"""
    _inherit = 'product.product'

#     @api.model
#     def create(self, vals):
#         """Function to add EAN13 Standard barcode at the time
#         create new product"""
#         res = super(ProductProduct, self).create(vals)
#         ean = generate_ean(str(res.id))
#         res.barcode = '21' + ean[2:]
#         return res
#
#
# def ean_checksum(eancode):
#     """Returns the checksum of an ean string of length 13, returns -1 if
#     the string has the wrong length"""
#     if len(eancode) != 13:
#         return -1
#     odd_sum = 0
#     even_sum = 0
#     for rec in range(len(eancode[::-1][1:])):
#         if rec % 2 == 0:
#             odd_sum += int(eancode[::-1][1:][rec])
#         else:
#             even_sum += int(eancode[::-1][1:][rec])
#     total = (odd_sum * 3) + even_sum
#     return int(10 - math.ceil(total % 10.0)) % 10
#
#
# def check_ean(eancode):
#     """Returns True if ean code is a valid ean13 string, or null"""
#     if not eancode:
#         return True
#     if len(eancode) != 13:
#         return False
#     try:
#         int(eancode)
#     except:
#         return False
#     return ean_checksum(eancode)
#
#
# def generate_ean(ean):
#     """Creates and returns a valid ean13 from an invalid one"""
#     if not ean:
#         return "0000000000000"
#     product_identifier = '00000000000' + ean
#     ean = product_identifier[-11:]
#     check_number = check_ean(ean + '00')
#     return f'{ean}0{check_number}'

    @api.model
    def create(self, vals):
        """Auto-generate 10-digit barcode increasing by 1."""
        # Only generate barcode if not manually set
        if not vals.get('barcode'):
            # Search for existing max barcode
            existing_barcodes = self.search([('barcode', '!=', False)])
            max_barcode = 0
            for product in existing_barcodes:
                try:
                    # Ensure barcode is numeric and 10 digits
                    if product.barcode.isdigit() and len(product.barcode) == 13:
                        max_barcode = max(max_barcode, int(product.barcode))
                except ValueError:
                    continue  # Skip non-integer barcodes

            # Generate next barcode
            next_barcode = str(max_barcode + 1).zfill(10)

            # Double-check uniqueness (rare, but safe)
            while self.search_count([('barcode', '=', next_barcode)]) > 0:
                max_barcode += 1
                next_barcode = str(max_barcode + 1).zfill(10)

            vals['barcode'] = next_barcode

        return super(ProductProduct, self).create(vals)