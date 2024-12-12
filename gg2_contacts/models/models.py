# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
# from mock.mock import self

class tsaexto(models.Model):
    _inherit = ['res.partner']
#
    x_balance_owing = fields.Float(string='Balance Owing', help='', copy=True, readonly=False, required=False, selectable=True)
    x_import_ref = fields.Char(string='TS Import Ref', help='', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_custno = fields.Char(string='SBT Custno', help='', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_disc = fields.Float(string='SBT Discount', help='Discount from SBT - taken from the DISC field in the arcust table', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_fields = fields.Text(string='SBT Fields', help='A collection of some of the more important fields from SBT (the previous accounting system used by Technical Solutions)', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_ref = fields.Char(string='SBT Ref', help='', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_vendno = fields.Char(string='SBT vendno', help='', copy=True, readonly=False, required=False, selectable=True)
    x_shortcut = fields.Char(string='Our Shortcut(s)', help='', copy=True, readonly=False, required=False, selectable=True)
    x_v8_id = fields.Char(string='V8 Id', help='', copy=True, readonly=False, required=False, selectable=True)
