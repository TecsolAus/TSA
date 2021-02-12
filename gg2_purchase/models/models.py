# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

class TsaSaleOrder(models.Model):
    _inherit = ['sale.order']

    @api.depends('partner_id', ' client_order_ref', 'name')
    def action_confirm(self):
        for order in self:
            # Refuse to validate a Sales Order if there already exists one with the same reference for the same partner
            if order.client_order_ref:
                DupeOrder = self.search([('state', '!=', 'cancel'), ('client_order_ref', '=', order.client_order_ref), ('partner_id', '=', order.partner_id.id), ('id', '!=', order.id)])
                if DupeOrder:
                    i = 0
                    for dupe in DupeOrder:
                        i = i + 1
                        if i == 1:
                            DupeNameList = dupe.name
                        else:
                            DupeNameList = DupeNameList + ' & ' + dupe.name
                    raise UserError(_("Duplicate Customer Reference, " + order.client_order_ref + " found in order(s): " + DupeNameList))
        return super(TsaSaleOrder, self).action_confirm()

    @api.depends('partner_id')
    def _get_customer_email(self):
        for record in self:
            record['x_customer_email']=record.partner_id.email

    x_customer_email = fields.Char(string='Customer Email',
                                   help='Read-only display of Customer Email Address (if defined in Contacts)',
                                   copy=False, readonly=True, required=False, selectable=False,
                                   compute='_get_customer_email')
    x_tracking_ref = fields.Char(string='Tracking Ref', help='', copy=False, readonly=False, required=False,                               selectable=True)

class tsaextq(models.Model):
    _inherit = ['sale.order.line']

    @api.depends('product_uom_qty', 'qty_delivered')
    def _get_qty_backorder(self):
        for record in self:
            record['x_qty_backorder'] = record['product_uom_qty'] - record['qty_delivered']

    x_qty_backorder = fields.Float(string='Quantity on Backorder', help='The quantity that is on back-order (i.e. to be delivered at a later date)', copy=False, readonly=True, required=False, selectable=False, compute='_get_qty_backorder')

