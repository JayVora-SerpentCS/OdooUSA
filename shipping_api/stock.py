# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import time
from openerp import models, fields, api
from openerp import netsvc
import openerp.addons.decimal_precision as dp


class stock_picking(models.Model):
    _inherit = "stock.picking"
    default = {}

    @api.multi
    def onchange_logis_company(self, logistic_company_id):
        company_code = ''
        if logistic_company_id:
            logistic_company_obj = self.env['logistic.company']
            company_code = logistic_company_obj.browse(logistic_company_id).ship_company_code
        res = {'value': {'ship_company_code': company_code}}
        return res

    @api.multi
    def distribute_weight(self):
        package_obj = self.env['stock.packages'].search([])
        pack_ids_list = self.read(['packages_ids', 'tot_del_order_weight'])
        for pack_ids in pack_ids_list:
            if pack_ids['tot_del_order_weight'] and pack_ids['packages_ids']:
                avg_weight = pack_ids['tot_del_order_weight'] / len(pack_ids['packages_ids'])
                package_obj.write({'weight': avg_weight})
        return True

    @api.one
    @api.depends('packages_ids')
    def _total_weight_net(self):
        result = 0.0
        for line in self.packages_ids:
            if line.weight:
                result += line.weight
        self.tot_ship_weight = result

    @api.one
    @api.depends('move_lines', 'product_id')
    def _total_ord_weight_net(self):
        result = 0.0
        for line in self.move_lines:
            if line.product_id:
                result += line.product_qty * line.product_id.weight_net
        self.tot_del_order_weight = result

    @api.model
    def _get_move_order(self):
        """Get the picking ids of the given Stock Moves."""
        result = {}
        for line in self.env['stock.move'].browse(self._ids):
            result[line.picking_id.id] = True
        return result.keys()

    @api.model
    def _get_company_code(self):
        return []
    logis_company = fields.Many2one('logistic.company', string='Logistics Company', help='Name of the Logistics company providing the shipper services.')
    freight = fields.Boolean(string='Shipment', help='Indicates if the shipment is a freight shipment.')
    sat_delivery = fields.Boolean(string='Saturday Delivery', help='Indicates is it is appropriate to send delivery on Saturday.')
    package_type = fields.Selection([
                        ('01', 'Letter'),
                        ('02', 'Customer Supplied Package'),
                        ('03', 'Tube'),
                        ('04', 'PAK'),
                        ('21', 'ExpressBox'),
                        ('24', '25KG Box'),
                        ('25', '10KG Box'),
                        ('30', 'Pallet'),
                        ('2a', 'Small Express Box'),
                        ('2b', 'Medium Express Box'),
                        ('2c', 'Large Express Box')
                        ], string='Package Type', help='Indicates the type of package')
    bill_shipping = fields.Selection([
                            ('shipper', 'Shipper'),
                            ('receiver', 'Receiver'),
                            ('thirdparty', 'Third Party')
                            ], string='Bill Shipping to', default='shipper', help='Shipper, Receiver, or Third Party.')
    with_ret_service = fields.Boolean(string='With Return Services', help='Include Return Shipping Information in the package.')
    tot_ship_weight = fields.Float(compute='_total_weight_net', digits=(16, 3), store=True, string='Total Shipment Weight',
                                    help="Adds the Total Weight of all the packages in the Packages Table.")
    tot_del_order_weight = fields.Float(compute='_total_ord_weight_net', string='Total Order Weight', store=True,
                                             help="Adds the Total Weight of all the packages in the Packages Table.")
    packages_ids = fields.One2many("stock.packages", 'pick_id',
                                   string='Packages Table')
    ship_state = fields.Selection([
                        ('draft', 'Draft'),
                        ('in_process', 'In Process'),
                        ('ready_pick', 'Ready for Pickup'),
                        ('shipped', 'Shipped'),
                        ('delivered', 'Delivered'),
                        ('void', 'Void'),
                        ('hold', 'Hold'),
                        ('cancelled', 'Cancelled')
                        ], 'Shipping Status', default='draft', readonly=True,
                                  help='The current status of the shipment')
    trade_mark = fields.Text(string='Trademarks AREA')
    ship_message = fields.Text(string='Message')
    address_validate = fields.Selection([
                            ('validate', 'Validate'),
                            ('nonvalidate', 'No Validation')
                            ], 'Address Validation', default='nonvalidate', help=''' No Validation = No address validation.
                                      Validate = Fail on failed address validation.
                                      Defaults to validate. Note: Full address validation is not performed. Therefore, it is
                                      the responsibility of the Shipping Tool User to ensure the address entered is correct to
                                      avoid an address correction fee.''')
    ship_description = fields.Text(string='Description')
    ship_from = fields.Boolean(string='Ship From', help='Required if pickup location is different from the shipper\'s address..')
    ship_from_tax_id_no = fields.Char(string='Identification Number', size=30)
    shipcharge = fields.Float(string='Shipping Cost', readonly=True)
    ship_from_address = fields.Many2one('res.partner',
                                        string='Ship From Address',
                                        size=30)
    address = fields.Many2one('res.partner', 'Ship From Address')
    sale_id = fields.Many2one('sale.order', string='Sale Order')
    tot_order_weight = fields.Float(related='sale_id.total_weight_net',
                                    string='Total Order Weight')
    comm_inv = fields.Boolean(string='Commercial Invoice', default=False)
    cer_orig = fields.Boolean(string='U.S. Certificate of Origin',
                              default=False)
    nafta_cer_orig = fields.Boolean(string='NAFTA Certificate of Origin',
                                    default=False)
    sed = fields.Boolean(string='Shipper Export Declaration (SED)',
                         default=False)
    prod_option = fields.Selection([
                                ('01', 'AVAILABLE TO CUSTOMS UPON REQUEST'),
                                ('02', 'SAME AS EXPORTER'),
                                ('03', 'ATTACHED LIST'),
                                ('04', 'UNKNOWN'),
                                (' ', ' ')
                                ], string='Option')
    prod_company = fields.Char(string='CompanyName', size=256, help='Only applicable when producer option is empty or not present.')
    prod_tax_id_no = fields.Char(string='TaxIdentificationNumber', size=256, help='Only applicable when producer option is empty or not present.')
    prod_address_id = fields.Many2one('res.partner', string='Producer Address', help='Only applicable when producer option is empty or not present.')
    inv_option = fields.Selection([
                                ('01', 'Unknown'),
                                ('02', 'Various'),
                                (' ', ' ')
                                ], string='Sold to Option')
    inv_company = fields.Char(string='CompanyName', size=256, help='Only applicable when Sold to option is empty or not present.')
    inv_tax_id_no = fields.Char(string='TaxIdentificationNumber', size=256, help='Only applicable when Sold to option is empty or not present.')
    inv_att_name = fields.Char(string='AttentionName', size=256, help='Only applicable when Sold to option is empty or not present.')
    inv_address_id = fields.Many2one('res.partner', string='Sold To Address', help='Only applicable when Sold to option is empty or not present.')
    blanket_begin_date = fields.Date(string='Blanket Begin Date')
    blanket_end_date = fields.Date(string='Blanket End Date')
    comm_code = fields.Char(string='Commodity Code', size=256,)
    exp_carrier = fields.Char(string='ExportingCarrier', size=256)
    ship_company_code = fields.Selection(_get_company_code,
                                         string='Ship Company',
                                         size=64)
    ship_charge = fields.Float(string='Value', default=0.0,
                               digits_compute=dp.get_precision('Account'))
    stock_pick_ids = fields.Many2one('stock.packages', string="Stock Pick ids")

    @api.v7
    def process_ship(self, cr, uid, ids, context=None):
        return True

    @api.multi
    def print_labels(self):
        ids = self._ids
        if not ids: return []
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'shipping_api.report_multiple_label_picking',
            'datas': {
                'model': 'stock.packages',
                'id': ids and ids[0] or False,
                'ids': ids,
                'report_type': 'pdf'
                },
            'nodestroy': True
        }

    @api.multi
    def print_packing_slips(self):
        ids = self._ids
        if not ids: return []
        packages_ids = []
        for package in self.browse(ids).packages_ids[0]:
            packages_ids.append(package.id)
        datas = {
            'model': 'stock.packages',
                     'id': ids and ids[0] or False,
                     'ids': packages_ids,
                     'report_type': 'pdf'
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'shipping_api.report_packing_slip_stock_packages',
            'datas': datas,
            }

    @api.multi
    def process_void(self):
        return True

    @api.multi
    def cancel_ship(self):
        self.write({'ship_state': 'cancelled'})
        return True

    @api.multi
    def _get_account_analytic_invoice(self, cursor, user, picking, move_line):
        partner_id = picking.partner_id and picking.partner_id.id or False
        analytic_obj = self.env['account.analytic.default']
        rec = analytic_obj.account_get(move_line.product_id.id, partner_id,
                                       time.strftime('%Y-%m-%d'))
        if rec:
            return rec.analytic_id.id
        return super(stock_picking, self)._get_account_analytic_invoice(picking, move_line)

    @api.multi
    def send_conf_mail(self):
        ids = self._ids
        for id in ids:
            obj = self.browse(ids)
            if obj and obj.address_id and obj.address_id.email:
                email_temp_obj = self.env['email.template']
                template_id = email_temp_obj.search([('object_name.model', '=', 'stock.picking'), ('ship_mail', '=', True)])
                if template_id:
                    template_obj_list = email_temp_obj.browse(template_id)
                    for template_obj in template_obj_list:
                        subj = self.get_value(obj, template_obj, 'def_subject') or ''
                        vals = {
                          'email_to': self.get_value(obj, template_obj.def_to) or '',
                          'body_text': self.get_value(obj, template_obj.def_body_text) or '',
                          'body_html': self.get_value(obj, template_obj.def_body_html) or '',
                          'account_id': template_obj.from_account.id,
                          'folder': 'outbox',
                          'state': 'na',
                          'subject': self.get_value(obj, template_obj.def_subject) or '',
                          'email_cc': self.get_value(obj, template_obj.def_cc) or '',
                          'email_bcc': self.get_value(obj, template_obj.def_bcc) or '',
                          'email_from': template_obj.from_account.email_id or '',
                          'reply_to': self.get_value(obj, template_obj.reply_to) or '' ,
                          'date_mail': time.strftime('%Y-%m-%d %H:%M:%S'),
                          }
                        if vals['email_to'] and vals['account_id']:
                            mail_id = self.env['email_template.mailbox'].create(vals)
                            data = {}
                            data['model'] = 'stock.picking'
                            if template_obj.report_template:
                                reportname = 'report.' + self.env['ir.actions.report.xml'].read(template_obj.report_template.id,
                                                                                                     ['report_name'])['report_name']
                                service = netsvc.LocalService(reportname)
                                (result, format) = service.create(id, data)
                                email_temp_obj._add_attachment(mail_id, subj, base64.b64encode(result),
                                                               template_obj.file_name or 'Order.pdf')
        return True


