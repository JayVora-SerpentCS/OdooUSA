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
    'name' : 'Total net weight of an order',
    'description': '''
            Adds the total net weight of the order form.
    ''',
    'version' : '2.1',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': ' http://www.serpentcs.com',
    'category': 'Generic Modules/Sales & Purchases',
    'depends': ['sale'],
    'demo': [],
    'data': ['sale_weight_view.xml'],
    'test':['sale.yml'],
    'active': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
