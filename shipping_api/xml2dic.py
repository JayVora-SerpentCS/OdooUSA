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
from lxml import etree


def dictlist(node):
	res = {}
	res[node.tag] = []
	xmltodict(node, res[node.tag])
	reply = {}
	reply[node.tag] = res[node.tag]
	return reply


def xmltodict(node, res):
	rep = {}
	if len(node):
		for n in list(node):
			rep[node.tag] = []
			value = xmltodict(n, rep[node.tag])
			if len(n):
				value = rep[node.tag]
				res.append({n.tag: value})
			else :
				res.append(rep[node.tag][0])
	else:
		value = {}
		value = node.text
		res.append({node.tag: value})
	return


def main(xml_string):
	tree = etree.fromstring(xml_string)
	res = dictlist(tree)
	return res


if __name__ == '__main__' :
	main()
