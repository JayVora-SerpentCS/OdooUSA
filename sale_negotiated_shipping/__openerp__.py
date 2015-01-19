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

{
    'name': 'Sale Negotiated Shipping',
    'version': '2.5',
    'category': 'Generic Modules/Logistics Management',
    'description': """
    """,
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': ' http://www.serpentcs.com',
    'depends': ['sale_weight','stock'],
    'data': [
       'sale_nagotiated_shipping_view.xml' ,
       'wizard/shipping_rate_view.xml',
       'sale_view.xml',
       'stock_view.xml',
       'security/ir.model.access.csv',
       'invoice_view.xml'
    ],
    'demo': [],
    'test': ['account_invoice.yml','sale_negotiate_shipping.yml','sale_negotiated_shipping.yml'],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: