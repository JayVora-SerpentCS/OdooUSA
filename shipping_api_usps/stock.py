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
from openerp.exceptions import except_orm, Warning, RedirectWarning
# from xml.dom.minidom import Document
# import httplib
import xml2dic
# import time
# import datetime
# from urlparse import urlparse
import Image
import tempfile
import re

# import netsvc
import base64
import logging
# import tools

# from base64 import b64decode
# import binascii

class logistic_company(models.Model):
    
    _inherit = "logistic.company"
    
    @api.model
    def _get_company_code(self):
        res = super(logistic_company, self)._get_company_code()
        res.append(('usps', 'USPS'))
        return res
    
    ship_company_code =     fields.Selection('_get_company_code', string='Ship Company', required=True)
    usps_userid =           fields.Char(string='User ID', size=128)
    usps_url_test =         fields.Char(string='Test Url', size=512)
    usps_url =              fields.Char(string='Production URL', size=512)
    usps_url_secure_test =  fields.Char(string='Test Url SSL', size=512)
    usps_url_secure =       fields.Char(string='Production URL SSL', size=512)
    


class stock_packages(models.Model):
    _inherit = "stock.packages"
    
    usps_confirmation_number = fields.Char(string='USPS Confirm Number', size=64, readonly=True)
     

class stock_picking(models.Model):

    _inherit = "stock.picking"
    
    @api.model
    def _get_company_code(self):
        res = super(stock_picking, self)._get_company_code()
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
        
    ship_company_code =         fields.Selection('_get_company_code', string='Ship Company', size=64)
    usps_confirmation_number =  fields.Char(string='Confirmation Number', size=64, readonly=True)
    usps_service_type =         fields.Selection('_get_service_type_usps', string='Service Type', size=100, default='Priority')
    usps_package_location =     fields.Selection([
                                    ('Front Door', 'Front Door'), 
                                    ('Back Door', 'Back Door'),
                                    ('Side Door', 'Side Door'),
                                    ('Knock on Door/Ring Bell', 'Knock on Door/Ring Bell'),
                                    ('Mail Room', 'Mail Room'),
                                    ('Office', 'Office'),
                                    ('Reception', 'Reception'),
                                    ('In/At Mailbox', 'In/At Mailbox'),
                                    ('Other', 'Other')], string='Package Location', default='Front Door')
    usps_first_class_mail_type =fields.Selection('_get_first_class_mail_type_usps', string='First Class Mail Type', default='Parcel', size=50)
    usps_container =            fields.Selection('_get_container_usps', string='Container', size=100, default='Variable')
    usps_size =                 fields.Selection('_get_size_usps', string='Size', default='REGULAR')
    usps_length =               fields.Float(string='Length')
    usps_width =                fields.Float(string='Width')
    usps_height =               fields.Float(string='Height')
    usps_girth =                fields.Float(string='Girth')
    
    @api.multi
    def process_ship(self):
        ids=self._ids
        do = self.browse(type(ids) == type([]) and ids[0] or ids)
        user = self.env['res.users'].browse(self._ids)
        if do.ship_company_code != 'usps':
            return super(stock_picking, self).process_ship()

        if not (do.logis_company and do.logis_company.ship_company_code == 'usps'):
            return super(stock_picking, self).process_ship()
        userid = do.logis_company.usps_userid
        url = do.logis_company.test_mode and do.logis_company.usps_url_secure_test or do.logis_company.usps_url_secure
        url_prd = do.logis_company.usps_url
        url_prd_secure = do.logis_company.usps_url_secure
        test = do.logis_company.test_mode
        str_error = ''
        ship_message = ''
        error = False
        for package in do.packages_ids:
                    str_error = ''
        # if do.packages_ids:
                    # @Changing to production URL SINCE DelivConfirmCertifyV3.0Request works only with production url and test data
                    url = do.logis_company.usps_url_secure
                    if test:
                        request_xml = """<DelivConfirmCertifyV3.0Request USERID="%(user_id)s">
                                <Option>1</Option>
                                <ImageParameters></ImageParameters>
                                <FromName>Joe Smith</FromName>
                                <FromFirm>ABD Corp.</FromFirm>
                                <FromAddress1>Apt. 3C</FromAddress1>
                                <FromAddress2>6406 Ivy Lane</FromAddress2>
                                <FromCity>Greenbelt</FromCity>
                                <FromState>MD</FromState>
                                <FromZip5>20770</FromZip5>
                                <FromZip4>1234</FromZip4>
                                <ToName>Tom Collins</ToName>
                                <ToFirm>XYZ Corp.</ToFirm>
                                <ToAddress1>Suite 4D</ToAddress1>
                                <ToAddress2>8 Wildwood Drive</ToAddress2>
                                <ToCity>Old Lyme</ToCity>
                                <ToState>CT</ToState>
                                <ToZip5>06371</ToZip5>
                                <ToZip4></ToZip4>
                                <WeightInOunces>1</WeightInOunces>
                                <ServiceType>Priority</ServiceType>
                                <SeparateReceiptPage></SeparateReceiptPage>
                                <POZipCode></POZipCode>
                                <ImageType>TIF</ImageType>
                                <LabelDate></LabelDate>
                                <CustomerRefNo></CustomerRefNo>
                                <AddressServiceRequested></AddressServiceRequested>
                                <SenderName></SenderName>
                                <SenderEMail></SenderEMail>
                                <RecipientName></RecipientName>
                                <RecipientEMail></RecipientEMail>
                                </DelivConfirmCertifyV3.0Request>
                    """ % {   
                            'user_id'      : userid,
                        }
                    if url and request_xml:
                        request_url = url + '?API=DelivConfirmCertifyV3&XML=' + request_xml
                    elif  do.company_id.partner_id.address:
                        from_address = do.company_id.partner_id.address[0]
                        request_xml = """<DeliveryConfirmationV3.0Request USERID="%(user_id)s">
                                            <Option>1</Option>
                                            <ImageParameters />
                                            <FromName>%(from_name)s</FromName>
                                            <FromFirm>%(from_firm)s</FromFirm>
                                            <FromAddress1 />
                                            <FromAddress2>%(from_address2)s</FromAddress2>
                                            <FromCity>%(from_city)s</FromCity>
                                            <FromState>%(from_state)s</FromState>
                                            <FromZip5>%(from_zip5)s</FromZip5>
                                            <FromZip4>%(from_zip4)s</FromZip4>
                                            <ToName>%(to_name)s</ToName>
                                            <ToFirm>%(to_firm)s</ToFirm>
                                            <ToAddress1>%(to_address1)s</ToAddress1>
                                            <ToAddress2>%(to_address2)s</ToAddress2>
                                            <ToCity>%(to_city)s</ToCity>
                                            <ToState>%(to_state)s</ToState>
                                            <ToZip5>%(to_zip5)s</ToZip5>
                                            <ToZip4>%(to_zip4)s</ToZip4>
                                            <WeightInOunces>%(weight)s</WeightInOunces>
                                            <ServiceType>%(service_type)s</ServiceType>
                                            <POZipCode></POZipCode>
                                            <ImageType>TIF</ImageType>
                                            <LabelDate></LabelDate>
                                            <CustomerRefNo></CustomerRefNo>
                                            <AddressServiceRequested>TRUE</AddressServiceRequested>
                                            </DeliveryConfirmationV3.0Request>
                        """ % {   
                            'user_id'       : userid,
                            'from_name'     : from_address.name,
                            'from_firm'     : '',
                            'from_address2' : from_address.street or '',
                            'from_city'     : from_address.city or '',
                            'from_state'    : from_address.state_id and from_address.state_id.code or '',
                            'from_zip5'     : from_address.zip or '',
                            'from_zip4'     : from_address.zip or '',
                            'to_name'       : do.address_id.name ,
                            'to_firm'       : '',
                            'to_address1'   : do.address_id.street,
                            'to_address2'   : do.address_id.street2,
                            'to_city'       : do.address_id.city,
                            'to_state'      : do.address_id.state_id and do.address_id.state_id.code or '',
                            'to_zip5'       : do.address_id.zip or '',
                            'to_zip4'       : do.address_id.zip,
                            'weight'        : package.weight,
                            'service_type'  : do.usps_service_type,
                        }
                        if url and request_xml:
                            request_url = url + '?API=DeliveryConfirmationV3&XML=' + request_xml
                    try :
                        import urllib
                        f = urllib.urlopen(request_url)
                        from xml.dom.minidom import parse, parseString
                        import xml2dic
                        
                        str_response = f.read()
                        xml_response = parseString(str_response)
                        xml_dic = xml2dic.main(str_response)
                        
                        if  'Error' in xml_dic.keys():
                            error = True
                            for item in xml_dic.get('Error'):
                                
                                if item.get('Number'):
                                    if str_error:
                                        str_error = str_error + "\n----------------------"
                                    str_error = str_error + "\nNumber : " + item['Number']
                                if item.get('Description'):
                                    str_error = str_error + "\nDescription : " + item['Description']

                        else:
                            confirmation_number = xml_dic['DelivConfirmCertifyV3.0Response'][0]['DeliveryConfirmationNumber']
                            label_data = xml_dic['DelivConfirmCertifyV3.0Response'][1]['DeliveryConfirmationLabel']
                            # logo = binascii.b2a_base64(str(b64decode(label_data)))
                            # logo = str(b64decode(label_data))
                            
                            logo = base64.decodestring(label_data)

                            import os
                            import tempfile
                            dir_temp = tempfile.gettempdir()
                            
                            f = open(dir_temp + '/usps.tif', 'w+')
                            f.write(logo)
                            f.close()
                            label_image = ''

                            cp = False
                            if os.name == 'posix' or 'nt':
                                try:
                                    os.system("tiffcp -c none " + dir_temp + "/usps.tif " + dir_temp + "/usps_temp.tif")
                                    cp = True
                                except Exception, e:
                                    str_error = "Please install tiffcp."
                            if cp:
                                im = Image.open(dir_temp + '/usps_temp.tif')
                                im.thumbnail(im.size)
                                im.save(dir_temp + '/usps_temp.jpg', "JPEG", quality=100)
                                label_from_file = open(dir_temp + '/usps_temp.jpg', 'rb')
                                label_image = base64.encodestring(label_from_file.read())

                                self.env['stock.packages'].write({'logo': label_image, 'tracking_no': confirmation_number, 'usps_confirmation_number': confirmation_number, 'ship_message': 'Shipment has processed'})
                                
                    except Exception, e:
                        str_error = str(e)
            
                    self._cr.commit()
                    if str_error:
                        self.env['stock.packages'].write({'ship_message': str_error})
                                
        
                
        if not error:
            self.write({'ship_state':'ready_pick', 'ship_message': 'Shipment has been processed.'})
            return {
                'type': 'ir.actions.report.xml',
                'report_name':'multiple.label.print',
                'datas': {
                        'model':'stock.picking',
                        'id': ids and ids[0] or False,
                        'ids': ids and ids or [],
                        'report_type': 'pdf'
                    },
                'nodestroy': True
                }
        else:
            self.write({'ship_message': 'Error occured on processing some of packages, for details please see the status packages.'})
            # @todo: raise appropriate error msg
            raise except_orm(_('Error'), _('%s' % ('No package lines are created for shippment process.')))
                
        return True
    
    @api.multi
    def process_void(self):
        ids=self._ids
        if type(ids) == list:
            ids = list(ids)
        do = self.browse(ids)[0]
        if do.ship_company_code != 'usps':
            return super(stock_picking, self).process_void()

        if not (do.logis_company and do.logis_company.ship_company_code == 'usps'):
            return super(stock_picking, self).process_void()
        
        userid = do.logis_company.usps_userid
        url = do.logis_company.test_mode and do.logis_company.usps_url_secure_test or do.logis_company.usps_url_secure
        url_prd = do.logis_company.usps_url
        url_prd_secure = do.logis_company.usps_url_secure
        test = do.logis_company.test_mode

        error = False
        str_error = '' 
        
        for pack in do.packages_ids:
            if pack.tracking_no:
                url = test and do.logis_company.usps_url_secure_test or do.logis_company.usps_url_secure
                url_sec = test and do.logis_company.usps_url_secure_test or do.logis_company.usps_url_secure
                if test:
                    request_xml = """<CarrierPickupCancelRequest USERID="%(user_id)s">
                        <FirmName>ABC Corp.</FirmName>
                        <SuiteOrApt>Suite 777</SuiteOrApt>
                        <Address2>1390 Market Street</Address2>
                        <Urbanization></Urbanization>
                        <City>Houston</City>
                        <State>TX</State>
                        <ZIP5>77058</ZIP5>
                        <ZIP4>1234</ZIP4>
                        <ConfirmationNumber>WTC123456789</ConfirmationNumber>
                        </CarrierPickupCancelRequest>
                        """ % {'user_id': do.logis_company.usps_userid}
                else:
                    request_xml = """<CarrierPickupCancelRequest USERID="%(user_id)">
                        <FirmName>ABC Corp.</FirmName>
                        <SuiteOrApt>Suite 777</SuiteOrApt>
                        <Address2>1390 Market Street</Address2>
                        <Urbanization></Urbanization>
                        <City>Houston</City>
                        <State>TX</State>
                        <ZIP5>77058</ZIP5>
                        <ZIP4>1234</ZIP4>
                        <ConfirmationNumber>%(confirmation_number)</ConfirmationNumber>
                        </CarrierPickupCancelRequest>
                        """ % {
                                'user_id': do.logis_company.usps_userid,
                                'confirmation_number' : pack.tracking_no,
                             }
                if url and request_xml:
                    request_url = url + '?API=CarrierPickupCancel&XML=' + request_xml
                try :
                    import urllib
                    f = urllib.urlopen(request_url)
                    from xml.dom.minidom import parse, parseString
                    import xml2dic
                
                    str_response = f.read()
                except Exception:
                    self.env['stock.packages'].write({'ship_message': str(Exception)})
                    
                    
                xml_response = parseString(str_response)
                xml_dic = xml2dic.main(str_response)
                
                if  'Error' in xml_dic.keys():
                    error = True
                    for item in xml_dic.get('Error'):
                        self.env['stock.packages'].write({'ship_message': str_error})
                        break
                else:
                    self.env['stock.packages'].write({      
                                                           'negotiated_rates' : 0.00,
                                                           'shipment_identific_no' :'',
                                                           'tracking_no': '',
                                                           'tracking_url': '',
                                                           'logo' : '',
                                                           'ship_message' : 'Shipment Cancelled'})

        if not error:
            self.write({'ship_state'    :'draft', 'ship_message' : 'Shipment has been cancelled.'})
        else :
            self.write({ 'ship_message'  : 'Cancellation of some of shipment has failed, please check the status of pakages.'})
        return True
    


