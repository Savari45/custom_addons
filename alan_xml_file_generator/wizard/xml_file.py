from odoo import models, fields, api
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from xml.sax.saxutils import escape
import base64
from odoo.fields import Date

class GenerateXMLReport(models.TransientModel):
    _name = 'generate.xml.report'
    _description = 'Generate the XML Report'

    start_date = fields.Date(string="Start Date" )
    end_date = fields.Date(string="End Date")
    file_data = fields.Binary(string="Report", readonly=True)
    file_name = fields.Char()
    @api.constrains('start_date', 'end_date')
    def _check_date_constraints(self):
        for rec in self:
            if not rec.start_date or not rec.end_date:
                raise UserError("Both start date and end date are required.")
            if rec.start_date > rec.end_date:
                raise UserError("Start date cannot be greater than the end date.")
    def prettify_xml(self, element):
        """
        Prettify XML for human readability.
        """
        rough_string = ET.tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="        ")
    def validate_company(self):
        """Validate essential company details."""
        company = self.env.company
        if not company:
            raise UserError("No company is configured.")
        if not company.vat:
            raise UserError("Tax Registration Number (VAT) is missing for the company.")
        if not company.street:
            raise UserError("Company address is incomplete (Street is missing).")
        if not company.currency_id or not company.currency_id.name:
            raise UserError("Company currency is not set.")
        return company

    def get_fiscal_year(self, target_date=None):
        target_date = target_date or fields.Date.today()
        fiscal_year = self.env['account.fiscal.year'].search([
            ('date_from', '<=', target_date),
            ('date_to', '>=', target_date),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if fiscal_year:
            return fiscal_year.name
        return str(target_date.year)



    def generate_header(self,root, company):
        address = company.street
        # Split the address by space to extract the number
        address_parts = address.split()
        # The first part is the number
        number = address_parts[0]
        building_number = escape(number) if number else ''
        config = self.env['ir.config_parameter'].sudo()

        software_validation_number = config.get_param('software.validation.number') or 'N/A'
        product_id = config.get_param('product.id') or 'Odoo ERP / Default'
        product_version = config.get_param('product.version') or '18.0'
        # Create Header section
        header = ET.SubElement(root, 'Header')
        ET.SubElement(header, 'AuditFileVersion').text = '1.01_01'
        ET.SubElement(header, 'CompanyID').text = '5000803960'
        ET.SubElement(header,
                      'TaxRegistrationNumber').text = company.vat or ''  # Assuming 'vat' holds the tax registration number
        ET.SubElement(header, 'TaxAccountingBasis').text = 'F'  # Assuming 'F' for tax accounting basis
        ET.SubElement(header, 'CompanyName').text = company.name or ''
        ET.SubElement(header, 'BusinessName').text = company.name or ''

        # Create Company Address Section
        company_address = ET.SubElement(header, 'CompanyAddress')
        ET.SubElement(company_address, 'BuildingNumber').text = escape(building_number)
        ET.SubElement(company_address, 'StreetName').text = company.street or ''
        ET.SubElement(company_address,
                      'AddressDetail').text = company.street or ''  # You can adjust to include more address details
        ET.SubElement(company_address, 'City').text = company.city or ''
        ET.SubElement(company_address, 'PostalCode').text = company.zip or ''  # Assuming postal code is in 'zip'
        ET.SubElement(company_address,
                      'Province').text = company.state_id.name or ''  # Assuming the state is in 'state_id'
        ET.SubElement(company_address, 'Country').text = company.country_id.name or ''
        ET.SubElement(header, 'FiscalYear').text = self.get_fiscal_year(self.start_date)
        ET.SubElement(header, 'StartDate').text = self.start_date.strftime("%d-%m-%Y")
        ET.SubElement(header, 'EndDate').text = self.end_date.strftime("%d-%m-%Y")
        ET.SubElement(header, 'CurrencyCode').text = escape(company.currency_id.name)
        ET.SubElement(header, 'DateCreated').text = Date.today().strftime('%d-%m-%Y')
        ET.SubElement(header, 'TaxEntity').text = company.country_id.name or 'Global'
        ET.SubElement(header, 'ProductCompanyTaxID').text = company.vat or ''
        ET.SubElement(header, 'SoftwareValidationNumber').text = software_validation_number
        ET.SubElement(header, 'ProductID').text = product_id
        ET.SubElement(header, 'ProductVersion').text = product_version
        ET.SubElement(header, 'Telephone').text = company.phone
        ET.SubElement(header, 'Mobile').text = company.mobile or ' '
        ET.SubElement(header, 'Email').text = company.email
        ET.SubElement(header, 'Website').text = company.website

    def generate_customers(self, transactions):
        """Generate customer details with validations."""

        customer_ids = self.env['res.partner'].search([('type', '=', 'contact')])
        for customer in customer_ids:
            street = customer.street or ''
            street_parts = street.split()
            building_number = street_parts[0] if street_parts else ''

            # Add customer details
            customer_details = ET.SubElement(transactions, 'CustomerDetails')
            ET.SubElement(customer_details, 'CustomerID').text = str(customer.id) or ''
            ET.SubElement(customer_details, 'AccountID').text = customer.property_account_receivable_id.code or ''
            ET.SubElement(customer_details, 'CustomerTaxID').text = customer.vat or ''
            ET.SubElement(customer_details, 'CustomerName').text = customer.name or ''
            ET.SubElement(customer_details, 'CustomerPhone').text = customer.phone or ''
            ET.SubElement(customer_details, 'CustomerEmail').text = customer.email or ''

            # Billing Address
            billing_address = ET.SubElement(customer_details, 'BillingAddress')
            billing_ids = self.env['res.partner'].search([
                ('type', '=', 'invoice'),
                ('parent_id', '=', customer.id)
            ])

            billing_partner = billing_ids[:1] if billing_ids else customer  # Take first billing address if exists

            billing_street = billing_partner.street or ''
            billing_parts = billing_street.split()
            billing_building_number = billing_parts[0] if billing_parts else building_number

            ET.SubElement(billing_address, 'BillingName').text = billing_partner.name or ''
            ET.SubElement(billing_address, 'AdressDetails').text = billing_street
            ET.SubElement(billing_address, 'BuildingNumber').text = billing_building_number
            ET.SubElement(billing_address, 'City').text = billing_partner.city or ''
            ET.SubElement(billing_address,
                          'State').text = billing_partner.state_id.name if billing_partner.state_id else ''
            ET.SubElement(billing_address, 'PostalCode').text = billing_partner.zip or ''
            ET.SubElement(billing_address,
                          'CountryName').text = billing_partner.country_id.name if billing_partner.country_id else ''

            # Shipping Address
            shipping_address = ET.SubElement(customer_details, 'ShippingAddress')
            delivery_ids = self.env['res.partner'].search([
                ('type', '=', 'delivery'),
                ('parent_id', '=', customer.id)
            ])

            delivery_partner = delivery_ids[:1] if delivery_ids else customer  # Take first delivery address if exists

            shipping_street = delivery_partner.street or ''
            shipping_parts = shipping_street.split()
            shipping_building_number = shipping_parts[0] if shipping_parts else building_number

            ET.SubElement(shipping_address, 'ShipToCustomer').text = delivery_partner.name or ''
            ET.SubElement(shipping_address, 'AddressDetails').text = shipping_street
            ET.SubElement(shipping_address, 'BuildingNumber').text = shipping_building_number
            ET.SubElement(shipping_address, 'City').text = delivery_partner.city or ''
            ET.SubElement(shipping_address,
                          'State').text = delivery_partner.state_id.name if delivery_partner.state_id else ''
            ET.SubElement(shipping_address, 'PostalCode').text = delivery_partner.zip or ''
            ET.SubElement(shipping_address,
                          'CountryName').text = delivery_partner.country_id.name if delivery_partner.country_id else ''

    def generate_products_xml(self, transactions):
        """
        Generates XML structure for products.
        """
        product_ids = self.env['product.template'].search([('type', '=', 'consu')])
        for product in product_ids:
            desc_name = str(product.description)
            description = desc_name.replace('<p>', '').replace('</p>', '')

            product_details = ET.SubElement(transactions, 'Product')
            ET.SubElement(product_details, 'ProductType').text = product.type
            ET.SubElement(product_details, 'ProductCode').text = product.default_code
            ET.SubElement(product_details, 'ProductGroup').text = product.categ_id.name
            ET.SubElement(product_details, 'ProductDescription').text = description
            ET.SubElement(product_details, 'ProductNumberCode').text = product.default_code

    def generate_tax_table_xml(self, transactions):
        """
        Generates XML structure for taxes.
        """
        tax_table = ET.SubElement(transactions, 'TaxTable')
        tax_ids = self.env['account.tax'].search([])
        for tax in tax_ids:
            desc_name = str(tax.description)
            description = desc_name.replace('<p>', '').replace('</p>', '')
            # Create TaxTableEntry for each tax
            tax_entry = ET.SubElement(tax_table, 'TaxTableEntry')
            ET.SubElement(tax_entry, 'TaxType').text = tax.type_tax_use or 'IVA'
            ET.SubElement(tax_entry, 'TaxCountryRegion').text = tax.country_id.name or ''
            ET.SubElement(tax_entry, 'TaxCode').text = ''
            ET.SubElement(tax_entry, 'Description').text = description or ''
            ET.SubElement(tax_entry, 'TaxAmountType').text = str(tax.amount_type) or ''
            ET.SubElement(tax_entry, 'TaxPercentage').text = str(tax.amount) or ''

    def generate_invoice_lines(self, root, company):

        source = ET.SubElement(root, 'SourceDocuments')
        sales_invoice = ET.SubElement(source, 'SalesInvoices')

        invoices_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                                                        ('invoice_date', '>=', self.start_date),
                                                        ('invoice_date', '<=', self.end_date)
                                                        ])
        number_of_entries = len(invoices_ids)
        total_debit = sum(invoice.amount_total_signed for invoice in invoices_ids if invoice.amount_total_signed < 0)
        total_credit = sum(invoice.amount_total_signed for invoice in invoices_ids if invoice.amount_total_signed > 0)
        ET.SubElement(sales_invoice, 'NumberOfEntries').text = str(number_of_entries)
        ET.SubElement(sales_invoice, 'TotalDebit').text = f"{total_debit:.2f}"
        ET.SubElement(sales_invoice, 'TotalCredit').text = f"{total_credit:.2f}"
        for invoice in invoices_ids:

            if invoice.invoice_origin:
                source_billing = 'P'
            else:
                source_billing = 'M'
            invoice_element = ET.SubElement(sales_invoice, 'Invoice')
            ET.SubElement(invoice_element, 'InvoiceNo').text = invoice.name or ''
            document_status = ET.SubElement(invoice_element, 'DocumentStatus')
            ET.SubElement(document_status, 'InvoiceStatus').text = 'N'
            ET.SubElement(document_status,
                          'InvoiceStatusDate').text = f"{invoice.create_date.strftime('%Y-%m-%dT%H:%M:%S')}"
            ET.SubElement(document_status, 'SourceID').text = invoice.create_uid.login or 'admin'
            ET.SubElement(document_status, 'SourceBilling').text = source_billing or ''

            # ET.SubElement(invoice_element, 'Hash').text = invoice.signature_code
            ET.SubElement(invoice_element, 'HashControl').text = "1"
            ET.SubElement(invoice_element, 'Period').text = str(invoice.invoice_date.month)
            ET.SubElement(invoice_element, 'InvoiceDate').text = str(invoice.invoice_date)
            ET.SubElement(invoice_element, 'InvoiceType').text = invoice.move_type

            # Special Regimes
            special_regimes = ET.SubElement(invoice_element, 'SpecialRegimes')
            # Self Billing
            self_billing = '1' if getattr(invoice.partner_id, 'self_billing', False) else '0'
            # Cash VAT
            cash_vat = any(
                tax.cash_basis_transition_account_id for line in invoice.invoice_line_ids for tax in line.tax_ids)
            cash_vat_indicator = '1' if cash_vat else '0'
            # Third Parties Billing
            third_party_billing = '1' if getattr(invoice, 'is_third_party_billing', False) else '0'

            ET.SubElement(special_regimes, 'SelfBillingIndicator').text = self_billing
            ET.SubElement(special_regimes, 'CashVATSchemeIndicator').text = cash_vat_indicator
            ET.SubElement(special_regimes, 'ThirdPartiesBillingIndicator').text = third_party_billing

            ET.SubElement(invoice_element, 'SourceID').text = invoice.create_uid.login or 'admin'
            ET.SubElement(invoice_element,
                          'SystemEntryDate').text = f"{invoice.create_date.strftime('%Y-%m-%dT%H:%M:%S')}"
            ET.SubElement(invoice_element, 'CustomerID').text = invoice.partner_id.name or 'Unknown'

            # ShipTo
            ship_to = ET.SubElement(invoice_element, 'ShipTo')
            delivery_date = ET.SubElement(ship_to, 'DeliveryDate')
            delivery_date.text = str(invoice.invoice_date)
            address = ET.SubElement(ship_to, 'Address')
            ET.SubElement(address, 'AddressDetail').text = str(invoice.partner_shipping_id.street) or ''
            ET.SubElement(address, 'City').text = str(invoice.partner_shipping_id.city) or ''
            ET.SubElement(address, 'PostalCode').text = str(invoice.partner_shipping_id.zip) or ''
            ET.SubElement(address, 'Country').text = str(invoice.partner_shipping_id.country_id.name) or ''

            # ship from
            ship_from = ET.SubElement(invoice_element, 'ShipFrom')
            delivery_date = ET.SubElement(ship_from, 'DeliveryDate')
            delivery_date.text = str(invoice.invoice_date)
            address = ET.SubElement(ship_from, 'Address')
            ET.SubElement(address, 'AddressDetail').text = str(company.street) or ''
            ET.SubElement(address, 'City').text = str(company.city) or ''
            ET.SubElement(address, 'PostalCode').text = str(company.zip) or ''
            ET.SubElement(address, 'Country').text = str(company.country_id.name) or ''

            ET.SubElement(invoice_element,
                          'MovementStartTime').text = f"{invoice.create_date.strftime('%Y-%m-%dT%H:%M:%S')}"

            for line in invoice.invoice_line_ids:

                 # Add the invoice lines
                line_element = ET.SubElement(invoice_element, 'Line')
                ET.SubElement(line_element, 'LineNumber').text = str(line.id)
                ET.SubElement(line_element, 'ProductCode').text = line.product_id.default_code or 'Nil'
                cleaned_description = (line.name or '').replace('\n', ' ').strip()
                ET.SubElement(line_element, 'ProductDescription').text = cleaned_description or 'Nil'
                ET.SubElement(line_element, 'Quantity').text = str(line.quantity)
                ET.SubElement(line_element, 'UnitOfMeasure').text = line.product_uom_id.name or ''
                ET.SubElement(line_element, 'UnitPrice').text = f"{line.price_unit:.2f}"
                ET.SubElement(line_element, 'TaxPointDate').text = str(invoice.invoice_date) if invoice.invoice_date else ''
                ET.SubElement(line_element, 'Description').text = cleaned_description or 'Nil'
                ET.SubElement(line_element, 'CreditAmount').text = f"{line.price_total:.2f}"

            # Add Tax Details
                for tax in line.tax_ids:
                    tax_element = ET.SubElement(line_element, 'Tax')
                    ET.SubElement(tax_element, 'TaxType').text = str(tax.amount_type) or 'Nil'
                    ET.SubElement(tax_element, 'TaxCountryRegion').text = str(tax.country_id.name) or 'Nil'
                    ET.SubElement(tax_element, 'TaxCode').text = 'NOR'
                    ET.SubElement(tax_element, 'TaxPercentage').text = str(tax.name)
                ET.SubElement(line_element, 'SettlementAmount').text = '00'


            document_totals = ET.SubElement(invoice_element, "DocumentTotals")
            ET.SubElement(document_totals, "TaxPayable").text = f"{invoice.amount_tax:.2f}"
            ET.SubElement(document_totals, "NetTotal").text = f"{invoice.amount_untaxed:.2f}"
            ET.SubElement(document_totals, "GrossTotal").text = f"{invoice.amount_total:.2f}"
            # WithholdingTax element
            withholding_tax = ET.SubElement(invoice_element, "WithholdingTax")
            ET.SubElement(withholding_tax, "WithholdingTaxType").text = "IRT"
            ET.SubElement(withholding_tax, "WithholdingTaxAmount").text = "00"

    def action_generate_report(self):
        """
        Generates an XML report for both sales and purchase with accounting details and saves it to a file.
        """
        # file_name = "/home/jagdish/Desktop/custom-18/Report_Encryption/sales_report.xml"
        company = self.env.company
        # company = self.env['res.company'].search([], limit=1)
        company.ensure_one()
        address = company.street
        # Split the address by space to extract the number (250)
        address_parts = address.split()
        # The first part is the number
        number = address_parts[0]
        building_number = escape(number) if number else ''

        root = ET.Element('AuditFile', xmlns="urn:OECD:StandardAuditFile-Tax:AO_1.01_01",
                          xmlns_xsd="http://www.w3.org/2001/XMLSchema",
                          xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance")
        self.generate_header(root, company)

        transactions = ET.SubElement(root, 'MasterFiles')
        self.generate_customers(transactions)
        self.generate_products_xml(transactions)
        self.generate_tax_table_xml(transactions)
        self.generate_invoice_lines(root, company)

        xml_string = self.prettify_xml(root)
        self.file_data = base64.b64encode(xml_string.encode('utf-8'))
        self.file_name = f"report_{fields.Date.today()}.xml"
        self.write({
            'file_data': self.file_data,
            'file_name': self.file_name,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Generate Wizard',
            'res_model': 'generate.xml.report',
            'view_mode': 'form',
            'res_id':self.id,
            'target': 'new',
        }
