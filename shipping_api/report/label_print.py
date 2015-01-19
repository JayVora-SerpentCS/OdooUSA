# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv
import time
from openerp.report import report_sxw

class report_print_label(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_label, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.localcontext.update({
            'time': time,
        })

class report_label_print_stock_packages(osv.AbstractModel):
    _name = 'report.shipping_api.report_label_print_stock_packages'
    _inherit = 'report.abstract_report'
    _template = 'shipping_api.report_label_print_stock_packages'
    _wrapped_report_class = report_print_label
#
#class report_label_print_shipping_move(osv.AbstractModel):
#    _name = 'report.shipping_api.report_label_print_shipping_move'
#    _inherit = 'report.abstract_report'
#    _template = 'shipping_api.report_label_print_shipping_move'
#    _wrapped_report_class = report_print_label
#
#class report_label_print_quick_ship(osv.AbstractModel):
#    _name = 'report.shipping_api.report_label_print_quick_ship'
#    _inherit = 'report.abstract_report'
#    _template = 'shipping_api.report_label_print_quick_ship'
#    _wrapped_report_class = report_print_label
#
#class report_label_print_stock_picking(osv.AbstractModel):
#    _name = 'report.shipping_api.report_label_print_stock_picking'
#    _inherit = 'report.abstract_report'
#    _template = 'shipping_api.report_label_print_stock_picking'
#    _wrapped_report_class = report_print_label


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: