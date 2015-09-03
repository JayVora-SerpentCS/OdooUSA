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
import time


class address_validation_response_data(models.TransientModel):
    '''
    Class to store address details returned from ups
    '''
    _name = "response.data.model"
    _rec_name = "street1"

    street1 = fields.Char(string='Street1', required=True, select=1)
    city = fields.Char(string='City', required=True, select=1)
    state = fields.Char(string='State', required=True, select=1)
    zip = fields.Char(string='Zip', required=True, select=1)
    classification = fields.Selection([('', ''), ('0', 'Unknown'), ('1', 'Commercial'), ('2','Residential')], string='Classification')
    so_validate_inv = fields.Many2one("so.addr_validate", string="Sale Order Validate")
    so_validate_ord = fields.Many2one("so.addr_validate", string="Sale Order Validate")
    so_validate_ship = fields.Many2one("so.addr_validate", string="Sale Order Validate")
    so_validate = fields.Integer(string="Sale Order Validate")
    select = fields.Boolean(string="Select")


class partner_addr_validate(models.TransientModel):
    '''
    Wizard object to validate address of partner address
    '''
    _name = "partner.addr_validate"
    _description = "Partner Address Validate"
#    _rec_name = 'inv_error_msg'

    @api.model
    def clean_memory(self, cr, uid):
        resp_env = self.env['response.data.model']
        resp_ids = resp_env.search([])
        resp_env.unlink(resp_ids)
        return True

    @api.model
    def get_state(self, state):  # not required any more
        """ Returns the state_id,by taking the state code as an argument """
        states = self.env['res.country.state'].search(['|',('name','=',state),('code','=',state)])
        return states and states[0] or False

    @api.model
    def get_zip(self, zip, state, city):  # not required any more
        """ Returns the id of the correct address.zip model """
        state_id = self.get_state(state)
        ids = self.env['address.zip'].search([('zipcode', '=', zip),
                                             ('state_id', '=', state_id),
                                             ('city', '=', city)])
        return ids

    @api.multi
    def do_write(self, cr, uid, address_id, address_list, context={}):
        address_vals = {}
#         cr = self._cr
        context = self._context

        for address_item in address_list:
            if address_item.select:
                state = address_item.state
                state_id = self.get_state(state)
                address_vals = {
                    'street': address_item.street1,
                    'city': address_item.city,
                    'state_id': state_id,
                    'last_address_validation': time.strftime('%Y-%m-%d'),
                    'classification': address_item.classification,
                    'zip': address_item.zip
                }
#                zip_id=self.get_zip(cr, uid,address_item.zip,state,address_item.city)
#                if len(zip_id) == 1:
#                    address_vals['zip_id'] = zip_id[0]
#                    address_vals['zip'] = address_item.zip
                break
#        address_vals and self.pool.get('res.partner').write(cr,uid,address_id, address_vals)
        part_obj = self.env['res.partner'].browse(context['active_id'])
        address_vals and part_obj.write(address_vals)
#        cr.commit()
        self.clean_memory()
        return True

    @api.multi
    def update_address(self):
        """ To write the selected address to the partner address form """
        ids = self._ids
        datas = self.browse(ids)
        for data in datas:
            self.do_write(data.address_list)
        return {}

    @api.multi
    def onchange_update(self, default_addr_id):
        ret = {}
        if default_addr_id:
            address_item = self.env['res.partner'].browse(default_addr_id)
            if address_item.address_validation_method is 'none':
                return {'value': ret}
            inv_return_data = self.env[address_item.address_validation_method].address_validation(default_addr_id)
            ret['error_msg'] = inv_return_data['error_msg']
            ret['address_list'] = inv_return_data['address_list']
            ret['address_id'] = default_addr_id
        return {'value': ret}
    error_msg = fields.Text(string='Error Message')
    address_list = fields.One2many('response.data.model', 'so_validate', string='Address List')
    address_id = fields.Many2one('res.partner', string='Address')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
