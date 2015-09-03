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
from openerp import models, fields, api, _
import math
from base64 import b64decode
import urllib
import xml2dic
from xml.dom.minidom import parse, parseString

class shipping_rate_wizard(models.TransientModel):
    _inherit = 'shipping.rate.wizard'

    @api.model
    def _get_company_code(self):
        res =  super(shipping_rate_wizard, self)._get_company_code()
        res.append(('usps', 'USPS'))
        return res

    @api.model
    def default_get(self, fields):
        res = super(shipping_rate_wizard, self).default_get(fields)
        context=self._context
        if context.get('active_model',False) == 'sale.order':
            sale_id = context.get('active_id',False)
            if sale_id:
                sale = self.env['sale.order'].browse(sale_id)
                if 'usps_service_type' in fields and  sale.usps_service_type:
                    res['usps_service_type'] = sale.usps_service_type
                
                if 'usps_first_class_mail_type' in fields and  sale.usps_first_class_mail_type:
                    res['usps_first_class_mail_type'] = sale.usps_first_class_mail_type
                    
                if 'usps_container' in fields and  sale.usps_container:
                    res['usps_container'] = sale.usps_container
                    
                if 'usps_package_location' in fields and  sale.usps_package_location:
                    res['usps_package_location'] = sale.usps_package_location
                    
                if 'usps_size' in fields and  sale.usps_size:
                    res['usps_size'] = sale.usps_size
                    
                if 'usps_length' in fields and  sale.usps_length:
                    res['usps_length'] = sale.usps_length
                    
                if 'usps_width' in fields and  sale.usps_width:
                    res['usps_width'] = sale.usps_width
                    
                if 'usps_height' in fields and  sale.usps_height:
                    res['usps_height'] = sale.usps_height
                    
                if 'usps_girth' in fields and  sale.usps_girth:
                    res['usps_girth'] = sale.usps_girth
        return res

    @api.multi
    def update_sale_order(self):
        ids=self._ids
        context=self._context
        data = self.browse(ids)[0]
        if not (data['rate_selection'] == 'rate_request' and data['ship_company_code']=='usps'):
            return super(shipping_rate_wizard, self).update_sale_order()
        if context.get('active_model',False) == 'sale.order':
            sale_id = context.get('active_id',False)
            sale_id and self.env['sale.order'].write({'shipcharge':data.shipping_cost,
                                                                'ship_method':data.usps_service_type,
                                                                'sale_account_id':data.logis_company and data.logis_company.ship_account_id and data.logis_company.ship_account_id.id or False,
                                                                'ship_company_code' :data.ship_company_code,
                                                                'logis_company' : data.logis_company and data.logis_company.id or False,
                                                                'usps_service_type' : data.usps_service_type,
                                                                'usps_package_location' : data.usps_package_location,
                                                                'usps_first_class_mail_type' : data.usps_first_class_mail_type ,
                                                                'usps_container' : data.usps_container ,
                                                                'usps_size' : data.usps_size ,
                                                                'usps_length' : data.usps_length ,
                                                                'usps_width' : data.usps_width ,
                                                                'usps_height' : data.usps_height ,
                                                                'usps_girth' : data.usps_girth ,
                                                                'rate_selection' : data.rate_selection
                                                                })
            self.env['sale.order'].button_dummy([sale_id])
            return {'nodestroy':False,'type': 'ir.actions.act_window_close'}
        return True

    @api.multi
    def get_rate(self):
        ids=self._ids
        context=self._context
        data = self.browse(self._ids)
        if not ( data['rate_selection'] == 'rate_request' and data['ship_company_code']=='usps'):
            return super(shipping_rate_wizard, self).get_rate()

        if context.get('active_model',False) == 'sale.order':
            sale_id = context.get('active_id',False)
            sale = self.env['sale.order'].browse(sale_id)
            test = data.logis_company.test_mode or False
            url = ''
            url_sec = ''
            if data.logis_company:
                url = test and data.logis_company.usps_url_test or  data.logis_company.usps_url
                url_sec = test and data.logis_company.usps_url_secure_test or data.logis_company.usps_url_secure
                url_prd = data.logis_company.usps_url

            address_from = sale.company_id.partner_id and sale.company_id.partner_id
            zip_origin = ''
            if address_from:
                zip_origin = address_from.zip or ''
            zip_destination=sale.partner_shipping_id.zip or ''
            weight = math.modf(sale.total_weight_net)
            pounds = int(weight[1])
            ounces = round(weight[0],2) * 16
            request_xml = """<RateV4Request USERID="%(user_id)s">
                                <Revision/>
                                    <Package ID="1ST">
                                        <Service>%(service_type)s</Service>
                                        <FirstClassMailType>%(first_class_mail_type)s</FirstClassMailType>
                                        <ZipOrigination>%(zip_origin)s</ZipOrigination>
                                        <ZipDestination>%(zip_desitination)s</ZipDestination>
                                        <Pounds>%(pounds)s</Pounds>
                                        <Ounces>%(ounces)s</Ounces>
                                        <Container>%(container)s</Container>
                                        <Size>REGULAR</Size>
                                        <Machinable>true</Machinable>
                                    </Package>
                            </RateV4Request>"""%{
                        'user_id' : data.logis_company and data.logis_company.usps_userid,
                        'service_type' : data.usps_service_type ,
                        'first_class_mail_type' : data.usps_first_class_mail_type,
                        'zip_origin' :  zip_origin,
                        'zip_desitination' : zip_destination, 
                        'pounds' : str(pounds),
                        'ounces' : str(ounces),
                        'container' : str(data.usps_container) ,
                     }
            if url_prd and request_xml:
                request_url = url_prd + '?API=RateV4&XML=' + request_xml
            # not supported with test accounts
            str_response = ''
            error = False
            try :
                f = urllib.urlopen(request_url)
                str_response = f.read()
            except Exception, e:
                self.write({'status_message': str(e)})
            if str_response:
                xml_dic = xml2dic.main(str_response)
                if 'Error' in xml_dic.keys():
                    error = True
                    for item in xml_dic.get('Error'):
                        if 'Description' in item:
                            self.write({'status_message': 'Error : ' + item['Description'] })
                else:
                    for pack in xml_dic['RateV4Response']:
                        if 'Package' in pack:
                            for item in pack['Package']:
                                if 'Error' in item:
                                    error = True
                                    for i in item['Error']:
                                        if 'Description' in i:
                                            self.write({'status_message': 'Error : ' + i['Description'] })
                                            break
                                if error:
                                    break
                        if error:
                            break
                if not error:
                    for pack in xml_dic['RateV4Response']:
                        if 'Package' in pack:
                            for item in pack['Package']:
                                if 'Postage' in item:
                                    for i in item['Postage']:
                                        if 'Rate' in i:
                                            self.write([data.id], {'status_message': '', 'shipping_cost': i['Rate'] })
                                            sale.write({'shipcharge': float(i['Rate']) or 0.00, 'ship_method':data.ship_company_code + ':' + data.usps_service_type, 'status_message': ''})
                                            return True
        mod, modid = self.env['ir.model.data'].get_object_reference('shipping_api_usps', 'view_for_shipping_rate_wizard_usps')
        return {
            'name':_("Get Rate"),
            'view_mode': 'form',
            'view_id': modid,
            'view_type': 'form',
            'res_model': 'shipping.rate.wizard',
            'type': 'ir.actions.act_window',
            'target':'new',
            'nodestroy': True,
            'domain': '[]',
            'res_id': ids[0],
            'context':context,
        }
    
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
        
        
    ship_company_code =             fields.Selection(_get_company_code, string='Ship Company')
    usps_service_type =             fields.Selection('_get_service_type_usps', string='Service Type')
    usps_package_location =         fields.Selection([
                                                    ('Front Door','Front Door'),
                                                    ('Back Door','Back Door'),
                                                    ('Side Door','Side Door'),
                                                    ('Knock on Door/Ring Bell','Knock on Door/Ring Bell'),
                                                    ('Mail Room','Mail Room'),
                                                    ('Office','Office'),
                                                    ('Reception','Reception'),
                                                    ('In/At Mailbox','In/At Mailbox'),
                                                    ('Other','Other'),
                                               ],string='Package Location')
    usps_first_class_mail_type =    fields.Selection('_get_first_class_mail_type_usps', string='First Class Mail Type')
    usps_container =                fields.Selection('_get_container_usps', string='Container')
    usps_size =                     fields.Selection('_get_size_usps', string='Size')
    usps_length =                   fields.Float(string='Length')
    usps_width =                    fields.Float(string='Width')
    usps_height =                   fields.Float(string='Height')
    usps_girth =                    fields.Float(string='Girth')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: