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

{
    'name': 'Partner Address Validation',
    'version': '2.5',
    'category': 'Generic Modules/Others',
    'description': """
        Module for providing the Address Validation
    """,
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': ' http://www.serpentcs.com',
    'depends': ['base', 'sale'],
    'data': [ 
        
        "wizard/saleorder_validation_view.xml",
        "wizard/response_data_view.xml",
        "wizard/address_validate_view.xml",
        "partner_address_validation_view.xml",
        "res_company_view.xml",
        "security/ir.model.access.csv",
        "validation_account_view.xml",
    ],
    'demo': [],
    'test':['partner_address_validation.yml'],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
