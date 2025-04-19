from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
import re
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_id = fields.Many2one(
        'product.product',
        domain="[('product_id.qty_available', '>', 0)]",  # Ensures only positive stock products
        required=True
    )
    product_template_id = fields.Many2one(
        'product.template',
        domain="[('qty_available', '>', 0)]",  # Ensures only positive stock products
        required=True
    )

    @api.constrains('product_id')
    def _check_product_stock(self):
        for line in self:
            if line.product_id.qty_available <= 0:
                raise ValidationError(f"The product {line.product_id.name} is out of stock!")
    # profit = fields.Float(string="Profit", compute="_compute_line_profit", store=True)
    # total_profit = fields.Float(string="Total Profit", compute="_compute_total_profit", store=True)
    # @api.depends('price_unit', 'product_id', 'product_id.standard_price', 'product_uom_qty')
    # def _compute_line_profit(self):
    #     """Compute profit for each sale order line."""
    #     for line in self:
    #         if line.product_id:
    #             line.profit = (line.price_unit - line.product_id.standard_price) * line.product_uom_qty
    #         else:
    #             line.profit = 0
    #
    # @api.depends('order_id.order_line.profit')
    # def _compute_total_profit(self):
    #     """Compute total profit for the entire sale order."""
    #     for order in self.mapped('order_id'):
    #         order.total_profit = sum(order.order_line.mapped('profit'))
    #
