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

class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _get_company_code(self):
        res = super(sale_order, self)._get_company_code()
        res.append(('usps', 'USPS'))
        return res
    
    @api.model
    def _get_service_type_usps(self):
        return [
            ('First Class', 'First Class'),
            ('First Class HFP Commercial', 'First Class HFP Commercial'),
            ('FirstClassMailInternational', 'First Class Mail International'),
            ('Priority', 'Priority'),
            ('Priority Commercial', 'Priority Commercial'),
            ('Priority HFP Commercial', 'Priority HFP Commercial'),
            ('PriorityMailInternational', 'Priority Mail International'),
            ('Express', 'Express'),
            ('Express Commercial', 'Express Commercial'),
            ('Express SH', 'Express SH'),
            ('Express SH Commercial', 'Express SH Commercial'),
            ('Express HFP', 'Express HFP'),
            ('Express HFP Commercial', 'Express HFP Commercial'),
            ('ExpressMailInternational', 'Express Mail International'),
            ('ParcelPost', 'Parcel Post'),
            ('ParcelSelect', 'Parcel Select'),
            ('StandardMail', 'Standard Mail'),
            ('CriticalMail', 'Critical Mail'),
            ('Media', 'Media'),
            ('Library', 'Library'),
            ('All', 'All'),
            ('Online', 'Online'),
        ]

    @api.model
    def _get_first_class_mail_type_usps(self):
        return [
            ('Letter', 'Letter'),
            ('Flat', 'Flat'),
            ('Parcel', 'Parcel'),
            ('Postcard', 'Postcard'),
        ]

    @api.model
    def _get_container_usps(self):
        return [
            ('Variable', 'Variable'),
            ('Card', 'Card'),
            ('Letter', 'Letter'),
            ('Flat', 'Flat'),
            ('Parcel', 'Parcel'),
            ('Large Parcel', 'Large Parcel'),
            ('Irregular Parcel', 'Irregular Parcel'),
            ('Oversized Parcel', 'Oversized Parcel'),
            ('Flat Rate Envelope', 'Flat Rate Envelope'),
            ('Padded Flat Rate Envelope', 'Padded Flat Rate Envelope'),
            ('Legal Flat Rate Envelope', 'Legal Flat Rate Envelope'),
            ('SM Flat Rate Envelope', 'SM Flat Rate Envelope'),
            ('Window Flat Rate Envelope', 'Window Flat Rate Envelope'),
            ('Gift Card Flat Rate Envelope', 'Gift Card Flat Rate Envelope'),
            ('Cardboard Flat Rate Envelope', 'Cardboard Flat Rate Envelope'),
            ('Flat Rate Box', 'Flat Rate Box'),
            ('SM Flat Rate Box', 'SM Flat Rate Box'),
            ('MD Flat Rate Box', 'MD Flat Rate Box'),
            ('LG Flat Rate Box', 'LG Flat Rate Box'),
            ('RegionalRateBoxA', 'RegionalRateBoxA'),
            ('RegionalRateBoxB', 'RegionalRateBoxB'),
            ('Rectangular', 'Rectangular'),
            ('Non-Rectangular', 'Non-Rectangular'),
         ]

    @api.model
    def _get_size_usps(self):
        return [
            ('REGULAR', 'Regular'),
            ('LARGE', 'Large'),
         ]
        
    @api.multi
    def action_ship_create(self):
        pick_obj = self.env['stock.picking']
        result = super(sale_order, self).action_ship_create()
        if result:
            for sale in self.browse(self._ids):
                if sale.ship_company_code == 'usps':
                    pick_ids = pick_obj.search([('sale_id', '=', sale.id)])
                    if pick_ids:
                        vals = {
                                'ship_company_code'     : 'usps',
                                'logis_company'         : sale.logis_company and sale.logis_company.id or False,
                                'usps_service_type'     : sale.usps_service_type,
                                'usps_package_location' : sale.usps_package_location,
                                'usps_first_class_mail_type' : sale.usps_first_class_mail_type,
                                'usps_container'    : sale.usps_container,
                                'usps_size'         : sale.usps_size,
                                'usps_length'       : sale.usps_length,
                                'usps_width'        : sale.usps_width,
                                'usps_height'       : sale.usps_height,
                                'usps_girth'        : sale.usps_girth,
                                'shipcharge'         : sale.shipcharge
                                }
                        pick_obj.write(vals)
        return result
    
    
    ship_company_code =             fields.Selection(_get_company_code, string='Ship Company')
    usps_service_type =             fields.Selection('_get_service_type_usps', string='Service Type', default='Priority')
    usps_package_location =         fields.Selection([
                                        ('Front Door', 'Front Door'),
                                        ('Back Door', 'Back Door'),
                                        ('Side Door', 'Side Door'),
                                        ('Knock on Door/Ring Bell', 'Knock on Door/Ring Bell'),
                                        ('Mail Room', 'Mail Room'),
                                        ('Office', 'Office'),
                                        ('Reception', 'Reception'),
                                        ('In/At Mailbox', 'In/At Mailbox'),
                                        ('Other', 'Other')], string='Package Location', default='Front Door')
    usps_first_class_mail_type =    fields.Selection('_get_first_class_mail_type_usps', string='First Class Mail Type', default='Parcel')
    usps_container =                fields.Selection('_get_container_usps', string='Container', default='Variable')
    usps_size =                     fields.Selection('_get_size_usps', string='Size', default='REGULAR')
    usps_length =                   fields.Float(string='Length')
    usps_width =                    fields.Float(string='Width')
    usps_height =                   fields.Float(string='Height')
    usps_girth =                    fields.Float(string='Girth')
    usps_packaging_type =           fields.Many2one('shipping.package.type', string='Packaging Type')
    
    