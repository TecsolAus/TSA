# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

# TO DO: Make database name always appear in the top banner by changing the Java Script
# /odoo/odoo-server/addons/web/static/src/js/chrome/user_menu.js
# or 
# /usr/lib/python3/dist-packages/odoo/addons/web/static/src/js/chrome/user_menu.js
#
# FROM THIS
#            var topbar_name = session.name;
#            if (session.debug) {
#                topbar_name = _.str.sprintf("%s (%s)", topbar_name, session.db);
#            }#
# TO THIS
#            var topbar_name = session.name;
#            topbar_name = _.str.sprintf("%s (%s)", topbar_name, session.db);
#            if (session.debug) {
#                topbar_name = _.str.sprintf("%s DEBUG", topbar_name);
#                //ORIG: topbar_name = _.str.sprintf("%s (%s)", topbar_name, session.db);
#            }

class TsaAccountInvoice(models.Model):
    _inherit = ['account.move']

    @api.depends('ref', 'commercial_partner_id')
    def action_post(self):
        for invoice in self:
            # Refuse to validate a customer invoice, vendor bill, refund or receipt if there already exists one with the same reference for the same partner,
            if invoice.type in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund', 'in_receipt', 'out_receipt') and invoice.ref:
                DupeSet = self.search([('type', '=', invoice.type), 
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

class tsaexte(models.Model):
    _inherit = ['hr.attendance']

    x_notes = fields.Text(string='Notes / Comments', help='Add notes and comments as required', copy=True, readonly=False, required=False, selectable=True)

class tsaextf(models.Model):
    _inherit = ['mrp.bom.line']

    x_designator = fields.Char(string='Designator', help='', copy=True, readonly=False, required=False, selectable=True)
    x_footprint = fields.Char(string='Footprint', help='', copy=True, readonly=False, required=False, selectable=True)

class tsaextg(models.Model):
    _inherit = ['repair.order']

    x_delivery_address_id = fields.Many2one('res.partner', string='Alter Delivery Address', help='', copy=True, readonly=False, required=False, selectable=True)
    x_received_by = fields.Many2one('res.users', string='Received By', help='', copy=True, readonly=False, required=False, selectable=True)
    x_reported_by_customer = fields.Text(string='Reported by Customer', help='', copy=True, readonly=False, required=False, selectable=True)
    x_serial = fields.Char(string='Serial Id', help='', copy=True, readonly=False, required=False, selectable=True)
    x_technician = fields.Many2one('res.users', string='Technician', help='', copy=True, readonly=False, required=False, selectable=True)
    x_time_spent = fields.Float(string='Time Spent (Hours)', help='', copy=True, readonly=False, required=False, selectable=True)

class tsaexth(models.Model):
    _inherit = ['product.category']

    x_description = fields.Char(string='Description', help='', copy=True, readonly=False, required=False, selectable=True)

class tsaexti(models.Model):
    _inherit = ['product.template']

    @api.depends('x_item_height_mfr','x_item_width_mfr','x_item_depth_mfr')
    def _get_volume_mfr_cm3(self):
        for record in self:
            record['x_item_volume_mfr_cm3']=record.x_item_height_mfr * record.x_item_width_mfr * record.x_item_depth_mfr
    @api.depends('x_item_height','x_item_length','x_item_depth')
    def _get_volume_cm3(self):
        for record in self:
            record['x_volume_cm3']=record.x_item_height * record.x_item_length * record.x_item_depth

    @api.depends('product_variant_ids.x_total_qty_sold')
    def _total_qty_sold2(self):
        for product in self:
            product.x_total_qty_sold = sum([p.x_total_qty_sold for p in product.product_variant_ids])

    @api.depends('product_variant_ids.x_total_qty_bought')
    def _total_qty_bought2(self):
        for product in self:
            product.x_total_qty_bought = sum([p.x_total_qty_bought for p in product.product_variant_ids])

    @api.depends('product_variant_ids.x_total_qty_made')
    def _total_qty_made2(self):
        for product in self:
            product.x_total_qty_made = sum([p.x_total_qty_made for p in product.product_variant_ids])

    x_total_qty_made = fields.Integer(compute='_total_qty_made2', string='Made')
    x_total_qty_bought = fields.Integer(compute='_total_qty_bought2', string='Bought')
    x_total_qty_sold = fields.Integer(compute='_total_qty_sold2', string='Sold')


    x_bcause = fields.Boolean(string='BCause Item', help='Tick if item is to be published on the BCause Website', copy=True, readonly=False, required=False, selectable=True)
    x_comment = fields.Text(string='Comment / Notes', help='Add whatever notes you want to this field', copy=True, readonly=False, required=False, selectable=True)
    x_cost_price = fields.Float(string='Cost Price', help='Cost Price - TSA copy of standard_price field', copy=True, readonly=False, required=False, selectable=True)
    x_counted_date = fields.Datetime(string='Date and time Counted', help='', copy=True, readonly=False, required=False, selectable=True)
    x_counted_qty = fields.Float(string='Counted Qty', help='Quantity Counted at last Stocktake (Please complete the Date field too)', copy=True, readonly=False, required=False, selectable=True)
    x_default_location = fields.Char(string='Default Location', help='The location where we normally store this product within our warehouse.', copy=True, readonly=False, required=False, selectable=True)
    x_default_location2 = fields.Char(string='Alternative Location', help='Excess stock will be placed in this location', copy=True, readonly=False, required=False, selectable=True)
    x_default_position = fields.Char(string='Position (Rack, Shelf)', help='Position of the item(s) - e.g. the last time anyone checked.  Rack: numbered from the left when faceing.  Shelf: numbered from the floor upwards  F,1,2,..,T where F=Floor, 1=1st Shelf, 2=2nd Shelf, .. , T=Top Shelf', copy=False, readonly=False, required=False, selectable=True)
    x_default_position2 = fields.Char(string='Alternative Position', help='Position of excess stock:  Rack: numbered from the left when faceing.  Shelf: numbered from the floor upwards  F,1,2,..,T where F=Floor, 1=1st Shelf, 2=2nd Shelf, .. , T=Top Shelf', copy=True, readonly=False, required=False, selectable=True)
    x_expert = fields.Many2one('res.users', string='Who to ask', help='The person to ask about this product - who knows most about it', copy=True, readonly=False, required=False, selectable=True)
    x_expert2 = fields.Many2one('res.users', string='Who to ask (alt)', help='Alternative source of knowledge about this item', copy=True, readonly=False, required=False, selectable=True)
    x_image_filename = fields.Char(string='Image Filename', help='', copy=True, readonly=False, required=False, selectable=True)
    x_imported_date = fields.Datetime(string='Date Imported', help='Datetime this product was imported', copy=True, readonly=False, required=False, selectable=True)
    x_item_depth = fields.Float(string='Depth (cm)', help='', copy=True, readonly=False, required=False, selectable=True)
    x_item_depth_mfr = fields.Float(string='Depth from Mfr (cm)', help='Depth as supplied by the manufacturer or vendor of the item', copy=True, readonly=False, required=False, selectable=True)
    x_item_height = fields.Float(string='Height (cm)', help='', copy=True, readonly=False, required=False, selectable=True)
    x_item_height_mfr = fields.Float(string='Height from mfr (cm)', help='Height as supplied by the manufacturer or vendor of the item', copy=True, readonly=False, required=False, selectable=True)
    x_item_length = fields.Float(string='Length (cm)', help='', copy=True, readonly=False, required=False, selectable=True)
    x_item_volume_mfr = fields.Float(string='Volume from Mfr (cm3)', help='Volume as supplied by the manufacturer or vendor of the item', copy=True, readonly=False, required=False, selectable=True)
    x_item_volume_mfr_cm3 = fields.Float(string='Manufacturer / Supplier Volume in cm3', help='', copy=False, readonly=True, required=False, selectable=False, compute='_get_volume_mfr_cm3')
    x_item_weight_mfr = fields.Float(string='Item weight as provided by the Manufacturer or the Supplier', help='', copy=True, readonly=False, required=False, selectable=True)
    x_item_width_mfr = fields.Float(string='Width from Mfr (cm)', help='Width as supplied by the manufacturer or vendor of the item', copy=True, readonly=False, required=False, selectable=True)
    x_jos_product_id = fields.Char(string='Jos Product Id', help='', copy=True, readonly=False, required=False, selectable=True)
    x_odoo_qty_b4_stocktake = fields.Float(string='Odoo Quantity Before Last Stocktake', help='We use this field to store the previous Stock-On-Hand quantity of the item prior to it being zeroed and re-populated with the Stocktake value.  The field is NOT automatically populated but must be filled in manually - probably as part of a csv export --> import operation.', copy=True, readonly=False, required=False, selectable=True)
    x_odoo_qty_capture_date = fields.Datetime(string='Odoo Quantity Capture Date', help='Date to which the field x_odoo_qty_b4_stocktake (Odoo Quanity Before Last Stocktake) reflects what Odoo said was the Stock-On-Hand quantity', copy=True, readonly=False, required=False, selectable=True)
    x_odoo_qty_last_30Jun = fields.Float(string='Odoo Qty 30 Jun', help='The qty Odoo thought we had last 30 Jun.  This field is NOT automatically populated.  It should be populated for all products at close-of-business 30 June by exporting Quantity-On-Hand and re-importing the value to this field.  Note:  To export you need to select all fields.', copy=True, readonly=True, required=False, selectable=True)
    x_sbt_fields = fields.Text(string='SBT Fields', help='', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_item = fields.Char(string='SBT Item', help='', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_last_buy = fields.Date(string='SBT Last Buy Date', help='The last date that this item was received or ordered in SBT', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_last_sold = fields.Date(string='SBT Last Sold Date', help='The last date recorded in SBT for a sale of this item', copy=True, readonly=False, required=False, selectable=True)
    x_sbt_product_sku = fields.Char(string='SBT Product SKU', help='', copy=True, readonly=False, required=False, selectable=True)
    x_shortcut = fields.Char(string='Our Shortcut(s)', help='', copy=True, readonly=False, required=False, selectable=True)
    x_v8_id = fields.Char(string='v8 id', help='', copy=True, readonly=False, required=False, selectable=True)
    x_volume_cm3 = fields.Float(string='Volume (cm3)', help='', copy=False, readonly=True, required=False, selectable=False, compute='_get_volume_cm3')

class tsaextk(models.Model):
    _inherit = ['project.task']

    x_external_document_a = fields.Html(string='External Document A', help='Use this field to add a hyperlink to a document or folder on your computer', copy=True, readonly=False, required=False, selectable=True)
    x_external_document_b = fields.Html(string='External Document B', help='', copy=True, readonly=False, required=False, selectable=True)

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

#class tsaextr(models.Model):
#    _inherit = ['stock.inventory.line']
#
#    x_new_location_id = fields.Many2one('stock.location', string='NewLocation', help='A note of what you need to MANUALLY change the default_location to become.  IMPORTANT: As yet this will NOT update the default_location on the item itself - that would be nice if it did - PFE !!!', copy=False, readonly=False, required=False, selectable=True)

## NOTE: stock.pack.operation does not exist in v12 ###
#class tsaexts(models.Model):
#    _inherit = ['stock.pack.operation']
#
#    x_my_loc_select = fields.Boolean(string='Tick to include in My-Location operation', help='', copy=True, readonly=False, required=False, selectable=True)
#    x_product_tmpl_id = fields.Integer(string='x_product_tmpl_id', help='', copy=False, readonly=True, required=False, selectable=False)

class tsaextt(models.Model):
    _inherit = ['stock.picking']

    def quick_do (self):
        #pdb.set_trace()
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))
        i = 0
        
        # for pick in self.move_line_ids:
            # if (pick.qty_done == 0) or (pick.qty_done > pick.product_uom_qty):
                # pick.qty_done = pick.product_uom_qty
                # i = i + 1
                # # SYNTAX ERROR raise UserError(_('Number of items processed: %d line_id= %d') % i, % pick.id)
        raise UserError(_('STILL UNDER CONSTRUCTION: Number of items processed: %d') % i)

    # def quick_do (self, cr, uid, ids, context=None):
        # pack_op_obj = self.pool['stock.pack.operation']
        # data_obj = self.pool['ir.model.data']
        # for pick in self.browse(cr, uid, ids, context=context):
            # for operation in pick.pack_operation_ids:
                # if (operation.qty_done == 0) or (operation.qty_done > operation.product_qty):
                    # operation.qty_done = operation.product_qty

#    x_carrier_id = fields.Many2one(string='Carrier:', help='Carrier company - who delivers the items', copy=False, readonly=False, required=False, selectable=True, related='delivery.carrier')
    x_extra_notes = fields.Text(string='Notes / References', help='Use this field to add extra notes and references (e.g. to appear on packing slips ..)', copy=True, readonly=False, required=False, selectable=True)
    x_extra_notes_ext = fields.Text(string='Notes for TSA Staff', help='Will *not appear on delivery docket', copy=True, readonly=False, required=False, selectable=True)
    x_my_location = fields.Many2one('stock.location', string='My Location', help='Use with the To My Location button to change the To location', copy=True, readonly=False, required=False, selectable=True)
    x_ship_in_out_date = fields.Date(string='Date Goods Sent / Received', help='', copy=False, readonly=False, required=False, selectable=True)
    x_special_address = fields.Many2one('res.partner', string='New Delivery Address', help='Fill in this field if a different delivery address is required to that originally provided on the order', copy=True, readonly=False, required=False, selectable=True)

class tsaextu(models.Model):
    _inherit = ['product.product']

    def _total_qty_sold(self):
        r = {}
        domain = [
            ('state', 'in', ['sale', 'done']),
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['sale.order.line'].read_group(domain, ['product_id', 'qty_delivered'], ['product_id']):
            r[group['product_id'][0]] = group['qty_delivered']
        for product in self:
            product.x_total_qty_sold = r.get(product.id, 0)
        return r

    def _total_qty_bought(self):
        r = {}
        domain = [
            ('state', 'in', ['purchase', 'done']),
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['purchase.order.line'].read_group(domain, ['product_id', 'qty_received'], ['product_id']):
            r[group['product_id'][0]] = group['qty_received']
        for product in self:
            product.x_total_qty_bought = r.get(product.id, 0)
        return r

    def _total_qty_made(self):
        r = {}
        domain = [
            ('state', 'in', ['done']),
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['mrp.production'].read_group(domain, ['product_id', 'product_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_qty']
        for product in self:
            product.x_total_qty_made = r.get(product.id, 0)
        return r

    x_total_qty_made = fields.Integer(compute='_total_qty_made', string='Sold')
    x_total_qty_bought = fields.Integer(compute='_total_qty_bought', string='Bought')
    x_total_qty_sold = fields.Integer(compute='_total_qty_sold', string='Sold')

class TsaRpt050BankJouA(models.Model):
    _name = "gg2.bankjou"
    _description = "Bank Statement to Journal X-Ref"
    _auto = False

    jou_entry_id = fields.Integer(string='JouEntryId', readonly=True)
    statement_id = fields.Integer(string='StmtId', readonly=True)
    statement_line_id = fields.Integer(string='StmtLineId', readonly=True)
    jou_item = fields.Char(string='JouItem', readonly=True)
    jou_line_ref = fields.Char(string='JouItemRef', readonly=True)
    jouitem_debit = fields.Float(string='ItemDebit', readonly=True)
    jouitem_credit = fields.Float(string='ItemCredit', readonly=True)
    jouentryid = fields.Many2one('account.move', string='JouEntry', readonly=True)
    jou_entry = fields.Char(string='JouEntry', readonly=True)
    stmtid = fields.Many2one('account.bank.statement', string='StmtId', readonly=True)
    stmt = fields.Char(string='StmtName', readonly=True)
    stmtlineid = fields.Many2one('account.bank.statement.line', string='StmtLineId', readonly=True)
    stmt_row = fields.Integer(string='StmtRow', readonly=True)
    stmt_line_desc = fields.Char(string='StmtLineDesc', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    joudate = fields.Date(string='JouDate', readonly=True)

    @api.model
    def init(self):
        self._cr.execute("""CREATE OR REPLACE VIEW gg2_bankjou AS (
        SELECT
            account_move_line.id,
            account_move_line.move_id AS jou_entry_id,
            account_move_line.statement_id,
            account_move_line.statement_line_id,
            account_move_line.name AS jou_item,
            account_move_line.ref AS jou_line_ref,
            account_move_line.debit AS jouitem_debit,
            account_move_line.credit AS jouitem_credit,
            account_move.id AS jouentryid,
            account_move.name AS jou_entry,
            account_bank_statement.id AS stmtid,
            account_bank_statement.name AS stmt,
            account_bank_statement_line.id AS stmtlineid,
            account_bank_statement_line.sequence AS stmt_row,
            account_bank_statement_line.name AS stmt_line_desc,
            account_bank_statement_line.amount AS amount,
            account_move.date AS joudate
        FROM 
            ((account_move_line 
            INNER JOIN account_move ON account_move_line.move_id = account_move.id)
            INNER JOIN account_bank_statement_line ON account_move_line.statement_line_id = account_bank_statement_line.id)
            INNER JOIN account_bank_statement ON account_move_line.statement_id = account_bank_statement.id
        )""")

    # OLD CODE - v12 was    def showjournalentry(self, values):
    def showjournalentry(self):
        self.ensure_one()
        my_view_id = self.env.ref('account.view_move_form').id
        my_row_id = self.jou_entry_id
        print("My Row ID=%d" % my_row_id)
        # raise UserError(_('view id is: %d   Row id is: %d') % my_view_id, % my_row_id)
        return {
            'name': _('Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': my_view_id,
            'res_id': my_row_id,
            'context': {},
            'target': 'current',
        }

    # OLD CODE (at v12) was     def showbankstatement(self, values):
    def showbankstatement(self):
        self.ensure_one()
        my_view_id = self.env.ref('account.view_bank_statement_form').id
        my_row_id = self.statement_id
        print("My Row ID=%d" % my_row_id)
        # raise UserError(_('view id is: %d   Row id is: %d') % my_view_id, % my_row_id)
        return {
            'name': _('Bank Statement'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': my_view_id,
            'res_id': my_row_id,
            'context': {},
            'target': 'current',
        }


class TsaRpt080SalesToDeliverD(models.Model):
    _name = "gg2.rpt080"
    _description = "Invoiced Items not yet delivered"
    _auto = False

    name = fields.Char(readonly=True)
    invqty = fields.Float(readonly=True)
    qty_delivered = fields.Float(readonly=True)
    qty_delivered_manual = fields.Float(readonly=True)
    orderqty =  fields.Float(readonly=True)
    item =  fields.Char(readonly=True)
    soid =  fields.Many2one('sale.order', string='SO Id', readonly=True)
    sostate =  fields.Char(readonly=True)
    soname =  fields.Char(readonly=True)
    orderdate =  fields.Datetime(readonly=True)
    customer =  fields.Integer(readonly=True)
    invto =  fields.Integer(readonly=True)
    whotoinvoice = fields.Char(readonly=True)
    shipto =  fields.Integer(readonly=True)
    partnerid = fields.Many2one('res.partner', string='Client', readonly=True) # ? One2many ? Many2many
    productid = fields.Many2one('product.product', string='ProdId', readonly=True) # ? One2many ? Many2many
    itemcode = fields.Char(string='ItemCode', readonly=True)
    producttmplid = fields.Many2one('product.template', string='ProdTmplId', readonly=True)
    itemtype = fields.Char(string='ItemCode', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            sale_order_line.id AS id, 
            sale_order_line.name AS name, 
            sale_order_line.qty_invoiced AS invqty, 
            sale_order_line.qty_delivered AS qty_delivered,
            sale_order_line.qty_delivered_manual AS qty_delivered_manual,
            sale_order_line.product_uom_qty AS orderqty,
            sale_order_line.product_id AS item,
            sale_order.id AS soid,
            sale_order.state AS sostate,
            sale_order.name AS soname,
            sale_order.date_order AS orderdate,
            sale_order.partner_id AS customer,
            sale_order.partner_invoice_id AS invto,
            sale_order.partner_shipping_id AS shipto,
            res_partner.id AS partnerid,
            res_partner.display_name AS whotoinvoice,
            product_product.id as productid,
            product_product.default_code as itemcode,
            product_template.id as producttmplid,
            product_template.type as itemtype
        """

        for field in fields.values():
            select_ += field

        from_ = """
            sale_order_line 
            INNER JOIN sale_order ON sale_order_line.order_id = sale_order.id
            INNER JOIN res_partner ON sale_order.partner_invoice_id = res_partner.id
            INNER JOIN product_product ON sale_order_line.product_id = product_product.id
            INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id
            %s
        """ % from_clause
        
        where_ = """
            (sale_order_line.qty_delivered::numeric < sale_order_line.qty_invoiced::numeric)
            AND (sale_order_line.invoice_status::text = 'invoiced'::text)
            AND (sale_order_line.qty_invoiced::numeric >= 1::numeric)
            AND (sale_order_line.product_uom_qty::numeric >= 1::numeric)
            AND (sale_order_line.name NOT LIKE 'SHIPPING%')
            AND (sale_order_line.name NOT LIKE 'POST%')
            AND (sale_order_line.name NOT LIKE 'SVCE%')
            AND (sale_order_line.name NOT LIKE 'Courier%')
            AND (sale_order_line.name NOT LIKE 'SVCE%')
            AND (sale_order_line.name NOT LIKE 'Australia Post%')
            AND (sale_order_line.name NOT LIKE '[SHIPPING%')
            AND (sale_order_line.name NOT LIKE '[POST%')
            AND (sale_order_line.name NOT LIKE '[SVCE%')
            AND (sale_order_line.name NOT LIKE '[Courier%')
            AND (sale_order_line.name NOT LIKE '[SVCE%')
            AND (sale_order_line.name NOT LIKE '[Australia Post%')
            AND (sale_order.state::text <> 'draft'::text)
            AND (sale_order.state::text <> 'cancel'::text)
            AND (sale_order.state::text <> 'done'::text)
            AND (product_template.type::text <> 'service'::text)
            AND (product_template.type::text <> 'consu'::text)
            AND (product_product.default_code::text <> 'SHIPPING'::text)
            AND (product_product.default_code::text NOT ILIKE 'POST%'::text)
        """
        
        order_ = """
            sale_order.id DESC, 
            sale_order_line.name ASC
        """

        return '%s (SELECT %s FROM %s WHERE %s ORDER BY %s)' % (with_, select_, from_, where_, order_)

    # @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    # OLD CODE (v12) was     def showsalesorder(self, values):
    def showsalesorder(self):
        self.ensure_one()
        sale_order_view_id = self.env.ref('gg2.view_form_sale_order_tsa').id
        mysaleorderlineid = self.ids[0]
        mysaleorderline = self.env['sale.order.line'].search([('id','=',mysaleorderlineid)])
        mysaleorderid = mysaleorderline.order_id.id  # type: Union[int, Any]
        print("My Sale Order ID=%d" % mysaleorderid)
        # raise UserError(_('view id is: %d   sale order id is: %d') % sale_order_view_id, % mysaleorderid)
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': sale_order_view_id,
            'res_id': mysaleorderid,
            'context': {'id': mysaleorderid },
            'target': 'current',
        }


class TsaRpt082SalesToDeliverD(models.Model):
    _name = "gg2.rpt082"
    _description = "SOs Invoiced but not yet delivered"
    _auto = False

    sostate = fields.Char(readonly=True)
    soname = fields.Char(readonly=True)
    orderdate = fields.Datetime(readonly=True)
    whotoinvoice = fields.Char(readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            gg2_rpt080.soid AS id,
            gg2_rpt080.sostate AS sostate,
            gg2_rpt080.soname AS soname,
            gg2_rpt080.orderdate AS orderdate,
            gg2_rpt080.whotoinvoice AS whotoinvoice
        """

        for field in fields.values():
            select_ += field

        from_ = """
            gg2_rpt080
            %s
        """ % from_clause

        groupby_ = """
            gg2_rpt080.soid,
            gg2_rpt080.sostate,
            gg2_rpt080.soname,
            gg2_rpt080.orderdate,
            gg2_rpt080.whotoinvoice
            %s
        """ % groupby

        order_ = """
            gg2_rpt080.soid DESC
        """

        return '%s (SELECT %s FROM %s GROUP BY %s ORDER BY %s)' % (with_, select_, from_, groupby_, order_)

    # @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def showsalesorder(self):
        self.ensure_one()
        sale_order_view_id = self.env.ref('gg2.view_form_sale_order_tsa').id
        mysaleorderid = self.ids[0]
        print("My Sale Order ID=%d" % mysaleorderid)
        # raise UserError(_('view id is: %d   sale order id is: %d') % sale_order_view_id, % mysaleorderid)
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': sale_order_view_id,
            'res_id': mysaleorderid,
            'context': {},
            'target': 'current',
        }

class TsaRpt090BalanceSheetH(models.Model):
    _name = "gg2.rpt090"
    _description = "Balance Sheet"
    _auto = False

    account_id = fields.Float(readonly=True)
    acctid = fields.Many2one('account.account', readonly=True)
    moveid = fields.Many2one('account.move', readonly=True)
    accttypeid = fields.Many2one('account.account.type', readonly=True)
    code = fields.Char(readonly=True)
    name = fields.Char(readonly=True)
    codename = fields.Char(readonly=True)
    date = fields.Date(readonly=True)
    debit = fields.Float(readonly=True)
    credit = fields.Float(readonly=True)
    balance = fields.Float(readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            account_move_line.id AS id,
            account_move_line.account_id AS account_id,
            account_account.id AS acctid,
            account_account.code AS code, 
            account_account.name AS name,
            CONCAT(account_account.code, ' ', account_account.name) AS codename,
            account_move_line.date AS date, 
            (account_move_line.debit) AS debit, 
            (account_move_line.credit) AS credit, 
            (account_move_line.balance) AS balance,
            account_move.id AS moveid,
            account_account_type.id AS accttypeid
        """

        for field in fields.values():
            select_ += field

        from_ = """
            account_move_line
            INNER JOIN account_move ON account_move_line.move_id = account_move.id
            INNER JOIN account_account ON account_move_line.account_id = account_account.id
            INNER JOIN account_account_type ON account_account.user_type_id = account_account_type.id
            %s
        """ % from_clause

        where_ = """
            ((account_move.state::text) = ('posted'::text)) AND
            ((account_account_type.internal_group::text) = ('asset'::text)) OR
            ((account_account_type.internal_group::text) = ('liability'::text))
        """

        order_ = """
            account_account.code,
            account_move_line.date desc
        """

        return '%s (SELECT %s FROM %s WHERE %s ORDER BY %s)' % (with_, select_, from_, where_, order_)

    # @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
