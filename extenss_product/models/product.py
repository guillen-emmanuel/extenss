from odoo import api, fields, models, api, _
from odoo.exceptions import Warning, UserError, ValidationError 

class ProductProduct(models.Model):
    _inherit='product.product'

    cat_extra = fields.Float(
        'Variant Cat Extra', compute='_compute_product_cat_extra',
        help="This is the sum of the extra price of all attributes")
    interest_rate_extra = fields.Float(
        'Variant Cat Extra', compute='_compute_product_interest_rate_extra',
        help="This is the sum of the extra price of all attributes")
    term_extra = fields.Integer(
        'Variant Term Extra', compute='_compute_product_term_extra',
        help="This is the sum of the extra price of all attributes")
    frequency_extra = fields.Integer(
        'Variant Fequency Extra', compute='_compute_product_frequency_extra',
        help="This is the sum of the extra price of all attributes")
    def _compute_product_cat_extra(self):
        for product in self:
            product.cat_extra = sum(product.product_template_attribute_value_ids.mapped('cat_extra'))
    def _compute_product_interest_rate_extra(self):
        for product in self:
            product.interest_rate_extra = sum(product.product_template_attribute_value_ids.mapped('interest_rate_extra'))
    def _compute_product_term_extra(self):
        for product in self:
            product.term_extra = sum(product.product_template_attribute_value_ids.mapped('term_extra'))
    def _compute_product_frequency_extra(self):
        for product in self:
            product.frequency_extra = sum(product.product_template_attribute_value_ids.mapped('frequency_extra'))
   
   
    
