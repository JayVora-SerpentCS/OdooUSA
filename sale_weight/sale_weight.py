# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""Compute the net weight of sale orders."""
from openerp import models, fields, api

class sale_order(models.Model):
    """Add the total net weight to the object "Sale Order"."""
    
    _inherit = "sale.order"

    @api.one
    @api.depends('order_line')
    def _total_weight_net(self):
       
        """Compute the total net weight of the given Sale Orders."""
        result = 0.0
        for line in self.order_line:
            if line.product_id:
                result += line.weight_net or 0.0
        self.total_weight_net = result



    total_weight_net = fields.Float(compute='_total_weight_net', readonly=True, store=True,
        string='Total Weight', help="The cumulated net weight of all the order lines.")

# Record the net weight of the order line
class sale_order_line(models.Model):
    """Add the net weight to the object "Sale Order Line"."""
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('product_id', 'product_id.weight', 'product_uom_qty', 'product_uom', 'th_weight')
    def _weight_net(self):
        """Compute the net weight of the given Sale Order Lines."""
        result=0.0
        if self.product_id:
            if self.product_id.weight_net:
                result += (self.product_id.weight_net * self.product_uom_qty / self.product_uom.factor)
            else:
                result += (self.th_weight * self.product_uom_qty / self.product_uom.factor)
        
        self.weight_net = result
        

    weight_net = fields.Float(compute='_weight_net', readonly=True, string='Net Weight', store=True, help="The net weight")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
