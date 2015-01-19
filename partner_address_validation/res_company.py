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

class res_company(models.Model):

    _description = 'Companies'
    _inherit='res.company'
    '''
    Address Validation Method on company
    '''
    @api.model
    def _method_get(self):
        list = [("none", "None")]
        ups_acc_obj = self.env['ups.account']
        fedex_acc_obj = self.env['fedex.account']
        usps_acc_obj = self.env['usps.account']
        ups_ids = ups_acc_obj.search([])
        fedex_ids = fedex_acc_obj.search([])
        usps_ids = usps_acc_obj.search([])
    
        if ups_ids:
            list.append(('ups.account','UPS'))
            
        if fedex_ids:
            list.append(('fedex.account','FedEx'))
            
        if usps_ids:
            list.append(('usps.account','USPS'))
        return list
    
    
    address_validation_method = fields.Selection('_method_get', string='Address Validation Method', default='none', required=True)

