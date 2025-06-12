from odoo import http
from odoo.http import route, request
from odoo.addons.portal.controllers import portal


class SopCustomerPortal(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "sop_checkout_count" in counters:
            count = request.env["sop.violation"].search_count([])
            values["sop_checkout_count"] = count
        return values

    @route(["/sop/violations", "/sop/violations/page/<int:page>"],type="http", auth="user", website=True, )
    def portal_violation_sop_form_view(self, page=1, **kw):
        checkout = request.env["sop.violation"].sudo()

        domain = [('employee_id.user_id', '=', request.env.uid)]

        # Prepare pager data
        checkout_count = checkout.search_count(domain)
        pager_data = portal.pager(
            url="/sop/violations",
            total=checkout_count,
            page=page,
            step=self._items_per_page,
        )
        # Recordset according to pager and domain filter
        checkouts = checkout.search(domain, limit=self._items_per_page, offset=pager_data["offset"], )
         # Prepare template values and render
        values = self._prepare_portal_layout_values()

        values.update({"checkouts": checkouts,
                       "page_name": "sop_violation",
                       "default_url": "/sop/violations",
                       "pager": pager_data,
                       "user": request.env.user})
        return request.render("pk_advance_employee_portal.sop_violation_form_view_temp_id", values)

    @http.route(["/sop/violations/form/<model('hr.leave'):leave_id>"],type="http", auth="user", website=True)
    def portal_violation_sop_list_view(self, leave_id, **kw):
        vals = {'doc':leave_id, "user": request.env.user}
        return request.render("pk_advance_employee_portal.sop_violation_list_view_temp_id", vals)
