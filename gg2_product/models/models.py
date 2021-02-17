# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

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
