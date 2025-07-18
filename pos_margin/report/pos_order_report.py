# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    margin_rate = fields.Float(string="Margin Rate (%)", group_operator="avg")

    def _select(self):
        res = super()._select()
        res += """
            , CASE 
                WHEN SUM(l.price_subtotal) = 0 THEN 0
                ELSE ROUND(SUM(
                    (l.price_subtotal - (l.total_cost / 
                        CASE 
                            WHEN COALESCE(s.currency_rate, 0) = 0 THEN 1.0 
                            ELSE s.currency_rate 
                        END)
                    ) 
                ) / NULLIF(SUM(l.price_subtotal), 0) * 100, 2)
              END AS margin_rate
        """
        return res

    def _group_by(self):
        res = super()._group_by()
        # Avoid grouping by subtotal and cost directly since aggregate already used
        # So, you **do not need to append** `l.price_subtotal, l.total_cost` in most cases
        return res