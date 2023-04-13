# -*- coding: utf-8 -*- 

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pytz


class PosConfig(models.Model):
    _inherit = 'pos.config'

    last_session_closing_datetime = fields.Datetime(compute='_compute_last_session')

    @api.depends('session_ids')
    def _compute_last_session(self):
        #FIXME:Here we have not called the super method because the change must be inside ,should we do better than this?
        PosSession = self.env['pos.session']
        for pos_config in self:
            session = PosSession.search_read(
                [('config_id', '=', pos_config.id), ('state', '=', 'closed')],
                ['cash_register_balance_end_real', 'stop_at', 'cash_register_id'],
                order="stop_at desc", limit=1)
            if session:
                timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
                closing_date = session[0]['stop_at'].astimezone(timezone)
                pos_config.last_session_closing_datetime = closing_date.astimezone().replace(tzinfo=None)
                pos_config.last_session_closing_date = closing_date.date()
                if session[0]['cash_register_id']:
                    pos_config.last_session_closing_cash = session[0]['cash_register_balance_end_real']
                else:
                    pos_config.last_session_closing_cash = 0
            else:
                pos_config.last_session_closing_cash = 0
                pos_config.last_session_closing_date = False



