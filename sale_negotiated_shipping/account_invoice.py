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

import time
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def addr_validate_act_window(self):
        if str(self.address_validation_method) == 'fedex.account':
            ir_model_data = self.env['ir.model.data']
            form_id = ir_model_data.get_object_reference('partner_address_validation', 'view_so_addrvalidate')[1]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'so.addr_validate',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
            }
        else:
            raise Warning(_('Please select a address validation method for your Fedex account'))

    @api.model
    def _method_get(self):
        list = []
        ups_acc_obj = self.env['ups.account']
        fedex_acc_obj = self.env['fedex.account']
        usps_acc_obj = self.env['usps.account']
        ups_ids = ups_acc_obj.search([])
        fedex_ids = fedex_acc_obj.search([])
        usps_ids = usps_acc_obj.search([])

        if ups_ids:
            list.append(('ups.account', 'UPS'))

        if fedex_ids:
            list.append(('fedex.account', 'FedEx'))

        if usps_ids:
            list.append(('usps.account', 'USPS'))
        return list

    @api.multi
    def _get_address_validation_method(self):
        ids = self._ids
        context = self._context
        if context is None:
            context = {}
        user = self.env['res.users'].browse(ids)
        return user and user.company_id and user.company_id.address_validation_method

    @api.one
    @api.depends('invoice_line')
    def _total_weight_net(self):
        """Compute the total net weight of the given Invoice."""
        result = 0.0
        for line in self.invoice_line:
            if line.product_id:
                result += line.weight_net or 0.0
        self.total_weight_net = result

    @api.multi
    def _amount_shipment_tax(self, shipment_taxes, shipment_charge):
        val = 0.0
        for c in self.env['account.tax'].compute_all(shipment_taxes, shipment_charge, 1)['taxes']:
            val += c.get('amount', 0.0)
        return val

    @api.multi
    def _amount_all(self, field_name, arg):
        res = super(account_invoice, self)._amount_all(field_name, arg)
        for invoice in self.browse(self._ids):
            if invoice.shipcharge:
                res[invoice.id]['amount_total'] = res[invoice.id]['amount_untaxed'] + res[invoice.id]['amount_tax'] + invoice.shipcharge
        return res

    @api.model
    def _get_invoice_from_line(self):
        invoice = self.env['account.invoice']
        return super(account_invoice, invoice)._get_invoice_from_line()

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """
        finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        Args:
            invoice: browsable record of the invoice that is generating the move lines
            move_lines: list of dictionaries with the account.move.lines (as for create())
        Returns:
            The (possibly updated) final move_lines to create for this invoice
        """
        move_lines = super(account_invoice, self).finalize_invoice_move_lines(move_lines)

        for rec in self:
            if rec.type == "out_refund":
                account = rec.account_id.id
            else:
                account = rec.sale_account_id.id
            if rec.type in ('out_invoice', 'out_refund') and account and rec.shipcharge:
                lines1 = {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'analytic_lines': [],
                    'tax_amount': False,
                    'name': 'Shipping Charge',
                    'ref': '',
                    'currency_id': False,
                    'credit': rec.shipcharge,
                    'product_id': False,
                    'date_maturity': False,
                    'debit': False,
                    'date': time.strftime("%Y-%m-%d"),
                    'amount_currency': 0,
                    'product_uom_id':  False,
                    'quantity': 1,
                    'partner_id': rec.partner_id.id,
                    'account_id': account
                }
                move_lines.append((0, 0, lines1))
                has_entry = False
                for move_line in move_lines:
                    journal_entry = move_line[2]
                    if journal_entry['account_id'] == rec.partner_id.property_account_receivable.id:
                        journal_entry['debit'] += rec.shipcharge
                        has_entry = True
                        break
                if not has_entry:       # If debit line does not exist create one
                    lines2 = {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'analytic_lines': [],
                        'tax_amount': False,
                        'name': '/',
                        'ref': '',
                        'currency_id': False,
                        'credit': False,
                        'product_id': False,
                        'date_maturity': False,
                        'debit': rec.shipcharge,
                        'date': time.strftime("%Y-%m-%d"),
                        'amount_currency': 0,
                        'product_uom_id': False,
                        'quantity': 1,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.partner_id.property_account_receivable.id
                    }
                    move_lines.append((0, 0, lines2))
        return move_lines
    total_weight_net = fields.Float(compute=_total_weight_net, string='Total Net Weight', store=True,
                                     help="The cumulated net weight of all the invoice lines.")
    logis_company = fields.Many2one('logistic.company', string='Logistic Company',
    # default=_get_logis_company, 
                                        help='Name of the Logistics company providing the shipper services.')
    address_validation_method = fields.Selection(_method_get, string='Address Validation Method',
                                                 default=_get_address_validation_method)
    shipcharge = fields.Float(string='Shipping Cost', readonly=True)
    ship_method = fields.Char(string='Ship Method', size=128, readonly=True)
    ship_method_id = fields.Many2one('shipping.rate.config', string='Shipping Method', readonly=True)
    sale_account_id = fields.Many2one('account.account', string='Shipping Account', readonly=True,
                                          help='This account represents the g/l account for booking shipping income.')


class invoice_line(models.Model):
    """Add the net weight to the object "Invoice Line"."""
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('product_id')
    def _weight_net(self):
        """Compute the net weight of the given Invoice Lines."""
        result = 0.0
        for line in self.product_id:
            result += line.weight_net * line.qty_available
        self.weight_net = result
    weight_net = fields.Float(compute='_weight_net', string='Net Weight', help="The net weight in Kg.", store=True)


class account_invoice_tax_inherit(models.Model):
    _inherit = "account.invoice.tax"

    @api.multi
    def compute(self, invoice_id):
        context = self._context
        tax_grouped = super(account_invoice_tax_inherit, self).compute(invoice_id)
        tax_obj = self.env['account.tax']
        cur_obj = self.env['res.currency']
        inv = invoice_id
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id
        tax_ids = inv.ship_method_id and inv.ship_method_id.shipment_tax_ids
        if tax_ids:
            for tax in tax_obj.compute_all(tax_ids, inv.shipcharge, 1)['taxes']:
                val = {}
                val.update({
                    'invoice_id': inv.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': tax['price_unit'] * 1
                    })
                if inv.type in ('out_invoice', 'in_invoice'):
                    val.update({
                        'base_code_id': tax['base_code_id'],
                        'tax_code_id': tax['tax_code_id'],
                        'base_amount': cur_obj.compute(inv.currency_id.id, company_currency, val['base'] * tax['base_sign'],
                                                       context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                        'tax_amount': cur_obj.compute(inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'],
                                                      context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                        'account_id': tax['account_collected_id'] or line.account_id.id
                        })
                else:
                    val.update({
                        'base_code_id': tax['ref_base_code_id'],
                        'tax_code_id': tax['ref_tax_code_id'],
                        'base_amount': cur_obj.compute(inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'],
                                                       context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                        'tax_amount': cur_obj.compute(inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'],
                                                      context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                        'account_id': tax['account_paid_id'] or line.account_id.id
                        })
                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])

                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

            for t in tax_grouped.values():
                t['base'] = cur_obj.round(cur, t['base'])
                t['amount'] = cur_obj.round(cur, t['amount'])
                t['base_amount'] = cur_obj.round(cur, t['base_amount'])
                t['tax_amount'] = cur_obj.round(cur, t['tax_amount'])
        return tax_grouped

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
