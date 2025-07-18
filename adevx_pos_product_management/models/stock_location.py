from odoo import api, fields, models


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = ['stock.location', 'pos.load.mixin']

    def pos_update_stock_on_hand_by_location_id(self, vals={}):

        quant = self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': vals['product_id'],
            'location_id': vals['location_id'],
            'inventory_quantity': vals['quantity'],
        })
        quant.action_apply_inventory()
        location = self.env['stock.location'].browse(vals['location_id'])
        product = self.env['product.product'].with_context({'location': location.id}).browse(vals.get('product_id'))
        return {
            'location': location.name,
            'product': product.display_name,
            'quantity': product.qty_available
        }

    def _get_child_locations(self, location_id, location_ids=[]):
        location = self.browse(location_id)
        if location.child_ids:
            location_ids = list(set(location_ids + [child.id for child in location.child_ids]))
            for child in location.child_ids:
                if child.usage == 'internal':
                    child_location_ids = self._get_child_locations(child.id, location_ids)
                    location_ids = list(set(location_ids + child_location_ids))
        return location_ids

    @api.model
    def get_stock_datas_by_locationIds(self, product_ids=[], location_ids=[]):
        productHasRemovedIds = []
        stock_datas = {}
        for location_id in location_ids:
            stock_datas[location_id] = {}
            location_ids = self._get_child_locations(location_id, [])
            location_ids.append(location_id)
            if len(location_ids) == 1:
                location_ids.append(0)
            if len(product_ids) == 1:
                product_ids.append(0)
            if len(location_ids) == 0:
                continue
            if not product_ids:
                sql = "SELECT pp.id FROM product_product as pp, product_template as pt where pp.product_tmpl_id=pt.id and pt.type = 'consu'"
                self.env.cr.execute(sql)
                products = self.env.cr.dictfetchall()
                product_ids = [p.get('id') for p in products]
            for product_id in product_ids:
                sql = "SELECT sum(quantity - reserved_quantity) FROM stock_quant where location_id in %s AND product_id = %s"
                self.env.cr.execute(sql, (tuple(location_ids), product_id,))
                datas = self.env.cr.dictfetchall()
                stock_datas[location_id][product_id] = 0
                if datas and datas[0]:
                    if not datas[0].get('sum', None):
                        stock_datas[location_id][product_id] = 0
                    else:
                        stock_datas[location_id][product_id] = datas[0].get('sum')
                    self.env.cr.execute("select id from product_product where id=%s" % product_id)
                    datas = self.env.cr.dictfetchall()
                    if len(datas) != 1 and product_id != 0:
                        productHasRemovedIds.append(product_id)
                        continue
        return stock_datas

    @api.model
    def _load_pos_data_domain(self, config_id):
        config = self.env['pos.config'].browse(config_id)
        if config.multi_location:
            return [
                ("usage", "=", "internal"), "|",
                ("id", "in", [l.id for l in config.stock_location_ids]),
                ("id", "=", config.picking_type_id.default_location_src_id.id)
            ]
        else:
            return [
                ("id", "=", config.picking_type_id.default_location_src_id.id)
            ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ["name", "location_id", "company_id", "usage", "barcode", "display_name", ]
        return params

    def _load_pos_data(self, data):
        config_data = data.get('pos.config', {}).get('data', [{}])[0]
        if config_data.get('invoice_screen', False):  # Safe access
            domain = self._load_pos_data_domain(config_data.get('id'))
            fields = self._load_pos_data_fields(config_data.get('id'))

            return {
                'data': self.search_read(domain, fields, load=False),
                'fields': fields,
                'relations': {},  # 🔐 Ensure this exists!
            }

        # 🔐 Default safe return
        return {
            'data': [],
            'fields': [],
            'relations': {},
        }