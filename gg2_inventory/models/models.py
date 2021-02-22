# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

class tsaextt(models.Model):
    _inherit = ['stock.picking']

    def quick_do (self):
        #pdb.set_trace()
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))
        i = 0
        
        for pick in self.move_line_ids_without_package:
            if (pick.quantity_done == 0) or (pick.quantity_done > pick.product_uom_qty):
                pick.quantity_done = pick.product_uom_qty
                i = i + 1
                # SYNTAX ERROR raise UserError(_('Number of items processed: %d line_id= %d') % i, % pick.id)
        raise UserError(_('Number of items processed: %d') % i)

    # def quick_do (self, cr, uid, ids, context=None):
        # pack_op_obj = self.pool['stock.pack.operation']
        # data_obj = self.pool['ir.model.data']
        # for pick in self.browse(cr, uid, ids, context=context):
            # for operation in pick.pack_operation_ids:
                # if (operation.qty_done == 0) or (operation.qty_done > operation.product_qty):
                    # operation.qty_done = operation.product_qty


    x_extra_notes = fields.Text(string='Notes / References', help='Use this field to add extra notes and references (e.g. to appear on packing slips ..)', copy=True, readonly=False, required=False, selectable=True)
    x_extra_notes_ext = fields.Text(string='Notes for TSA Staff', help='Will *not appear on delivery docket', copy=True, readonly=False, required=False, selectable=True)
    x_my_location = fields.Many2one('stock.location', string='My Location', help='Use with the To My Location button to change the To location', copy=True, readonly=False, required=False, selectable=True)
    x_ship_in_out_date = fields.Date(string='Date Goods Sent / Received', help='', copy=False, readonly=False, required=False, selectable=True)
    x_special_address = fields.Many2one('res.partner', string='New Delivery Address', help='Fill in this field if a different delivery address is required to that originally provided on the order', copy=True, readonly=False, required=False, selectable=True)
