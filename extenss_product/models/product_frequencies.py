from odoo import fields, models

FREQ = [
    ('0', 'Quincenal'),
    ('1', 'Mensual'),
    ('2', 'Semanal'),
]

class ProductFrequencies(models.Model):
    _inherit = 'product.template'
    frequency = fields.Selection(FREQ, string='Frequency', index=True, default=FREQ[0][0])
    