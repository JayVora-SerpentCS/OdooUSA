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


class shipping_rate_wizard(models.TransientModel):
    _inherit = 'shipping.rate.wizard'

    @api.model
    def _get_company_code(self):
        return [('fedex', 'Fedex')]

    @api.multi
    def onchange_logis_company(self, logistic_company_id):
        company_code = ''
        if logistic_company_id:
            logis_comp_obj = self.env['logistic.company']
            company_code = logis_comp_obj.browse(logistic_company_id).ship_company_code
        res = {'value': {'ship_company_code': company_code}}
        return res

    @api.model
    def _get_rate_selection(self):
        context = self._context
        if context is None:
            context = {}
        if context.get('active_model', False) == 'sale.order':
            sale_id = context.get('active_id', False)
            if sale_id:
                sale = self.env['sale.order'].browse(sale_id)
                if sale.rate_selection:
                    return sale.rate_selection
                return sale.company_id and sale.company_id.rate_selection or 'rate_card'
        return 'rate_card'

    @api.model
    def default_get(self, fields):
        res = super(shipping_rate_wizard, self).default_get(fields)
        context = self._context
        if context is None:
            context = {}
        if context.get('active_model', False) == 'sale.order':
            sale_id = context.get('active_id', False)
            if sale_id:
                sale = self.env['sale.order'].browse(sale_id)
                res.update({
                    'logis_company': sale.logis_company and sale.logis_company.id or False,
                    'ship_company_code': sale.ship_company_code,
                    'shipping_cost': sale.shipcharge
                    })
        elif context.get('active_model', False) == 'account.invoice':
            inv_id = context.get('active_id', False)
            invoice = self.env['account.invoice'].browse(inv_id)
            if inv_id:
                res.update({
                    'shipping_cost': invoice.shipcharge
                    })
        return res

    @api.model
    def update_shipping_cost(self):
        data = self.browse(self._ids)
        context = self._context
        if context is None:
            context = {}
        if context.get('active_model', False) == 'sale.order':
            sale_id = context.get('active_id', False)
            if sale_id:
                self.env['sale.order'].write({'rate_selection': data.rate_selection})
        return super(shipping_rate_wizard, self).update_shipping_cost()

    @api.model
    def get_rate(self):
        return True
    rate_selection = fields.Selection([('rate_card', 'Rate Card'), ('rate_request', 'Rate Request')], default=_get_rate_selection, string='Ship Rate Method')
    logis_company = fields.Many2one('logistic.company', string='Shipper Company', help='Name of the Logistics company providing the shipper services.')
    ship_company_code = fields.Selection(_get_company_code, string='Ship Company')
    status_message = fields.Char(string='Status', size=128, readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: