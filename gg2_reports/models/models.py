# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

class TsaRpt050BankJouA(models.Model):
    _name = "gg2_reports.bankjou"
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
    # stmt_line_desc = fields.Char(string='StmtLineDesc', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    joudate = fields.Date(string='JouDate', readonly=True)

    @api.model
    def init(self):
        self._cr.execute("""CREATE OR REPLACE VIEW gg2_reports_bankjou AS (
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
            account_bank_statement_line.amount AS amount,
            account_move.date AS joudate
        FROM 
            ((account_move_line 
            INNER JOIN account_move ON account_move_line.move_id = account_move.id)
            INNER JOIN account_bank_statement_line ON account_move_line.statement_line_id = account_bank_statement_line.id)
            INNER JOIN account_bank_statement ON account_move_line.statement_id = account_bank_statement.id
        )""")

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
    _name = "gg2_reports.rpt080"
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
        sale_order_view_id = self.env.ref('gg2_reports.view_form_sale_order_tsa').id
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
    _name = "gg2_reports.rpt082"
    _description = "SOs Invoiced but not yet delivered"
    _auto = False

    sostate = fields.Char(readonly=True)
    soname = fields.Char(readonly=True)
    orderdate = fields.Datetime(readonly=True)
    whotoinvoice = fields.Char(readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            gg2_reports_rpt080.soid AS id,
            gg2_reports_rpt080.sostate AS sostate,
            gg2_reports_rpt080.soname AS soname,
            gg2_reports_rpt080.orderdate AS orderdate,
            gg2_reports_rpt080.whotoinvoice AS whotoinvoice
        """

        for field in fields.values():
            select_ += field

        from_ = """
            gg2_reports_rpt080
            %s
        """ % from_clause

        groupby_ = """
            gg2_reports_rpt080.soid,
            gg2_reports_rpt080.sostate,
            gg2_reports_rpt080.soname,
            gg2_reports_rpt080.orderdate,
            gg2_reports_rpt080.whotoinvoice
            %s
        """ % groupby

        order_ = """
            gg2_reports_rpt080.soid DESC
        """

        return '%s (SELECT %s FROM %s GROUP BY %s ORDER BY %s)' % (with_, select_, from_, groupby_, order_)

    # @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def showsalesorder(self):
        self.ensure_one()
        sale_order_view_id = self.env.ref('gg2_reports.view_form_sale_order_tsa').id
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
    _name = "gg2_reports.rpt090"
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
