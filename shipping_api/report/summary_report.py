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


from openerp.osv import osv
import time
from openerp.report import report_sxw


class summary_report_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(summary_report_print, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_total': self.get_total,
            'get_items': self.get_items,
        })

    def get_total(self):
        ship_ids = self.pool.get('shipping.move').search(self.cr, self.uid, [('state', '=', 'ready_pick')])
        return str(len(ship_ids))

    def get_items(self):
        ret = {}
        ship_ids = self.pool.get('shipping.move').search(self.cr, self.uid, [('state', '=', 'ready_pick')])
        if ship_ids:
            for ship_id in self.pool.get('shipping.move').browse(self.cr, self.uid, ship_ids):
                key = ship_id.service and ship_id.service.description or ''
                ret[key] = 1 + ret.get(key, 0)
        return ret.items()


class report_summary_shipping_move(osv.AbstractModel):
    _name = 'report.shipping_api.report_summary_shipping_move'
    _inherit = 'report.abstract_report'
    _template = 'shipping_api.report_summary_shipping_move'
    _wrapped_report_class = summary_report_print


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: