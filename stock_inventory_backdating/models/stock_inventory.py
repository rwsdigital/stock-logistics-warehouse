# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class StockInventory(models.Model):
	_inherit = 'stock.inventory'

	date = fields.Datetime('Inventory Date', readonly=False, required=True, default=fields.Datetime.now,
		help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
		"If the inventory adjustment is validated, date at which the inventory adjustment has been validated.")

	def action_start(self):
		for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
			vals = {'state': 'confirm'}
			if (inventory.filter != 'partial') and not inventory.line_ids:
				vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
				inventory.write(vals)
		return True

	def post_inventory(self):
		# The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
		# as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
		# as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
		moves_todo = self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()
		moves_todo.write({'date': self.date, 'date_expected': self.date})
		moves_todo.mapped('move_line_ids').write({'date': self.date})
