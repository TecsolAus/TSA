# -*- coding: utf-8 -*-
from typing import Any, Union

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import pdb
from mock.mock import self

class tsaextf(models.Model):
    _inherit = ['mrp.bom.line']

    x_designator = fields.Char(string='Designator', help='', copy=True, readonly=False, required=False, selectable=True)
    x_footprint = fields.Char(string='Footprint', help='', copy=True, readonly=False, required=False, selectable=True)
