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

class ups_account_shipping(models.Model):
    
    _name = "ups.account.shipping"

    name =                  fields.Char(string='Name', size=64, required=True)
    ups_account_id =        fields.Many2one('ups.account', string='UPS Account', required=True)
    accesslicensenumber =   fields.Char(related='ups_account_id.accesslicensenumber', size=64, string='AccessLicenseNumber')
    userid =                fields.Char(related='ups_account_id.userid', string='UserId', size=64)
    password =              fields.Char(related='ups_account_id.password', size=64, string='Password')
    active =                fields.Boolean(related='ups_account_id.ups_active', string='Active', default=True)
    acc_no =                fields.Char(related='ups_account_id.acc_no', string='Account Number',size=64)
    atten_name =            fields.Char(string='AttentionName', size=64, required=True)
    tax_id_no =             fields.Char(string='Tax Identification Number', size=64, help="Shipper's Tax Identification Number.")
    logistic_company_id =   fields.Many2one('logistic.company', string='Parent Logistic Company')
#   'ups_shipping_service_ids': fields.one2many('ups.shipping.service.type', 'ups_account_id', 'Shipping Service')
    ups_shipping_service_ids =  fields.Many2many('ups.shipping.service.type', 'shipping_service_rel', 'ups_account_id', 'service_id', string='Shipping Service')
    address =                   fields.Many2one('res.partner', string="Shipper Address")
    trademark =                 fields.Char(string='Trademark', size=1024)
    company_id =                fields.Many2one('res.company', string='Company')

    @api.multi
    def onchange_ups_account(self, ups_account_id=False):
        res = {
            'accesslicensenumber': '',
            'userid': '',
            'password': '',
            'active': True,
            'acc_no': ''
            }
        
        if ups_account_id:
            ups_account = self.env['ups.account'].browse(ups_account_id)
            res = {
                'accesslicensenumber': ups_account.accesslicensenumber,
                'userid': ups_account.userid,
                'password': ups_account.password,
                'active': ups_account.ups_active,
                'acc_no': ups_account.acc_no
                }
        return {'value': res}


class ups_account_shipping_service(models.Model):
    
    _name = "ups.shipping.service.type"
    _rec_name = "description"
    
    description =           fields.Char(string='Description', size=32, required=True)
    category =              fields.Char(string='Category', size=32)
    shipping_service_code = fields.Char(string='Shipping Service Code', size=8)
    rating_service_code =   fields.Char(string='Rating Service Code', size=8)
    ups_account_id =        fields.Many2one('ups.account.shipping', string='Parent Shipping Account')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
