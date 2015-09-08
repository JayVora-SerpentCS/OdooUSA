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

from openerp import models, fields, api


class shipping_package_type(models.Model):
    _name = 'shipping.package.type'
    name = fields.Char(string='Package Type', size=32, required=True)
    code = fields.Char(string='Code', size=16)
    length = fields.Float(string='Length', help='Indicates the longest length of the box in inches.')
    width = fields.Float(string='Width')
    height = fields.Float(string='Height')


class stock_packages(models.Model):
    _name = "stock.packages"
    _description = "Packages of Delivery Order"
    _rec_name = "packge_no"

    @api.one
    @api.depends('pick_id', 'pick_id.ship_state')
    def _button_visibility(self):
        val = True
        if self.pick_id.ship_state in ['read_pick','shipped','delivered', 'draft', 'cancelled']:
            val = False
        self.show_button = val

    @api.one
    @api.depends('stock_move_ids')
    def _get_decl_val(self):
        sum_amount = 0.0
        for line in self.stock_move_ids:
            sum_amount += line.cost or 0.0
        self.decl_val = sum_amount
    packge_no = fields.Char(string='Package Number', size=64, help='The number of the package associated with the delivery.\
                                Example: 3 packages may be associated with a delivery.')
    weight = fields.Float(string='Weight (lbs)', required=1, default=0.0, help='The weight of the individual package')
    package_type = fields.Many2one('shipping.package.type',
                                   string='Package Type',
                                   help='Indicates the type of package')
    length = fields.Float(string='Length', help='Indicates the longest length of the box in inches.')
    width = fields.Float(string='Width',
                         help='Indicates the width of the package in inches.')
    height = fields.Float(string='Height', help='Indicates the height of the package inches.')
    ref1 = fields.Selection([
                            ('AJ', 'Accounts Receivable Customer Account'),
                            ('AT', 'Appropriation Number'),
                            ('BM', 'Bill of Lading Number'),
                            ('9V', 'Collect on Delivery (COD) Number'),
                            ('ON', 'Dealer Order Number'),
                            ('DP', 'Department Number'),
                            ('3Q', 'Food and Drug Administration (FDA) Product Code'),
                            ('IK', 'Invoice Number'),
                            ('MK', 'Manifest Key Number'),
                            ('MJ', 'Model Number'),
                            ('PM', 'Part Number'),
                            ('PC', 'Production Code'),
                            ('PO', 'Purchase Order Number'),
                            ('RQ', 'Purchase Request Number'),
                            ('RZ', 'Return Authorization Number'),
                            ('SA', 'Salesperson Number'),
                            ('SE', 'Serial Number'),
                            ('ST', 'Store Number'),
                            ('TN', 'Transaction Reference Number'),
                            ('EI', 'Employee ID Number'),
                            ('TJ', 'Federal Taxpayer ID No.'),
                            ('SY', 'Social Security Number'),
                            ], string='Reference Number 1', help='Indicates the type of 1st reference no')
    ref2 = fields.Char(string='Reference Number 1', size=64,
                       help='A reference number 1 associated with the package.')
    ref2_code = fields.Selection([
                        ('AJ', 'Accounts Receivable Customer Account'),
                        ('AT', 'Appropriation Number'),
                        ('BM', 'Bill of Lading Number'),
                        ('9V', 'Collect on Delivery (COD) Number'),
                        ('ON', 'Dealer Order Number'),
                        ('DP', 'Department Number'),
                        ('3Q', 'Food and Drug Administration (FDA) Product Code'),
                        ('IK', 'Invoice Number'),
                        ('MK', 'Manifest Key Number'),
                        ('MJ', 'Model Number'),
                        ('PM', 'Part Number'),
                        ('PC', 'Production Code'),
                        ('PO', 'Purchase Order Number'),
                        ('RQ', 'Purchase Request Number'),
                        ('RZ', 'Return Authorization Number'),
                        ('SA', 'Salesperson Number'),
                        ('SE', 'Serial Number'),
                        ('ST', 'Store Number'),
                        ('TN', 'Transaction Reference Number'),
                        ('EI', 'Employee ID Number'),
                        ('TJ', 'Federal Taxpayer ID No.'),
                        ('SY', 'Social Security Number'),
                        ], string='Reference Number', help='Indicates the type of 2nd reference no')
    ref2_number = fields.Char(string='Reference Number 2', size=64, help='A reference number 2 associated with the package.')
    pick_id = fields.Many2one('stock.picking', string='Delivery Order')
    ship_move_id = fields.Many2one('shipping.move', string='Delivery Order')
    description = fields.Text(string='Description')
    logo = fields.Binary(string='Logo')
    negotiated_rates = fields.Float(string='NegotiatedRates')
    shipment_identific_no = fields.Char(string='ShipmentIdentificationNumber',
                                        size=64)
    tracking_no = fields.Char(string='TrackingNumber', size=64)
    ship_message = fields.Text(string='Status Message')
    tracking_url = fields.Char(string='Tracking URL', size=512)
    package_type_id = fields.Many2one('logistic.company.package.type',
                                      string='Package Type')
    show_button = fields.Boolean(compute='_button_visibility', store=True,
                                 string='Show')
    # package_item_ids = fields.One2many('shipment.package.item','package_id',
    # string='Package Items')
    stock_move_ids = fields.One2many('stock.move', 'package_id',
                                     string='Package Items')
    decl_val = fields.Float(compute='_get_decl_val', string='Declared Value',
                            store=True,
                            help='The declared value of the package.')

    @api.model
    def default_get(self, fields):
        context = self._context
        ret_val = super(stock_packages, self).default_get(fields)
        if ret_val.get('stock_move_ids', []):
            if ret_val['stock_move_ids'][0][0] == 6:
                new_list = []
                for el in ret_val['stock_move_ids'][0][2]:
                    new_list.append((4, el))
                ret_val['stock_move_ids'] = new_list
        return ret_val

    @api.multi
    def print_label(self):
        ids = self._ids
        if not ids: return []
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'shipping_api.report_label_print_stock_packages',
            'datas': {
                'model': 'stock.packages',
                'id': ids and ids[0] or False,
                'ids': ids,
                'report_type': 'pdf'
                },
            'nodestroy': True
        }

    @api.multi
    def print_packing_slips(self):
        ids = self._ids
        if not ids: return []
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'shipping_api.report_packing_slip_stock_packages',
            'datas': {
                'model': 'stock.packages',
                'id': ids and ids[0] or False,
                'ids': ids,
                'report_type': 'pdf'
                },
            'nodestroy': True
        }

    @api.multi
    def onchange_packge_no(self, packge_no, line_ids):
        """
        Function to generate sequence on packages
        """
        ret = {}
        if packge_no:
            ret['packge_no'] = packge_no
        else:
            if line_ids:
                for line in line_ids:
                        if line and line[2] and line[2]['packge_no'] and packge_no < line[2]['packge_no']:
                            packge_no = line[2]['packge_no']
                packge_no = str(int(packge_no)+1)
            ret['packge_no'] = packge_no
        return {'value': ret}

    @api.multi
    def onchange_weight(self, line_ids, tot_order_weight, weight):
        """
        Function to automatically fill package weight
        """
        if line_ids == False:
            line_ids = []
        ret = {}
        if weight:
            ret['weight'] = weight
        else:
            used_weight = 0
            for line in line_ids:
                if line and line[2] and line[2]['weight']:
                    used_weight += line[2]['weight']
            if used_weight < tot_order_weight:
                ret['weight'] = tot_order_weight - used_weight
        return {'value': ret}

    @api.multi
    def onchange_stock_package(self, package_type):
        res = {}
        res['value'] = {
                'length': 0,
                'width': 0,
                'height': 0,
        }
        if package_type:
            package_type_obj = self.env['shipping.package.type'].browse(package_type)
            res['value'] = {
                'length': package_type_obj.length,
                'width':package_type_obj.width,
                'height': package_type_obj.height,
        }
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