# class SaleReport(models.Model):
#     _inherit = 'sale.report'
#
#     sub_categ_id = fields.Many2one(
#         comodel_name='product.category', string="Product Category", readonly=True)
#
#     @api.depends_context('allowed_company_ids')
#     def _compute_currency_id(self):
#         self.currency_id = self.env.company.currency_id
#
#     def _with_sale(self):
#         return ""
#
#     def _select_sale(self):
#         select_ = f"""
#             MIN(l.id) AS id,
#             l.product_id AS product_id,
#             l.invoice_status AS line_invoice_status,
#             t.uom_id AS product_uom,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS product_uom_qty,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_delivered / u.factor * u2.factor) ELSE 0 END AS qty_delivered,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM((l.product_uom_qty - l.qty_delivered) / u.factor * u2.factor) ELSE 0 END AS qty_to_deliver,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END AS qty_invoiced,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END AS qty_to_invoice,
#             CASE WHEN l.product_id IS NOT NULL THEN AVG(l.price_unit
#                 / {self._case_value_or_one('s.currency_rate')}
#                 * {self._case_value_or_one('account_currency_table.rate')}
#                 ) ELSE 0
#             END AS price_unit,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_total
#                 / {self._case_value_or_one('s.currency_rate')}
#                 * {self._case_value_or_one('account_currency_table.rate')}
#                 ) ELSE 0
#             END AS price_total,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_subtotal
#                 / {self._case_value_or_one('s.currency_rate')}
#                 * {self._case_value_or_one('account_currency_table.rate')}
#                 ) ELSE 0
#             END AS price_subtotal,
#             CASE WHEN l.product_id IS NOT NULL OR l.is_downpayment THEN SUM(l.untaxed_amount_to_invoice
#                 / {self._case_value_or_one('s.currency_rate')}
#                 * {self._case_value_or_one('account_currency_table.rate')}
#                 ) ELSE 0
#             END AS untaxed_amount_to_invoice,
#             CASE WHEN l.product_id IS NOT NULL OR l.is_downpayment THEN SUM(l.untaxed_amount_invoiced
#                 / {self._case_value_or_one('s.currency_rate')}
#                 * {self._case_value_or_one('account_currency_table.rate')}
#                 ) ELSE 0
#             END AS untaxed_amount_invoiced,
#             COUNT(*) AS nbr,
#             s.name AS name,
#             s.date_order AS date,
#             s.state AS state,
#             s.invoice_status as invoice_status,
#             s.partner_id AS partner_id,
#             s.user_id AS user_id,
#             s.company_id AS company_id,
#             s.campaign_id AS campaign_id,
#             s.medium_id AS medium_id,
#             s.source_id AS source_id,
#             t.categ_id AS categ_id,
#             t.sub_categ_id AS sub_categ_id,
#             s.pricelist_id AS pricelist_id,
#             s.team_id AS team_id,
#             p.product_tmpl_id,
#             partner.commercial_partner_id AS commercial_partner_id,
#             partner.country_id AS country_id,
#             partner.industry_id AS industry_id,
#             partner.state_id AS state_id,
#             partner.zip AS partner_zip,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(p.weight * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS weight,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(p.volume * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS volume,
#             l.discount AS discount,
#             CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_unit * l.product_uom_qty * l.discount / 100.0
#                 / {self._case_value_or_one('s.currency_rate')}
#                 * {self._case_value_or_one('account_currency_table.rate')}
#                 ) ELSE 0
#             END AS discount_amount,
#             concat('sale.order', ',', s.id) AS order_reference"""
#
#         additional_fields_info = self._select_additional_fields()
#         template = """,
#             %s AS %s"""
#         for fname, query_info in additional_fields_info.items():
#             select_ += template % (query_info, fname)
#
#         return select_
#
#     def _case_value_or_one(self, value):
#         return f"""CASE COALESCE({value}, 0) WHEN 0 THEN 1.0 ELSE {value} END"""
#
#     def _select_additional_fields(self):
#         """Hook to return additional fields SQL specification for select part of the table query.
#
#         :returns: mapping field -> SQL computation of field, will be converted to '_ AS _field' in the final table definition
#         :rtype: dict
#         """
#         return {}
#
#     def _from_sale(self):
#         currency_table = self.env['res.currency']._get_simple_currency_table(self.env.companies)
#         currency_table = self.env.cr.mogrify(currency_table).decode(self.env.cr.connection.encoding)
#         return f"""
#             sale_order_line l
#             LEFT JOIN sale_order s ON s.id=l.order_id
#             JOIN res_partner partner ON s.partner_id = partner.id
#             LEFT JOIN product_product p ON l.product_id=p.id
#             LEFT JOIN product_template t ON p.product_tmpl_id=t.id
#             LEFT JOIN uom_uom u ON u.id=l.product_uom
#             LEFT JOIN uom_uom u2 ON u2.id=t.uom_id
#             JOIN {currency_table} ON account_currency_table.company_id = s.company_id
#             """
#
#     def _where_sale(self):
#         return """
#             l.display_type IS NULL"""
#
#     def _group_by_sale(self):
#         return """
#             l.product_id,
#             l.order_id,
#             l.price_unit,
#             l.invoice_status,
#             t.uom_id,
#             t.categ_id,
#             t.sub_categ_id,
#             s.name,
#             s.date_order,
#             s.partner_id,
#             s.user_id,
#             s.state,
#             s.invoice_status,
#             s.company_id,
#             s.campaign_id,
#             s.medium_id,
#             s.source_id,
#             s.pricelist_id,
#             s.team_id,
#             p.product_tmpl_id,
#             partner.commercial_partner_id,
#             partner.country_id,
#             partner.industry_id,
#             partner.state_id,
#             partner.zip,
#             l.is_downpayment,
#             l.discount,
#             s.id,
#             account_currency_table.rate"""
#
#     def _query(self):
#         with_ = self._with_sale()
#         return f"""
#             {"WITH" + with_ + "(" if with_ else ""}
#             SELECT {self._select_sale()}
#             FROM {self._from_sale()}
#             WHERE {self._where_sale()}
#             GROUP BY {self._group_by_sale()}
#             {")" if with_ else ""}
#         """
#
#     @property
#     def _table_query(self):
#         return self._query()
#
#     def action_open_order(self):
#         self.ensure_one()
#         return {
#             'res_model': self.order_reference._name,
#             'type': 'ir.actions.act_window',
#             'views': [[False, 'form']],
#             'res_id': self.order_reference.id,
#         }