class stock_move(models.Model):
    
    _inherit = "stock.move"
    
    @api.model
    def create(self, vals):
        context=self._context
        if not context: context = {}
        package_obj = self.env['stock.packages']
        pack_id = None
        package_ids = package_obj.search([('pick_id', "=", vals.get('picking_id'))])
        if vals.get('picking_id'):
            rec = self.env['stock.picking'].browse(vals.get('picking_id'))
            if not context.get('copy'):
                if not package_ids:
                    pack_id = package_obj.create({'package_type': rec.sale_id.usps_packaging_type.id, 'pick_id': vals.get('picking_id')})
        res = super(stock_move, self).create(vals)
        if not context.get('copy'):
            context.update({'copy': 1})
            default_vals = {}
            if pack_id:
                default_vals = {'package_id':pack_id, 'picking_id':[]}
            elif package_ids:
                default_vals = {'package_id':package_ids[0], 'picking_id':[]}
            self.copy(res, default_vals)
        return res
    

class stock(models.Model):
    
    _inherit = "stock.invoice.onshipping"
    
    @api.multi
    def create_invoice(self):
        context=self._context
        if context is None:
            context = {}
        invoice_ids = []
        res = super(stock, self).create_invoice()
        invoice_ids += res.values()
        picking_env = self.env['stock.picking']
        invoice_env = self.env['account.invoice']
        active_picking = picking_env.browse(context.get('active_id', False))
        if active_picking:
            invoice_env.write({'shipcharge':active_picking.shipcharge })
        return res