class stock_move(models.Model):
    _inherit = "stock.move"
    package_id = fields.Many2one('stock.packages', string='Package',
                                 help='Indicates the package')
    cost = fields.Float(string='Value', digits_compute=dp.get_precision('Account'))

    @api.v7
    def onchange_quantity(self, cr, uid, ids, product_id, product_uom_qty, product_uom, product_uos, sale_line_id = False):
        result = super(stock_move, self).onchange_quantity(cr, uid, ids,product_id, product_uom_qty, product_uom, product_uos)
        if product_id:
            product = self.pool.get('product.product').browse(cr,uid,product_id)
            if sale_line_id:
                sale_unit_price = self.pool.get('sale.order.line').browse(cr,uid,sale_line_id).price_unit
                price = sale_unit_price * product_uom_qty
            else:
                price = product.list_price * product_uom_qty
            result['value'].update({'cost': price})
        return result

class Prod(models.Model):
    _inherit = 'product.product'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context
        if context is None:
            context = {}

        if context.get('move_type', 'p') == 'package' and context.get('move_ids'):
            picks = self.env['stock.packages'].browse(context.get('move_ids')).pick_id
            if picks:
                p_ids = [x.product_id.id for x in picks.move_lines]
                args += [('id', 'in', p_ids)]

        return super(Prod, self).search(args, offset, limit, order, count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