class ResPartner(models.Model):
   _inherit = 'res.partner'
   adhar_no = fields.Char(string="Adhar Number",size=12)
   @api.model
   def name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
       domain = expression.AND([[('mobile', operator, name)], args or []])
       records = self.search_fetch(domain, ['mobile'], limit=limit)
       return [(record.id, record.display_name) for record in records.sudo()]

   @api.constrains('adhar_no')  # Ensure correct field name
   def _check_aadhar_number(self):
       for record in self:
           if record.adhar_no and not re.fullmatch(r'\d{12}', record.adhar_no):
               raise ValidationError(_("Aadhar Number must be exactly 12 digits and contain only numbers."))

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # margin = fields.Monetary("Margin", compute='_compute_margin', store=True)
    # margin_percent = fields.Float("Margin (%)", compute='_compute_margin', store=True, aggregator="avg")
    mobile = fields.Char(related='partner_id.mobile', string='Mobile Number', readonly=True, store=True)
    adhar = fields.Char(related='partner_id.adhar_no',string="Adhar Number", store=True,copy=True)



    # total_profit = fields.Float(string="Total Profit", compute="_compute_total_profit", store=True)
    #
    # @api.depends('order_line.profit')
    # def _compute_total_profit(self):
    #     """Compute total profit for the entire sale order."""
    #     for order in self:
    #         order.total_profit = sum(order.order_line.mapped('profit'))

    def action_print_invoice(self):
        """Finds the invoice linked to the sale order and calls the print function."""
        self.ensure_one()  # Ensure a single record is processed

        invoice = self.invoice_ids.filtered(lambda inv: inv.state in ['posted', 'draft'])

        if not invoice:
            raise UserError(
                "No invoice found for this Sale Order! Please ensure the invoice is created and in Draft or Posted state.")

        # Get the print report function from `account.move`
        return self.env.ref('custom_report.action_report_pos_invoice').report_action(invoice)
    def action_a4_print_invoice(self):
        """Finds the invoice linked to the sale order and calls the print function."""
        self.ensure_one()  # Ensure a single record is processed

        invoice = self.invoice_ids.filtered(lambda inv: inv.state in ['posted', 'draft'])

        if not invoice:
            raise UserError(
                "No invoice found for this Sale Order! Please ensure the invoice is created and in Draft or Posted state.")

        # Get the print report function from `account.move`
        return self.env.ref('account.account_invoices').report_action(invoice)







