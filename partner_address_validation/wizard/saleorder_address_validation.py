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
import time
# import pdb


class so_addr_validate(models.TransientModel):
    '''
    Wizard object to validate address of sale order
    '''
    _name = "so.addr_validate"
    _description = "Sale order Address Validate"
    _rec_name = 'inv_error_msg'

    @api.model
    def clean_memory(self):
        resp_env = self.env['response.data.model']
        resp_ids = resp_env.search([])
        resp_env.unlink()
        add_ids = self.search([])
        self.unlink()
        return True

    @api.multi
    def get_state(self, state):  # not required any more
        """ Returns the state_id,by taking the state code as an argumrnt """
        states = self.env['res.country.state'].search(['|', ('name','=',state), ('code','=',state)])
        return states and states[0] or False

    @api.multi
    def get_zip(self, zip, state, city):  # not required any more
        """ Returns the id of the correct address.zip model """
        state_id = self.get_state(state)
        ids = self.env['address.zip'].search([('zipcode','=',zip),('state_id','=',state_id),('city','=',city)])
        return ids

    @api.multi
    def do_write(self, address_id, address_list):
        address_vals = {}
        context=self._context
        for address_item in address_list:
            if address_item.select:
                state = address_item.state
                state_id = self.get_state(state)
                address_vals = {'street': address_item.street1,
                                'city': address_item.city,
                                'state_id': state_id,
                                'last_address_validation': time.strftime('%Y-%m-%d'),
                                'classification': address_item.classification,
                                'zip': address_item.zip
                                }
#                zip_id=self.get_zip(cr, uid,address_item.zip,state,address_item.city)
#                if len(zip_id) == 1:
#                    address_vals['zip_id'] = zip_id[0]
                break
#                    address_vals['zip'] = address_item.zip
#        res_obj=self.env['res.partner'].browse(address_id)
        part_obj = self.env['res.partner'].browse(address_id)
        address_vals and part_obj.write(address_vals)
        return True

    @api.multi
    def update_address(self):
        ids = self._ids
        datas = self.browse(ids)
        for data in datas:
            self.do_write(data.inv_address_id.id, data.inv_address_list)
            if data.inv_address_id.id != data.ord_address_id.id:
                self.do_write(data.ord_address_id.id, data.ord_address_list)
            if data.inv_address_id.id != data.ship_address_id.id and data.ord_address_id.id != data.ship_address_id.id:
                self.do_write(data.ship_address_id.id, data.ship_address_list)
        self.clean_memory()
        return {}

    @api.multi
    def onchange_update(self, sale_id):
            ret = {}
            if sale_id:
                sale_obj=self.env['sale.order'].browse(sale_id)
                res_obj= sale_obj.read(['partner_invoice_id', 'partner_shipping_id','address_validation_method', 'partner_id'])
            for res in res_obj:
                inv_addr_id = res['partner_invoice_id'][0]
                ord_addr_id = res['partner_id']
                ship_addr_id = res['partner_shipping_id'][0]
                validation_method = res['address_validation_method']
                inv_return_data = self.env[validation_method].address_validation(inv_addr_id)
                print '-----', inv_return_data
                
                if inv_return_data['address_list']:
                    inv_return_data['address_list'][0]['select']=True
                ret['inv_error_msg'] = inv_return_data['error_msg']
                if inv_return_data['address_list']:
                    ret['inv_address_list'] = inv_return_data['address_list']
               
                if inv_addr_id == ord_addr_id:
                    ord_return_data = inv_return_data
               
                if inv_addr_id == ship_addr_id:
                    ship_return_data = inv_return_data
                elif ord_addr_id == ship_addr_id:
                    ship_return_data = ord_return_data
                else:
                    ship_return_data = self.env[validation_method].address_validation(ship_addr_id)
                    if ship_return_data['address_list']:
                        ship_return_data['address_list'][0]['select']=True
                ret['ship_error_msg'] = ship_return_data['error_msg']
                if ship_return_data['address_list']:
                    ret['ship_address_list'] = ship_return_data['address_list']

                ret['inv_address_id'] = inv_addr_id
                ret['ord_address_id'] = ord_addr_id
                ret['ship_address_id'] = ship_addr_id
            return {'value':ret}


    update_field =      fields.Boolean(string='Update')
    sale_id =           fields.Many2one('sale.order','Sale Order')

    inv_error_msg =     fields.Text(string='Status', size=35 , readonly= True)
    ord_error_msg =     fields.Text(string='Status' ,size=35, readonly= True)
    ship_error_msg =    fields.Text(string='Status' ,size=35 ,readonly= True)

    inv_address_list =  fields.One2many('response.data.model','so_validate_inv', string='Invoice Address List')
    ord_address_list =  fields.One2many('response.data.model','so_validate_ord', string='Order Address List')
    ship_address_list=  fields.One2many('response.data.model','so_validate_ship', string='Ship Address List')

    inv_address_id =    fields.Many2one('res.partner', string='Invoice Address')
    ord_address_id =    fields.Many2one('res.partner', string='Order Address')
    ship_address_id =   fields.Many2one('res.partner', string='Ship Address')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: