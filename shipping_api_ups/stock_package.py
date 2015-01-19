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

class stock_packages(models.Model):
    _inherit = "stock.packages"
    
    @api.model
    def process_package(self):
        return True
    
    @api.one
    @api.depends('highvalue','decl_val')
    def _get_highvalue(self):
        res=0.0
        highvalue = False
        if self.decl_val >1000:
                res = highvalue
        self.highvalue = res
                
    shipment_digest =       fields.Text(string='ShipmentDigest')
    control_log_receipt =   fields.Binary(string='Control Log Receipt')
    highvalue =             fields.Boolean(compute='_get_highvalue', string='High Value')
    att_file_name =         fields.Char(string='File Name',size=128)

    @api.multi
    def print_control_receipt_log(self):
        ids=self._ids
        if not ids: return []
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'control.log.receipt.print',
            'datas': {
                'model': 'stock.packages',
                'id': ids and ids[0] or False,
                'ids': ids and ids or [],
                'report_type': 'pdf'
                },
            'nodestroy': True
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: