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
from openerp.tools.translate import _


class res_partner(models.Model):
    _description ='Partner Addresses'
    _inherit='res.partner'

    @api.model
    def _method_get(self):
        list = [('none', ''), ("", "")]
        ups_acc_obj = self.env['ups.account']
        fedex_acc_obj = self.env['fedex.account']
        usps_acc_obj = self.env['usps.account']
        ups_ids = ups_acc_obj.search([])
        fedex_ids = fedex_acc_obj.search([])
        usps_ids = usps_acc_obj.search([])

        if ups_ids:
            list.append(('ups.account', 'UPS'))

        if fedex_ids:
            list.append(('fedex.account', 'FedEx'))

        if usps_ids:
            list.append(('usps.account', 'USPS'))
        return list
    last_address_validation = fields.Date(string='Last Address Validation', readonly=True)
    address_validation_method = fields.Selection(_method_get, string='Address Validation Method')
    classification = fields.Selection([('', ''), ('0', 'Unknown'), ('1', 'Commercial'), ('2','Residential')], string='Classification')
    '''
    Change the address disply as us format
    '''

    @api.model
    def _get_address_validation_method(self):
        ids = self._ids
        user = self.env['res.users'].browse(ids)
        return user and user.company_id and user.company_id.address_validation_method
#    _defaults = {
#        'address_validation_method': _get_address_validation_method,
#    }


class sale_order(models.Model):
    _inherit = 'sale.order'
    '''
    Add address validation fields on sale order
    '''

    @api.model
    def _method_get(self):
        list = [('none',''),("", "")]
        ups_acc_obj = self.env['ups.account']
        fedex_acc_obj = self.env['fedex.account']
        usps_acc_obj = self.env['usps.account']
        ups_ids = ups_acc_obj.search([])
        fedex_ids = fedex_acc_obj.search([])
        usps_ids = usps_acc_obj.search([])

        if ups_ids:
            list.append(('ups.account', 'UPS'))

        if fedex_ids:
            list.append(('fedex.account', 'FedEx'))

        if usps_ids:
            list.append(('usps.account', 'USPS'))
        return list

    @api.model
    def so_addr_validate_wiz(self):
        ids = self._ids
        context = self._context
#        obj_model = self.env['ir.model.data']
#        model_data_ids = obj_model.search([('model','=','ir.ui.view'),('name','=','view_so_addrvalidate')])
#        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        obj_model = self.env['ir.model.data'].search([('model','=','ir.ui.view'),('name','=','view_so_addrvalidate')])
        resource_id = obj_model.read(['res_id'])[0]
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'so.addr_validate',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    @api.one
    @api.depends('partner_invoice_id.last_address_validation', 'partner_shipping_id.last_address_validation')
    def _validated(self):
        res = False
        if self.partner_invoice_id.last_address_validation and self.partner_shipping_id.last_address_validation:
            res = True
        self.hide_validate = res

    @api.model
    def _get_address_validation_method(self):
        ids = self._ids
        context = self._context
        if context is None:
            context = {}
        user = self.env['res.users'].browse(ids)
        return user and user.company_id and user.company_id.address_validation_method
    hide_validate = fields.Boolean(compute='_validated', string='Hide Validate', store=False)
    address_validation_method = fields.Selection(_method_get, string='Address Validation Method',
                                                 default=_get_address_validation_method)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
