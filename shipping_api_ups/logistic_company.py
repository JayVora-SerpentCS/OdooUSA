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
import re

class logistic_company(models.Model):
    _inherit="logistic.company"
    
    @api.model
    def _get_company_code(self):
        res =  super(logistic_company, self)._get_company_code()
        res.append(('ups', 'UPS'))
        return res

    ship_company_code =     fields.Selection(_get_company_code, string='Logistic Company', required=True, size=64)
    ship_req_web =          fields.Char(string='Ship Request Website', size=256 )
    ship_req_port =         fields.Integer(string='Ship Request Port')
    ship_req_test_web =     fields.Char(string='Test Ship Request Website', size=256 )
    ship_req_test_port =    fields.Integer(string='Test Ship Request Port')
    ship_accpt_web =        fields.Char(string='Ship Accept Website', size=256 )
    ship_accpt_port =       fields.Integer(string='Ship Accept Port' )
    ship_accpt_test_web =   fields.Char(string='Test Ship Accept Website', size=256)
    ship_accpt_test_port =  fields.Integer(string='Test Ship Accept Port')
    ship_void_web =         fields.Char(string='Ship Void Website', size=256)
    ship_void_port =        fields.Integer(string='Ship Void Port')
    ship_void_test_web =    fields.Char(string='Test Ship Void Website', size=256)
    ship_void_test_port =   fields.Integer(string='Test Ship Void Port')
    ship_tracking_url =     fields.Char(string='Tracking URL', size=256)
    ups_shipping_account_ids = fields.One2many('ups.account.shipping', 'logistic_company_id', string='Shipping Account')
    
    @api.multi
    def onchange_shipping_number(self, shipping_no, url):
        ret = {}
        if url:
            b = url[url.rindex('/'): len(url)]
            b = b.strip('/')
            if re.match("^[0-9]*$", b):
                url = url[0:url.rindex('/')]
            url += ('/' + shipping_no)
            ret['url'] = url
        return{'value': ret}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: