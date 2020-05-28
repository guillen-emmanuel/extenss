from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError, ValidationError 

CALC_TYPE = [
    ('0', 'Saldos Insolutos'),
]
CT = [
    ('Credito Simple'),
    ('Arrendamiento Financiero'),
    ('Arrendamiento Puro'),
]

class ExtenssProductCreditType(models.Model):
    _name = 'extenss.product.credit_type'
    _order = 'name'
    _description = 'Credit Type'

    name = fields.Char(string='Credit Type',  translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssProductCalculationBase(models.Model):
    _name = 'extenss.product.calculation_base'
    _orde = 'name'
    _description = 'Calculation Base'
    
    name = fields.Char(string='Calculation Base',  translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)
class ExtenssProductBaseInterestRate(models.Model):
    _name = 'extenss.product.base_interest_rate'
    _orde = 'name'
    _description = 'Base Interest Rate'
    
    name = fields.Char(string='Base Interest Rate',  translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)
    interest_rate_ids = fields.One2many('extenss.product.interest_rate_date','base_interest_rate_id',string=' ')

class ExtenssProductTypeDocs(models.Model):
    _name = 'extenss.product.type_docs'
    _order = 'name'
    _description = 'Type Documents'

    name = fields.Char(string='Document Name', translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)
    related_to = fields.Selection(string='Related to', selection=[('contact', 'Contact'), ('request', 'Request')], default='contact')
    
    _sql_constraints = [
        ('name_unique',
        'UNIQUE(name)',
        "The Document name must be unique"),
    ]

class ExtenssProductRecDocs(models.Model):
    _name = 'extenss.product.rec_docs'
    _order = 'name'
    _description = 'Recruitment Documents'

    name = fields.Char(string='Document Name', translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)
    
    _sql_constraints = [
        ('name_unique',
        'UNIQUE(name)',
        "The Document name must be unique"),
    ]

    @api.constrains('name')
    def _check_name_insensitive(self):
        model_ids = self.search([('id', '!=', self.id)])
        list_names = [x.name.upper() for x in model_ids if x.name]
        if self.name.upper() in list_names:
            raise Warning(
                "Ya existe un registro con el nombre: %s " % (self.name.upper())
            )

class ExtenssProductInterestRate(models.Model):
    _name = 'extenss.product.interest_rate'
    _description = 'multiples registros interest rate'

    @api.constrains('initial_term', 'final_term', 'cat', 'interest_rate_2')   
    def _check_intrat(self):
        for intrat in self: 
            if intrat.initial_term <= 0:
                raise ValidationError(_('The Internal Term must be greater than 0'))
            if intrat.final_term  <= 0:
                raise ValidationError(_('The Final Term at must be greater than 0'))
            if intrat.initial_term >= intrat.final_term:
                raise ValidationError(_('The Internal Term must be less than The Final Term'))
            if intrat.interest_rate_2  <= 0:
                raise ValidationError(_('The Interest Rate at must be greater than 0'))
            if intrat.cat  <= 0:
                raise ValidationError(_('The Cat at must be greater than 0'))

    interest_rate_id = fields.Many2one('product.template')
    initial_term = fields.Integer('Initial term',  translate=True, required=True,)
    final_term = fields.Integer('Final term',  translate=True, required=True,)
    interest_rate_2 = fields.Float('Interest Rate',  translate=True, required=True,)
    cat = fields.Float('Cat',  translate=True, required=True,)
    frequencies_ir = fields.Many2one('extenss.product.frequencies', string="Frequencies", required=True,)
class ExtenssFrequencies(models.Model):
    _name = "extenss.product.frequencies"
    _description = "Frequencies"

    name = fields.Char('Frequency', required=True)
    days = fields.Integer('Days', required=True)

class Product(models.Model):
    _inherit = 'product.template'

    @api.constrains('min_age', 'max_age', 'min_amount', 'max_amount')   
    def _check_fields(self):
        for product in self:
            if product.min_age <=0:
                raise ValidationError(_('The Min. Age must be greater than 0'))
            if product.max_age <=0:
                raise ValidationError(_('The Max. Age must be greater than 0'))
            if product.min_age >99:
                raise ValidationError(_('The Min. Age is not valid'))
            if product.max_age >99:
                raise ValidationError(_('The Max. Age is not valid'))
            if product.min_age >= product.max_age:
                raise ValidationError(_('The Min. Age must be less than The Max. Age'))
            if product.min_amount <= 0:
                raise ValidationError(_('The Min. Amount must be greater than 0'))
            if product.max_amount <= 0:
                raise ValidationError(_('The Max. Amount must be greater than 0'))
            if product.min_amount >= product.max_amount:
                raise ValidationError(_('The Min. Amount must be less than The Max. Amount'))

    @api.constrains('base_interest_rate')   
    def _check_bir(self):
        for product in self:
            if product.base_interest_rate.id != False and product.point_base_interest_rate == False:
                raise ValidationError(_('The Point Base Interest Rate at must be greater than '))

    credit_type = fields.Many2one('extenss.product.credit_type')
    calculation_base = fields.Many2one('extenss.product.calculation_base')
    base_interest_rate = fields.Many2one('extenss.product.base_interest_rate')
    point_base_interest_rate = fields.Float('P. of Base Interest Rate', (2,6), translate=True)
    include_taxes = fields.Boolean('Include Taxes', default=False,  translate=True)
    min_age = fields.Integer('Min. Age', translate=True)
    max_age = fields.Integer('Max. Age',  translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    min_amount = fields.Monetary('Min. Amount',  currency_field='company_currency', tracking=True)
    max_amount = fields.Monetary('Max. Amount',  currency_field='company_currency', tracking=True)
    apply_company = fields.Boolean('Apply Company', default=False,  translate=True)
    apply_person = fields.Boolean('Apply Person', default=False,  translate=True)
    endorsement = fields.Boolean('Requires Endorsement', default=False,  translate=True)
    obligated_solidary = fields.Boolean('Requires Obligated solidary', default=False,  translate=True)
    guarantee = fields.Boolean('Requires Warranty', default=False,  translate=True)
    socioeconomic_study = fields.Boolean('Socio-economic study', default=False,  translate=True)
    sic_consult = fields.Boolean('SIC Query', default=False,  translate=True)
    beneficiaries = fields.Boolean('Beneficiaries', default=False,  translate=True)
    patrimonial_relationship = fields.Boolean('Patrimonial Declaration', default=False,  translate=True)
    financial_situation = fields.Boolean('Business information', default=False,  translate=True)
    calculation_type = fields.Selection(CALC_TYPE, string='Calculation Type', index=True, default=CALC_TYPE[0][0])
    docs_ids = fields.One2many('extenss.product.cat_docs','doc_id',string=' ')
    rec_docs_ids = fields.One2many('extenss.product.recruitment_documents','product_id',string=' ')
    hide = fields.Boolean(string="Hide", default=True)

    @api.onchange('base_interest_rate')
    def base_interest_rate_change(self):
        if not self.base_interest_rate:
            return
        self.hide=False

class ExtenssProductInteresRateExtra(models.Model):
    _inherit ='product.template.attribute.value'
    
    @api.constrains('interest_rate_extra', 'cat_extra')   
    def _check_intcatextra(self):
        for intrat in self: 
            if intrat.interest_rate_extra <= 0:
                raise ValidationError(_('The Interest Rate must be greater than 0'))
            if intrat.cat_extra <= 0:
                raise ValidationError(_('The Cat must be greater than 0'))
            if intrat.term_extra <= 0:
                raise ValidationError(_('The Term must be greater than 0'))

    interest_rate_extra = fields.Float('Interest Rate',(2,6) ,translate=True,required=True)
    cat_extra = fields.Float('Cat',(2,6),translate=True, required=True)
    frequencies_extra = fields.Many2one('extenss.product.frequencies', string="Frequencies", translate=True, required=True)
    term_extra = fields.Integer('Term', translate=True, required=True)
    frequency_extra = fields.Integer('Frequency')

    @api.onchange('frequencies_extra')
    def frequencies_extra_change(self):
        if not self.frequencies_extra:
            return
        self.frequency_extra = self.frequencies_extra.id

class ExtenssProductCatDocs(models.Model):
    _name = 'extenss.product.cat_docs'
    _description = 'Documentos requeridos'

    doc_id = fields.Many2one('product.template')
    catalogo_docs = fields.Many2one('extenss.product.type_docs', string='Document name', translate=True)
    flag_activo = fields.Boolean(string='Required', default=False, translate=True)
    
    _sql_constraints = [
        ('name_unique',
        'UNIQUE(doc_id,catalogo_docs)',
        "The Document name must be unique"),
    ]

class ExtenssInterestRateDate(models.Model):
    _name = 'extenss.product.interest_rate_date'
    _description = 'Interest Rate Date'

    base_interest_rate_id = fields.Many2one('extenss.product.base_interest_rate')
    date = fields.Date('Date')
    interest_rate = fields.Float('Interest Rate',(2,6) ,translate=True)

    _sql_constraints = [
        ('name_unique',
        'UNIQUE(base_interest_rate_id,date)',
        "The Date must be unique"),
    ]

class ExtenssProductRecruitmentDocuments(models.Model):
    _name = 'extenss.product.recruitment_documents'
    _description = 'Recruitmen Documents'

    product_id = fields.Many2one('product.template')
    catalog_recru_docs = fields.Many2one('extenss.product.rec_docs', string='Document', translate=True)
    
    _sql_constraints = [
        ('name_unique',
        'UNIQUE(product_id,catalog_recru_docs)',
        "The Document name must be unique"),
    ]

