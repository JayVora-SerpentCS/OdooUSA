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

from openerp import models, fields, api, _
from openerp.osv import fields as oldFields
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class sale_order(models.Model):
    _inherit = "sale.order"

    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_id = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        if inv_id:
            if order.sale_account_id:
                inv_obj = self.pool.get('account.invoice')
                inv_obj.write({
                    'shipcharge': order.shipcharge,
                    'ship_method': order.ship_method,
                    'ship_method_id': order.ship_method_id.id,
                    'sale_account_id': order.sale_account_id.id,
                    })
                inv_obj.button_reset_taxes([inv_id])
        return inv_id

    @api.model
    def _amount_shipment_tax(self, shipment_taxes, shipment_charge):
        val = 0.0
        for c in self.env['account.tax'].compute_all(shipment_taxes, shipment_charge, 1)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
    @api.v7
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = super(sale_order, self)._amount_all(cr, uid, ids, field_name, arg, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            cur = order.pricelist_id.currency_id
            tax_ids = order.ship_method_id and order.ship_method_id.shipment_tax_ids
            if tax_ids:
                val = self._amount_shipment_tax(cr, uid, tax_ids, order.shipcharge)
                res[order.id]['amount_tax'] += cur_obj.round(cr, uid, cur, val)
                res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + order.shipcharge
            elif order.shipcharge:
                res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + order.shipcharge
        return res
    
    @api.v7
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    @api.multi
    def view_for_shipping_rate_wizard(self):
        if str(self.address_validation_method) == 'fedex.account':
            ir_model_data = self.env['ir.model.data']
            form_id = ir_model_data.get_object_reference('sale_negotiated_shipping', 'view_for_shipping_rate_wizard')[1]
            return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'shipping.rate.wizard',
                    'views': [(form_id, 'form')],
                    'view_id': form_id,
                    'target': 'new',
                    }
        else:
            raise Warning(_("Please configure a fedex account in setting < Address Validation Method < FedEx Account"))
    shipcharge = fields.Float(string='Shipping Cost', readonly=True)
    ship_method = fields.Char(string='Ship Method', size=128, readonly=True)
    ship_method_id = fields.Many2one('shipping.rate.config', string='Shipping Method', readonly=True)
    sale_account_id = fields.Many2one('account.account', string='Shipping Account',
                                       help='This account represents the g/l account for booking shipping income.')

    _columns = {
        'amount_total': oldFields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'shipcharge'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
 
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
