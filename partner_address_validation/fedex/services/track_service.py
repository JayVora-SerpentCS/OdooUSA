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
Tracking Service Module
=======================
This package contains the shipment tracking methods defined by Fedex's 
TrackService WSDL file. Each is encapsulated in a class for easy access. 
For more details on each, refer to the respective class's documentation.
"""
from .. base_service import FedexBaseService, FedexError


class FedexInvalidTrackingNumber(FedexError):
    """
    Exception: Sent when a bad tracking number is provided.
    """
    pass


class FedexTrackRequest(FedexBaseService):
    """
    This class allows you to track shipments by providing a tracking
    number or other identifying features. By default, you
    can simply pass a tracking number to the constructor. If you would like
    to query shipments based on something other than tracking number, you will
    want to read the documentation for the L{__init__} method. 
    Particularly, the tracking_value and package_identifier arguments.
    """

    def __init__(self, config_obj, *args, **kwargs):
        """
        Sends a shipment tracking request. The optional keyword args
        detailed on L{FedexBaseService} apply here as well.
        @type config_obj: L{FedexConfig}
        @param config_obj: A valid FedexConfig object.
        """
        self._config_obj = config_obj
        # Holds version info for the VersionId SOAP object.
        self._version_info = {'service_id': 'trck', 'major': '4', 
                             'intermediate': '0', 'minor': '0'}
        self.TrackPackageIdentifier = None
        """@ivar: Holds the TrackPackageIdentifier WSDL object."""
        # Call the parent FedexBaseService class for basic setup work.
        super(FedexTrackRequest, self).__init__(self._config_obj,
                                                'TrackService_v4.wsdl',
                                                *args, **kwargs)

    def _prepare_wsdl_objects(self):
        """
        This sets the package identifier information. This may be a tracking
        number or a few different things as per the Fedex spec.
        """
        self.TrackPackageIdentifier = self.client.factory.create('TrackPackageIdentifier')
        # Default to tracking number.
        self.TrackPackageIdentifier.Type = 'TRACKING_NUMBER_OR_DOORTAG'

    def _check_response_for_request_errors(self):
        """
        Checks the response to see if there were any errors specific to
        this WSDL.
        """
        if self.response.HighestSeverity == "ERROR":
            for notification in self.response.Notifications:
                if notification.Severity == "ERROR":
                    if "Invalid tracking number" in notification.Message:
                        raise FedexInvalidTrackingNumber(notification.Code, notification.Message)
                    else:
                        raise FedexError(notification.Code, notification.Message)

    def _assemble_and_send_request(self):
        """
        Fires off the Fedex request.
        @warning: NEVER CALL THIS METHOD DIRECTLY. CALL send_request(), WHICH RESIDES
            ON FedexBaseService AND IS INHERITED.
        """
        client = self.client
        # Fire off the query.
        response = client.service.track(WebAuthenticationDetail=self.WebAuthenticationDetail,
                                        ClientDetail=self.ClientDetail,
                                        TransactionDetail=self.TransactionDetail,
                                        Version=self.VersionId,
                                        PackageIdentifier=self.TrackPackageIdentifier)
        return response
