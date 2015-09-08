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


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_company_code(self):
        return [('fedex', 'FeDex')]

    @api.multi
    def onchange_logis_company(self, logistic_company_id):
        res = {}

        if logistic_company_id:
            logistic_company = self.env['logistic.company'].browse(logistic_company_id)
            res = {'value': {'ship_company_code': logistic_company.ship_company_code, 'sale_account_id': logistic_company.ship_account_id.id}}
        else:
            res = {'values': {}}
        return res

    @api.multi
    def _get_logis_company(self):
        context=self._context

        if context is None:
            context = {}
        user_rec = self.env['res.users'].browse(self._ids)
        logis_company = self.env['logistic.company'].search([])
        logis_company_id = False

        for val in logis_company:
            if not logis_company_ids:
                logis_company_id = val
                break
        return logis_company_id
    logis_company = fields.Many2one('logistic.company', string='Logistic Company',
    # default=_get_logis_company, 
                                        help='Name of the Logistics company providing the shipper services.')
    ship_company_code = fields.Selection(_get_company_code, string='Ship Company')
    rate_selection = fields.Selection([('rate_card', 'Rate Card'), ('rate_request', 'Rate Request')], string='Ship Rate Method')
    partner_order_id = fields.Many2one('res.partner', string='Ordering Contact', 
#                         default= lambda self : self._context.get('partner_id', False) and self.env['res.partner'].address_get(['partner_id'], ['order_contact'])['order_contact'],
                         readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The name and address of the contact who requested the order or quotation.")

    @api.multi
    def onchange_partner_id(self, part):
        addr = {}
        if part:
            addr = super(sale_order, self).onchange_partner_id(part)
            addr['value'].update({'partner_order_id': part})
        return addr


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        res = []
        ids = self._ids
        if type(ids) is not list:
            ids = list(ids)
        partners = self.browse(ids)
        for partner in partners:
            pname = partner.name
            res.append((partner.id, pname))
        return res
