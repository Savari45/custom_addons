from odoo import http
from odoo.http import route, request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "book_checkout_count" in counters:
            count = request.env["active.warning"].search_count([])
            values["active_warning_checkout_count"] = count
        return values

    @route(["/active/warnings", "/active/warnings/page/<int:page>"],type="http", auth="user", website=True, )
    def portal_active_warning_list_view(self, page=1, **kw):
        checkout = request.env["active.warning"].sudo()

        domain = [('employee_id.user_id', '=', request.env.uid)]

        # Prepare pager data
        checkout_count = checkout.search_count(domain)
        pager_data = portal.pager(
            url="/active/warnings",
            total=checkout_count,
            page=page,
            step=self._items_per_page,
        )
        # Recordset according to pager and domain filter
        checkouts = checkout.search(domain, limit=self._items_per_page, offset=pager_data["offset"], )
         # Prepare template values and render
        values = self._prepare_portal_layout_values()

        values.update({"checkouts": checkouts,
                       "page_name": "active_warning",
                       "default_url": "/active/warnings",
                       "pager": pager_data,
                       "user": request.env.user})
        return request.render("pk_advance_employee_portal.active_warning_form_view_temp_id", values)

    @http.route(["/active/warning/<model('hr.leave'):leave_id>"],type="http", auth="user", website=True)
    def portal_active_warning_form_view(self, leave_id, **kw):
        vals = {'doc':leave_id, "user": request.env.user}
        return request.render("pk_advance_employee_portal.active_warning_form_view_temp_id", vals)