# class ProductProduct(models.Model):
#     _inherit = "product.product"
#
#     @api.depends('name', 'default_code', 'product_tmpl_id', 'qty_available')
#     @api.depends_context('display_default_code', 'seller_id', 'company_id', 'partner_id')
#     def _compute_display_name(self):
#
#         def get_display_name(name, code, qty):
#             qty_display = f" -- Available: {qty}" if qty is not None else ""
#             if self._context.get('display_default_code', True) and code:
#                 return f'[{code}] {name}{qty_display}'
#             return f"{name}{qty_display}"
#
#         partner_id = self._context.get('partner_id')
#         if partner_id:
#             partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
#         else:
#             partner_ids = []
#         company_id = self.env.context.get('company_id')
#
#         self.check_access("read")
#
#         product_template_ids = self.sudo().product_tmpl_id.ids
#
#         if partner_ids:
#             supplier_info = self.env['product.supplierinfo'].sudo().search_fetch(
#                 [('product_tmpl_id', 'in', product_template_ids), ('partner_id', 'in', partner_ids)],
#                 ['product_tmpl_id', 'product_id', 'company_id', 'product_name', 'product_code'],
#             )
#             supplier_info_by_template = {}
#             for r in supplier_info:
#                 supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
#
#         # Fetch qty_available in batch for performance optimization
#         qty_available_dict = {
#             rec['id']: rec['qty_available']
#             for rec in self.sudo().read(['qty_available'])
#         }
#
#         for product in self.sudo():
#             variant = product.product_template_attribute_value_ids._get_combination_name()
#             name = variant and "%s (%s)" % (product.name, variant) or product.name
#             qty_available = qty_available_dict.get(product.id, 0)  # Get quantity from precomputed dict
#
#             sellers = self.env['product.supplierinfo'].sudo().browse(self.env.context.get('seller_id')) or []
#             if not sellers and partner_ids:
#                 product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
#                 sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
#                 if not sellers:
#                     sellers = [x for x in product_supplier_info if not x.product_id]
#                 if company_id:
#                     sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
#
#             if sellers:
#                 temp = []
#                 for s in sellers:
#                     seller_variant = s.product_name and (
#                             variant and "%s (%s)" % (s.product_name, variant) or s.product_name
#                     ) or False
#                     temp.append(get_display_name(seller_variant or name, s.product_code or product.default_code,
#                                                  qty_available))
#
#                 product.display_name = ", ".join(set(temp))  # Use set to avoid duplicates
#             else:
#                 product.display_name = get_display_name(name, product.default_code, qty_available)
#
#
# class ProductTemplate(models.Model):
#     _inherit = "product.template"
#
#     sub_categ_id = fields.Many2one(
#         'product.category', 'Product Sub Category')
#     a_percentage = fields.Float(string="A (%)", store=True)
#     b_percentage = fields.Float(string="B (%)", store=True)
#     c_percentage = fields.Float(string="C (%)", store=True)
#     d_percentage = fields.Float(string="D (%)", store=True)
#
#     margin_percentage = fields.Float(
#         string="Margin (%)",
#         compute="_compute_margin_percentage",
#         store=True
#     )
#
#     @api.depends('standard_price', 'list_price')
#     def _compute_margin_percentage(self):
#         """ Calculate the margin percentage """
#         for product in self:
#             if product.standard_price is None or product.standard_price <= 0:
#                 product.margin_percentage = 0.0
#             elif product.list_price:  # Avoid division by zero
#                 product.margin_percentage = ((product.list_price - product.standard_price) / product.list_price) * 100
#             else:
#                 product.margin_percentage = 0.0
#
#     @api.onchange('margin_percentage')
#     def _onchange_margin_percentage(self):
#         """ Automatically update sub-category based on margin percentage and defined thresholds """
#         categories = self.env['product.category'].search([('name', 'in', ['A', 'B', 'C', 'D'])])
#
#         # Create a dictionary for category lookup
#         category_map = {cat.name: cat.id for cat in categories}
#
#         for product in self:
#             if product.margin_percentage >= product.a_percentage and 'A' in category_map:
#                 product.sub_categ_id = category_map['A']  # Margin >= A → Category A
#             elif product.b_percentage <= product.margin_percentage < product.a_percentage and 'B' in category_map:
#                 product.sub_categ_id = category_map['B']  # B ≤ Margin < A → Category B
#             elif product.c_percentage <= product.margin_percentage < product.b_percentage and 'C' in category_map:
#                 product.sub_categ_id = category_map['C']  # C ≤ Margin < B → Category C
#             elif product.margin_percentage < product.c_percentage and 'D' in category_map:
#                 product.sub_categ_id = category_map['D']  # Margin < C → Category D
#             else:
#                 product.sub_categ_id = False  # No valid category found, reset it
#
#     @api.depends('name', 'default_code', 'qty_available')
#     def _compute_display_name(self):
#         for template in self:
#             if not template.name:
#                 template.display_name = False
#             else:
#                 template.display_name = "{} {}--AVAILABLE : {}".format(
#                     "[%s] " % template.default_code if template.default_code else "",
#                     template.name,
#                     int(template.qty_available)  # Convert to integer for cleaner display
#                 )
#

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    price_unit = fields.Float(string ="Unit price",compute='_compute_unit_price', store=True)
    price_subtotal = fields.Monetary(
        string="Subtotal",
        store=True,
        readonly=False                # Allow manual entry
    )


    @api.depends('product_qty','price_subtotal')
    def _compute_unit_price(self):
        print("welcome")
        """When the user changes price_subtotal, auto-update price_unit."""
        for line in self:
            if line.product_qty > 0:
                line.price_unit = line.price_subtotal / line.product_qty

