##############################################################################
#
#    Copyright (C) 2017 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from odoo import api, models


class AccountStatementImport(models.TransientModel):
    _inherit = 'account.statement.import'

    @api.model
    def _complete_stmts_vals(self, stmts_vals, journal, account_number):
        """
        Use completion rules in journal to find missing partners.
        """
        stmts_vals = super()._complete_stmts_vals(
            stmts_vals, journal, account_number)
        if journal.completion_rules:
            for st_vals in stmts_vals:
                journal.completion_rules.auto_complete(st_vals)
        return stmts_vals
