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

from openerp import models, fields, api, _
from openerp import netsvc


class shipping_rate_card(models.Model):
    _name = 'shipping.rate.card'
    _description = "Ground Shipping Calculation Table"
    name = fields.Char(string='Name', size=128, required=True)
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    rate_ids = fields.One2many('shipping.rate', 'card_id', string='Shipping Rates', required=True)


class shipping_rate_config(models.Model):
    _name = 'shipping.rate.config'
    _description = "Configuration for shipping rate"
    _rec_name = 'shipmethodname'
    real_id = fields.Integer(string='ID', readonly=True)
    shipmethodname = fields.Char(string='Name', size=128, help='Shipping method name. Displayed in the wizard.')
    active = fields.Boolean(string='Active', help='Indicates whether a shipping method is active')
    use = fields.Boolean(string='Select')
    calc_method = fields.Selection([('country_weight', 'Country & Weight'),
                                    ('state_zone_weight', 'State-Zone-Weight'),
                                    ('manual', 'Manually Calculate')],
                                   string='Shipping Calculation Method',
                                   default='country_weight',
                                   help='Shipping method name. Displayed in the wizard.')
    shipping_wizard = fields.Integer(string='Shipping Wizard')
    zone_map_ids = fields.One2many('zone.map', 'rate_config_id', string='Zone Map')
    account_id = fields.Many2one('account.account', string='Account', help='This account represents the g/l account for booking shipping income.')
    shipment_tax_ids = fields.Many2many('account.tax', 'shipment_tax_rel', 'shipment_id', 'tax_id', string='Taxes', domain=[('parent_id', '=', False)])
    rate_card_id = fields.Many2one('shipping.rate.card', string='Shipping Rate Card')


class zone_map(models.Model):
    _name = 'zone.map'
    _description = "Zone Mapping Table"
    _rec_name = 'zone'
    zone = fields.Integer(string='Zone')
    state_id = fields.Many2one('res.country.state', string='State / Zone')
    rate_config_id = fields.Many2one('shipping.rate.config', string='Shipping Rate Configuration')


class shipping_rate(models.Model):
    _name = 'shipping.rate'
    _description = "Shipping Calculation Table"
    name = fields.Char(string='Name', size=128)
    from_weight = fields.Integer(string='From Weight', required=True)
    to_weight = fields.Integer(string='To Weight')
    charge = fields.Float(string='Shipping Charge')
    over_cost = fields.Float(string='Shipping Charge per pound over')
    country_id = fields.Many2one('res.country', string='Country')
    zone = fields.Integer(string='Zone', required=True)
    card_id = fields.Many2one('shipping.rate.card', string='Shipping Table')

    def find_cost(self, config_id, address, model_obj):
        """
        Function to calculate shipping cost
        """
        cost = 0
        table_env = self.env['shipping.rate']
        config_env = self.env['shipping.rate.config']
        # logger = netsvc.Logger()
        config_obj = config_env.browse(config_id)
        rate_card_id = config_obj.rate_card_id.id

        if config_obj.calc_method == 'country_weight':
            country_id = address.country_id.id
            weight_net = model_obj.total_weight_net
            table_ids = table_env.search([('card_id', '=', rate_card_id), ('country_id', '=', country_id),
                                          ('from_weight', '<=', weight_net), ('to_weight', '>', weight_net)])
            if table_ids:
                table_obj = table_env.browse(table_ids)[0]
                if table_obj.charge == 0.0 and table_obj.over_cost:
                    cost = model_obj.total_weight_net * table_obj.over_cost
                else:
                    cost = table_obj.charge
            else:
                search_list = [('card_id', '=', rate_card_id), ('country_id', '=', country_id), ('over_cost', '>', 0)]
                table_ids = table_env.search(search_list)
                if table_ids:
                    table_objs = table_env.browse(table_ids)
                    table_obj = table_objs[0]
                    for table in table_objs:
                        if table_obj.from_weight < table.from_weight:
                            table_obj = table
                    weight = model_obj.total_weight_net
                    if table_obj.charge > 0:
                        cost = table_obj.charge
                        weight -= table_obj.from_weight
                        if weight > 0:
                            cost += weight * table_obj.over_cost
                    else:
                        cost = weight * table_obj.over_cost
#                else:
#                    logger.notifyChannel(_("Calculate Shipping"), netsvc.LOG_WARNING, _("Unable to find rate table with Shipping Table = %s and \
#                                            Country = %s and Over Cost > 0."%(config_obj.rate_card_id.name, address.country_id.name)))

        elif config_obj.calc_method == 'state_zone_weight':
            zone_env = self.env['zone.map']
            state_id = address.state_id.id
            zone_ids = zone_env.search([('rate_config_id', '=', config_obj.id), ('state_id', '=', state_id)])
            if zone_ids:
                zone = zone_env.read(['zone'])[0]
                table_ids = table_env.search([('card_id', '=', rate_card_id), ('zone', '=', zone)])
                if table_ids:
                    table_obj = table_env.browse(table_ids)[0]
                    weight = model_obj.total_weight_net
                    if table_obj.charge > 0:
                        cost = table_obj.charge
                        weight -= table_obj.to_weight
                        if weight > 0:
                            cost += weight * table_obj.over_cost
                    else:
                        cost = weight * table_obj.over_cost
#                else:
#                    logger.notifyChannel(_("Calculate Shipping"), netsvc.LOG_WARNING, _("Unable to find rate table with Shipping Table = %s and \
#                                            Zone = %s."%(config_obj.shipmethodname, zone)))
#            else:
#                logger.notifyChannel(_("Calculate Shipping"), netsvc.LOG_WARNING, _("Unable to find Zone Mapping Table with Shipping Rate \
#                                        Configuration = %s and State = %s."%(config_obj.shipmethodname, address.state_id.name)))
        elif config_obj.calc_method == 'manual':
            cost = 0.0
        return cost


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
