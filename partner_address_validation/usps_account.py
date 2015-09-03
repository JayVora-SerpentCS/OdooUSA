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
# import pdb


class usps_account(models.Model):
    '''
        USPS Account details
    '''
    _name = "usps.account"
    name = fields.Char(string='Company Name')
    usps_userid = fields.Char(string='User ID')
    usps_url_test = fields.Char(string='Test URL', size=512)
    usps_url = fields.Char(string='Production URL', size=512)
    test_mode = fields.Boolean(string='Test Mode', default=lambda * a: True)

    @api.multi
    def address_validation(self, address_id):
        # pdb.set_trace()
        """ This function is called from the wizard.Performs the actual computing in address validation """
        status = 0
        error_msg = ''
        usps_accounts = self.env['usps.account'].search([])

        if not usps_accounts:
            warning = {
                'title': "No USPS account!",
                'message': "No USPS account found for validation."
            }
            return {'warning': warning}

        if usps_accounts and address_id:
            usps_account = self.env['usps.account'].browse(usps_accounts.id)
            if type(address_id) is list or type(address_id) is tuple:
                address_id = address_id[0]
            partner_address = self.env['res.partner'].browse(address_id)
            url = usps_account.test_mode and usps_account.usps_url_test or usps_account.usps_url
            userid = usps_account.usps_userid or ''

            from usps.addressinformation import base
            connector = base.AddressValidate(url)
            ret_list = []
            try:
                response = connector.execute([{'Address2': partner_address.street,
                                               'City': partner_address.city,
                                               'State': partner_address.state_id and partner_address.state_id.code or '',
                                               'Zip5': partner_address.zip or ''
                                               }])[0]
                error_msg = "Success: Address is valid."

            except base.USPSXMLError, e:
                error_msg = error_msg + str(e)

            except Exception, e:

                error_msg = error_msg + str(e)
            return {
                'addr_status': status,
                'error_msg': error_msg,
                'address_list': ret_list
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
