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

class logistic_company(models.Model):
    _name = "logistic.company"
    
    @api.model
    def _get_company_code(self):
        return []
    
    name =              fields.Char(string='Name', size=32, required=True, select=1)
    ship_company_code = fields.Selection(_get_company_code, string='Logistic Company')
    url =               fields.Char(string='Website',size=256 , select=1)
    company_id =        fields.Many2one('res.company', string='Company')
    test_mode =         fields.Boolean(string='Test Mode')
    ship_account_id =   fields.Many2one('account.account', string="Ship Account")
    note =              fields.Text('Notes')


class logistic_company_service_type(models.Model):
    _name = "logistic.company.service.type"
    
    name =                  fields.Char(string='Service Name', size=32, required=True)
    logistic_company_id =   fields.Many2one('logistic.company', string='Logistic Company')
    code =                  fields.Char(string='Service Code', size=32)
    description =           fields.Char(string='Description', size=128)



class logistic_company_package_type(models.Model):
    
    _name = "logistic.company.package.type"
    
    name =                  fields.Char(string='Package Name', size=32, required=True)
    logistic_company_id =   fields.Many2one('logistic.company', string='Logistic Company')
    code =                  fields.Char(string='Package Code', size=32)
    description =           fields.Char(string='Description', size=128)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
