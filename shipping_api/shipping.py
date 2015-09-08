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


from openerp import models, fields, api


class shipping_move(models.Model):
    _name = "shipping.move"
    _rec_name = 'pick_id'
    pick_id = fields.Many2one("stock.picking", string='Delivery Order')
    pic_date = fields.Datetime(string='Pickup Date')
    ship_date = fields.Datetime(string='Shipping Date')
    logis_company = fields.Many2one('res.company', string='Logistics Company',
                                    help='Name of the Logistics company providing the shipper services.')
    package_weight = fields.Float(string='Package Weight')
    state = fields.Selection([
                        ('draft', 'Draft'),
                        ('in_process', 'In Process'),
                        ('ready_pick', 'Ready for Pickup'),
                        ('shipped', 'Shipped'),
                        ('delivered', 'Delivered'),
                        ('hold', 'Hold'),
                        ('void', 'Void'),
                        ('cancelled', 'Cancelled')
                        ], string='Shipping Status', readonly=True, help='The current status of the shipment')
    tracking_no = fields.Char(string='Tracking', size=128,)
    ship_to = fields.Many2one('res.partner', string='Ship To')
    package = fields.Char(string='Package', size=128)
    ship_cost = fields.Float(string='Shipment Cost')
    ship_from = fields.Many2one('res.partner', string='Ship From' )
    freight = fields.Boolean(string='Shipment', help='Indicates if the shipment is a freight shipment.')
    sat_delivery = fields.Boolean(string='Saturday Delivery',
                                  help='Indicates is it is appropriate to send delivery on Saturday.')
    package_type = fields.Selection([('', '')], string='Package Type',
                                    help='Indicates the type of package')
    bill_shipping = fields.Selection([('shipper', 'Shipper'),
                                      ('receiver', 'Receiver'),
                                      ('thirdparty', 'Third Party')],
                                     string='Bill Shipping to',
                                     default='shipper',
                                     help='Shipper, Receiver, or Third Party.')
    with_ret_service = fields.Boolean(string='With Return Services',
                                      help='Include Return Shipping Information in the package.')
    trade_mark = fields.Text(string='Trademarks AREA')
    packages_ids = fields.One2many("stock.packages", 'ship_move_id',
                                   string='Packages Table')
    partner_id = fields.Many2one("res.partner", string='Customer/Reseller')
    sale_id = fields.Many2one('sale.order', string='Sale Order')

    @api.multi
    def write(self, vals):
        res = super(shipping_move, self).write(vals)

        if 'state' in vals:
            pick_ids = []
            if 'pick_id' in vals:
                pick_ids.append(vals['pick_id'])
            else:
                for log_obj in self.browse(ids):
                    if log_obj.pick_id:
                        pick_ids.append(log_obj.pick_id.id)
            self.env['stock.picking'].write({'ship_state': vals['state']})
        return res

    @api.model
    def create(self, vals):
        move_id = super(shipping_move, self).create(vals)
        if 'state' in vals:
            pick_ids = []
            if 'pick_id' in vals:
                pick_ids.append(vals['pick_id'])
                self.env['stock.picking'].write({'ship_state': vals['state']})
        return move_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
