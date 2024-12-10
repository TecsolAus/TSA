# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
# from mock.mock import self

class tsaexte(models.Model):
    _inherit = ['hr.attendance']

    x_notes = fields.Text(string='Notes / Comments', help='Add notes and comments as required', copy=True, readonly=False, required=False, selectable=True)
