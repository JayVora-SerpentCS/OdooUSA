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

"""
Package Movement Information Service
====================================
This package contains classes to check service availability, route, and postal
codes. Defined by the PackageMovementInformationService WSDL file. 
"""
from .. base_service import FedexBaseService, FedexError


class FedexPostalCodeNotFound(FedexError):
    """
    Exception: Sent when the postalcode is missing.
    """
    pass


class FedexInvalidPostalCodeFormat(FedexError):
    """
    Exception: Sent when the postal code is invalid
    """
    pass


class PostalCodeInquiryRequest(FedexBaseService):
    """
    The postal code inquiry enables customers to validate postal codes
    and service commitments.
    """

    def __init__(self, config_obj, postal_code=None, country_code=None, *args, **kwargs):
        """
        Sets up an inquiry request. The optional keyword args
        detailed on L{FedexBaseService} apply here as well.
        @type config_obj: L{FedexConfig}
        @param config_obj: A valid FedexConfig object
        @param postal_code: a valid postal code
        @param country_code: ISO country code to which the postal code belongs to.
        """
        self._config_obj = config_obj

        # Holds version info for the VersionId SOAP object.
        self._version_info = {'service_id': 'pmis', 'major': '4',
                             'intermediate': '0', 'minor': '0'}
        self.PostalCode = postal_code
        self.CountryCode = country_code
        # Call the parent FedexBaseService class for basic setup work.
        super(PostalCodeInquiryRequest, self).__init__(self._config_obj,
                                                'PackageMovementInformationService_v4.wsdl',
                                                *args, **kwargs)

    def _check_response_for_request_errors(self):
        """
        Checks the response to see if there were any errors specific to
        this WSDL.
        """
        if self.response.HighestSeverity == "ERROR":
            for notification in self.response.Notifications:
                if notification.Severity == "ERROR":
                    if "Postal Code Not Found" in notification.Message:
                        raise FedexPostalCodeNotFound(notification.Code, notification.Message)

                    elif "Invalid Postal Code Format" in self.response.Notifications:
                        raise FedexInvalidPostalCodeFormat(notification.Code, notification.Message)
                    else:
                        raise FedexError(notification.Code, notification.Message)

    def _prepare_wsdl_objects(self):
        pass

    def _assemble_and_send_request(self):
        """
        Fires off the Fedex request.
        @warning: NEVER CALL THIS METHOD DIRECTLY. CALL send_request(), WHICH RESIDES
            ON FedexBaseService AND IS INHERITED.
        """
        client = self.client
        # We get an exception like this when specifying an IntegratorId:
        # suds.TypeNotFound: Type not found: 'IntegratorId'
        # Setting it to None does not seem to appease it.
        del self.ClientDetail.IntegratorId
        # Fire off the query.
        response = client.service.postalCodeInquiry(WebAuthenticationDetail=self.WebAuthenticationDetail,
                                        ClientDetail=self.ClientDetail,
                                        TransactionDetail=self.TransactionDetail,
                                        Version=self.VersionId,
                                        PostalCode = self.PostalCode,
                                        CountryCode = self.CountryCode)
        return response
