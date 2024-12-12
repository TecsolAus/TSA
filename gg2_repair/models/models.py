# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
# from mock.mock import self

class tsaextg(models.Model):
    _inherit = ['repair.order']

    x_delivery_address_id = fields.Many2one('res.partner', string='Alter Delivery Address', help='', copy=True, readonly=False, required=False, selectable=True)
    x_received_by = fields.Many2one('res.users', string='Received By', help='', copy=True, readonly=False, required=False, selectable=True)
    x_reported_by_customer = fields.Text(string='Reported by Customer', help='', copy=True, readonly=False, required=False, selectable=True)
    x_serial = fields.Char(string='Serial Id', help='', copy=True, readonly=False, required=False, selectable=True)
    x_technician = fields.Many2one('res.users', string='Technician', help='', copy=True, readonly=False, required=False, selectable=True)
    x_time_spent = fields.Float(string='Time Spent (Hours)', help='', copy=True, readonly=False, required=False, selectable=True)
