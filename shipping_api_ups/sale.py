# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Serpent Consulting Services PVT. LTD. (<http://www.serpentcs.com>) 
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, fields, api

class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def action_ship_create(self):
        pick_obj = self.env['stock.picking']
        result = super(sale_order, self).action_ship_create()
        if result:
            for sale in self.browse(self._ids):
                if sale.ship_company_code == 'ups':
#                    pick_ids = pick_obj.search([('sale_id', '=', sale.id), ('type', '=', 'out')])
                    pick_ids = pick_obj.search([('sale_id', '=', sale.id)])
                    if pick_ids:
                        vals = {
                            'ship_company_code': 'ups',
                            'logis_company': sale.logis_company and sale.logis_company.id or False,
                            'shipper': sale.ups_shipper_id and sale.ups_shipper_id.id or False,
                            'ups_service': sale.ups_service_id and sale.ups_service_id.id or False,
                            'ups_pickup_type': sale.ups_pickup_type,
                            'ups_packaging_type': sale.ups_packaging_type and sale.ups_packaging_type.id or False,
                            'ship_from_address':sale.ups_shipper_id and sale.ups_shipper_id.address and sale.ups_shipper_id.address.id or False,
                            'shipcharge':sale.shipcharge or False
                            }
                        pick_ids.write(vals)
                else:
                    pick_ids = pick_obj.search([('sale_id', '=', sale.id)])
                    if pick_ids:
                        pick_ids.write({'shipper': False, 'ups_service': False})
        return result
    
    @api.model
    def _get_company_code(self):
        res = super(sale_order, self)._get_company_code()
        res.append(('ups', 'UPS'))
        return res
    
    @api.multi
    def _get_sale_account(self):
        context=self._context
        if context is None:
            context = {}
        logsitic_obj = self.env['logistic.company']
        user_rec = self.env['res.users'].browse(self._ids)
        logis_company = logsitic_obj.search([])
        return logis_company[0].ship_account_id.id
    
    @api.multi
    def onchage_service(self, ups_shipper_id):
        vals = {}
        service_type_ids = []
        if ups_shipper_id:
            shipper_obj = self.env['ups.account.shipping'].browse(ups_shipper_id)
            for shipper in shipper_obj.ups_shipping_service_ids:
                service_type_ids.append(shipper.id)
        domain = [('id', 'in', service_type_ids)]
        return {'domain': {'ups_service_id': domain}}
    
    
    payment_method =    fields.Selection([
                            ('cc_pre_auth', 'Credit Card – PreAuthorized'),
                            ('invoice', 'Invoice'),
                            ('cod', 'COD'),
                            ('p_i_a', 'Pay In Advance'),
                            ('pay_pal', 'Paypal'),
                            ('no_charge', 'No Charge')], string='Payment Method')
    ship_company_code = fields.Selection(_get_company_code, string='Logistic Company', size=64)
    ups_shipper_id =    fields.Many2one('ups.account.shipping', string='Shipper')
    ups_service_id =    fields.Many2one('ups.shipping.service.type', string='Service Type')
    ups_pickup_type =   fields.Selection([ 
                            ('01', 'Daily Pickup'),
                            ('03', 'Customer Counter'),
                            ('06', 'One Time Pickup'),
                            ('07', 'On Call Air'),
                            ('11', 'Suggested Retail Rates'),
                            ('19', 'Letter Center'),
                            ('20', 'Air Service Center')], string='Pickup Type')
    ups_packaging_type = fields.Many2one('shipping.package.type', string='Packaging Type')
    sale_account_id =    fields.Many2one('account.account', string='Shipping Account', default=_get_sale_account,
                                           help='This account represents the g/l account for booking shipping income.')
    partner_shipping_id = fields.Many2one('res.partner', string='Shipping Address')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
