# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    # _name = 'account.move'
    _inherit = 'account.move'

    @api.onchange('date')
    def _onchange_date(self):
        '''On the form view, a change on the date will trigger onchange() on account.move
        but not on account.move.line even the date field is related to account.move.
        Then, trigger the _onchange_amount_currency manually.
        '''
        self.line_ids._onchange_amount_currency()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('amount_currency', 'currency_id', 'account_id')
    def _onchange_amount_currency(self):
        '''Recompute the debit/credit based on amount_currency/currency_id and date.
        However, date is a related field on account.move. Then, this onchange will not be triggered
        by the form view by changing the date on the account.move.
        To fix this problem, see _onchange_date method on account.move.
        '''
        for line in self:
            company_currency_id = line.account_id.company_id.currency_id
            amount = line.amount_currency
            if line.currency_id and company_currency_id and line.currency_id != company_currency_id:
                amount = line.currency_id._convert(amount, company_currency_id, line.company_id or line.account_id.company_id, line.date or fields.Date.today())
                line.debit = amount > 0 and amount or 0.0
                line.credit = amount < 0 and -amount or 0.0