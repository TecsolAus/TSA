# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

class TsaAccountInvoice(models.Model):
    _inherit = ['account.move']

    @api.depends('ref', 'commercial_partner_id')
    def action_post(self):
        for invoice in self:
            # Refuse to validate a customer invoice, vendor bill, refund or receipt if there already exists one with the same reference for the same partner,
            if invoice.move_type in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund', 'in_receipt', 'out_receipt') and invoice.ref:
                DupeSet = self.search([('type', '=', invoice.move_type), 
				                ('ref', '=', invoice.ref),
                                ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                                ('id', '!=', invoice.id)
                                ])
                if DupeSet:
                    i = 0
                    for dupe in DupeSet:
                        i = i + 1
                        if i == 1:
                            myinvlist = dupe.name
                        else:
                            myinvlist = myinvlist + " & " + dupe.name
                    raise UserError(_(
                        "Duplicate Reference, ( " + invoice.ref + " ) detected in: " + myinvlist))
        return super(TsaAccountInvoice, self).action_post()

    @api.depends('partner_id')
    def _get_customer_email(self):
        for record in self:
            record['x_customer_email'] = record.partner_id.email
    @api.depends('name')
    def _get_name_truncated(self):
        for record in self:
            if (record.name):
                if (len(record.name) > 32):
                    record['x_name_truncated'] = (record.name[:30] + '..')
                else:
                    record.name
            else:
                record.name

    name = fields.Char(readonly=False)
    reference = fields.Char(readonly=False)
    x_customer_email = fields.Char(string='Email', help='Read-only display of Customer or Vendors Email Address (if defined in Contacts)', copy=False, readonly=True, required=False, selectable=False, compute='_get_customer_email')
    x_items_for_partner_id = fields.Many2one('res.partner', string='Items For', help='', copy=True, readonly=False, required=False, selectable=True)
    x_tracking_ref = fields.Char(string='Tracking Ref', help='', copy=False, readonly=False, required=False, selectable=True)
    x_name_truncated = fields.Char(string='Ref / Desc', copy=False, readonly=True, required=False, selectable=False, compute='_get_name_truncated')
    x_extra_notes = fields.Text(string='Additional Notes', help='', copy=False, readonly=False, required=False, selectable=True)

class tsaextb(models.Model):
    _inherit = ['account.move']

    x_credit_or_debit_note = fields.Boolean(string='Credit/Debit Note', help='Credit Note or Debit Note', copy=True, readonly=False, required=False, selectable=True)
    x_gst_clearing = fields.Boolean(string='GST Clearing', help='Please tick if this journal is for GST Clearing', copy=True, readonly=False, required=False, selectable=True)

class tsaextc(models.Model):
    _inherit = ['account.move.line']

    @api.depends('credit')
    def _get_credit_rounded(self):
        for record in self:
            record['x_credit_rounded']=round(record.credit,6)

    x_credit_rounded = fields.Monetary(string='Credit Rounded', help='', copy=False, readonly=True, required=False, selectable=False, compute='_get_credit_rounded')

class tsaextd(models.Model):
    _inherit = ['account.payment']

    @api.depends('payment_type', 'amount')
    def _get_amount_signed(self):
        for record in self:
            if record['payment_type'] == 'outbound':
                record['x_amount_signed'] = - record['amount']
            else:
                record['x_amount_signed'] = record['amount']
    @api.depends('journal_id')
    def _get_payment_method(self):
        for record in self:
            if len(record.journal_id.name) > 17:
                record['x_payment_method'] = (record.journal_id.name[:15] + '..')
            else:
                record.journal_id
    @api.depends('payment_type')
    def _get_payment_type_trunc(self):
        for record in self:
            if record['payment_type'] == 'outbound':
                record['x_payment_type'] = 'Send'
            if record['payment_type'] == 'inbound':
                record['x_payment_type'] = 'Receive'
            if record['payment_type'] == 'transfer':
                record['x_payment_type'] = 'Transfer'
            else:
                record['x_payment_type'] = 'Unknown'

    x_amount_signed = fields.Monetary(string='Amount', help='Negative if payment_type=outbound (Send Money) else positive', copy=False, readonly=True, required=False, selectable=False, compute='_get_amount_signed')
    x_payment_method = fields.Char(string='Payment Method', help='', copy=False, readonly=True, required=False, selectable=False, compute='_get_payment_method')
    x_payment_type = fields.Char(string='Direction', help='', copy=False, readonly=True, required=False, selectable=False, compute='_get_payment_type_trunc')
