from odoo.addons.portal.controllers import portal
from odoo import http, fields
from odoo.http import route, request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalAnnouncement(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "portal_announcement" in counters:
            count = request.env["portal.announcement"].search_count([])
            values["portal_announcement"] = count
        return values

    @route(["/my/announcement", "/my/announcement/page/<int:page>"], type="http", auth="user", website=True)
    def portal_announcement_form_view(self, page=1, **kw):
        # Elevate privileges for hr.leave model operations
        checkout = request.env["portal.announcement"].sudo()
        user = request.env.user

        # domain = [('employee_id.user_id', '=', request.env.uid)]
        domain = []

        # Prepare pager data
        checkout_count = checkout.search_count(domain)
        pager_data = portal.pager(
            url="/my/announcement",
            total=checkout_count,
            page=page,
            step=self._items_per_page,
        )

        # Recordset according to pager and domain filter
        checkouts = checkout.search(domain, limit=self._items_per_page, offset=pager_data["offset"])

        # Prepare template values and render
        values = self._prepare_portal_layout_values()

        values.update({
            "checkouts": checkouts,
            "page_name": "portal_announcement",
            "default_url": "/my/announcement",
            "pager": pager_data,
            "user": user,
        })

        return request.render("pk_advance_employee_portal.portal_announcement_list_view_temp_id", values)

    @http.route(["/my/announcement-list/<model('portal.announcement'):doc>"], type="http", auth="user", website=True)
    def portal_announcement_list_view(self, doc, **kw):
        # Prepare template values for the detailed view of the announcement
        doc = doc.sudo()
        vals = {
            'doc': doc,  # The individual announcement record
            "user": request.env.user,
            "page_name": "portal_announcement",  # Set the page name to show the breadcrumb
        }

        return request.render("pk_advance_employee_portal.portal_announcement_form_view_temp_id", vals)


