# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

class tsaextl(models.Model):
    _inherit = ['purchase.order']

    @api.depends('partner_id')
    def _get_customer_email(self):
        for record in self:
            record['x_customer_email']=record.partner_id.email

    x_back_count = fields.Integer(string='No. of <Back> button hits', help='The number of times the Back button has been used', copy=True, readonly=False, required=False, selectable=True)
    x_customer_email = fields.Char(string='Customer Email', help='Read-only display of Customer Email Address (if defined in Contacts)', copy=False, readonly=True, required=False, selectable=False, compute='_get_customer_email')
    x_ordered_by = fields.Char(string='Ordered By', help='Who Placed this order / Our Ref', copy=True, readonly=False, required=False, selectable=True)

class tsaextm(models.Model):
    _inherit = ['purchase.order.line']

    x_sequence = fields.Integer(string='Sequence', help='Sequence No. (e.g. use to assist with cross-checking orders)', copy=True, readonly=False, required=False, selectable=True)

