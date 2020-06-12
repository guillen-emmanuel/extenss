from odoo import fields, models, api, _, exceptions
from odoo.exceptions import Warning, UserError, ValidationError

CREDIT_STATUS = [
    ('pending', 'Pending'),
    ('active', 'Active'),
    ('finished', 'Finished'),
    ('liquidated', 'Liquidated'),
    ('cancelled', 'Cancelled'),
]

class Credits(models.Model):
    _name = 'extenss.credit'
    _description = 'Credit'

    credit_id = fields.Char('Credit', copy=False, readonly=True, index=True, tracking=True, translate=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True, translate=True)
    request_id = fields.Many2one('crm.lead', string='Request Id', tracking=True, translate=True)
    product_id = fields.Many2one('product.template', string='Product', tracking=True, translate=True)
    salesperson_id = fields.Many2one('res.users', string='Salesperson Id', tracking=True, translate=True)
    office_id = fields.Many2one('crm.team', string='Branch office Id', tracking=True, translate=True)
    anchor_id = fields.Char( string='Financial funding', tracking=True, translate=True)
    bill_id = fields.Many2one('extenss.credit.account', string='Bill', tracking=True, translate=True)
    customer_type = fields.Selection([('person','Individual'),('company','Company')], string='Customer type', tracking=True, translate=True)
    #customer_name = fields.Char(string='Customer', tracking=True, translate=True)
    amount_financed = fields.Monetary(string='Amount Financed', currency_field='company_currency', tracking=True, translate=True)
    term = fields.Integer(string='Term', tracking=True, translate=True)
    frequency = fields.Many2one('extenss.product.frequencies', string='Frequency', tracking=True, translate=True)
    vat_factor = fields.Float('VAT factor', (2,6), tracking=True, translate=True)
    rate_type = fields.Char(string='Rate type', tracking=True, translate=True)
    base_rate_type = fields.Char(string='Base rate type', tracking=True, translate=True)
    base_rate_value = fields.Float('Base rate value', (2,6), tracking=True, translate=True)
    differential = fields.Float('Differential', (2,6), tracking=True, translate=True)
    interest_rate = fields.Float('Interest rate', (2,6), tracking=True, translate=True)
    default_factors = fields.Float('Default factors', (2,6), tracking=True, translate=True)##preguntar el nombre en ingles
    days_notice = fields.Integer(string='Days to notice', tracking=True, translate=True)
    type_credit = fields.Many2one('extenss.product.credit_type', string='Type of Credit', tracking=True, translate=True)
    hiring_date = fields.Date(string='Hiring date', tracking=True, translate=True)
    first_payment_date = fields.Date(string='First payment date', tracking=True, translate=True)
    dispersion_date = fields.Date(string='Dispersion date', tracking=True, translate=True)
    last_payment_date = fields.Date(string='Last payment date', tracking=True, translate=True)
    purchase_option = fields.Float('% Purchase option', (2,6), tracking=True, translate=True)
    purchase_option_amount = fields.Monetary(string='Purchase option amount', currency_field='company_currency', tracking=True, translate=True)
    residual_value = fields.Float('% Residual value', (2,6), tracking=True, translate=True)
    amount_residual_value = fields.Monetary(string='Amount of Residual Value', currency_field='company_currency', tracking=True, translate=True)
    total_paid = fields.Monetary(string='Total Paid', currency_field='company_currency', tracking=True, translate=True)
    outstanding_balance = fields.Monetary(string='Outstanding balance', currency_field='company_currency', tracking=True, translate=True)
    past_due_interest = fields.Monetary(string='Past due interest', currency_field='company_currency', tracking=True, translate=True)
    overdue_capital = fields.Monetary(string='Overdue capital', currency_field='company_currency', tracking=True, translate=True)
    expired_capital_vat = fields.Monetary(string='Expired capital VAT', currency_field='company_currency', tracking=True, translate=True)
    expired_interest_vat = fields.Monetary(string='Expired interest VAT', currency_field='company_currency', tracking=True, translate=True)
    overdue_balance = fields.Monetary(string='Overdue balance', currency_field='company_currency', tracking=True, translate=True)
    deposit_income = fields.Monetary(string='Deposit income', currency_field='company_currency', tracking=True, translate=True)
    income_tax_deposit = fields.Monetary(string='Income Tax on deposit', currency_field='company_currency', tracking=True, translate=True)
    total_deposit_income = fields.Monetary(string='Total deposit income', currency_field='company_currency', tracking=True, translate=True)
    percentage_guarantee_deposit = fields.Float('% Guarantee deposit', (2,6), tracking=True, translate=True)
    guarantee_deposit = fields.Monetary(string='Guarantee deposit', currency_field='company_currency', tracking=True, translate=True)
    vat_guarantee_deposit = fields.Monetary(string='VAT guarantee deposit', currency_field='company_currency', tracking=True, translate=True)
    total_guarantee_deposit = fields.Monetary(string='Total guarantee deposit', currency_field='company_currency', tracking=True, translate=True)
    dep_income_application = fields.Monetary(string='Deposit Income Application', currency_field='company_currency', tracking=True, translate=True)
    guarantee_dep_application = fields.Monetary(string='Guarantee Deposit Application', currency_field='company_currency', tracking=True, translate=True)
    balance_income_deposit = fields.Monetary(string='Balance of Income on deposit', currency_field='company_currency', tracking=True, translate=True)
    guarantee_dep_balance = fields.Monetary(string='Guarantee Deposit Balance', currency_field='company_currency', tracking=True, translate=True)
    days_transfer_past_due = fields.Integer(string='Days to transfer to past due portfolio', tracking=True, translate=True)
    number_days_overdue = fields.Integer(string='Number of days overdue', tracking=True, translate=True)
    portfolio_type = fields.Selection([('vigente','Valid'),('vencida','Expired')], string='Portfolio Type', tracking=True, translate=True)
    credit_status = fields.Selection(CREDIT_STATUS, string='Credit status', tracking=True, translate=True)
    percentage_commission = fields.Float('% Commission', (2,6), tracking=True, translate=True)
    commission_amount = fields.Monetary(string='Commission amount', currency_field='company_currency', tracking=True, translate=True)
    commission_vat = fields.Monetary(string='Commission VAT', currency_field='company_currency', tracking=True, translate=True)
    total_commission = fields.Monetary(string='Total commission', currency_field='company_currency', tracking=True, translate=True)
    ratification = fields.Monetary(string='Ratification', currency_field='company_currency', tracking=True, translate=True)
    ratification_vat = fields.Monetary(string='Ratification VAT', currency_field='company_currency', tracking=True, translate=True)
    total_ratification = fields.Monetary(string='Total Ratification', currency_field='company_currency', tracking=True, translate=True)
    initial_total_payment = fields.Monetary(string='Initial total payment', currency_field='company_currency', tracking=True, translate=True)
    order_id = fields.Integer(String='Order')
    account_status_date = fields.Date(string=u'Account Status Date',
    default=fields.Date.context_today)
    cs = fields.Boolean(String='CS')
    af = fields.Boolean(String='AF')
    ap = fields.Boolean(String='AP')
    amortization_ids = fields.One2many(
        'extenss.credit.amortization', 
        'credit_id', 
        string='Amortization Table')
    leased_team = fields.Char('Leased Team')
    amount_si = fields.Monetary('Amount s/iva', currency_field='company_currency', tracking=True)
    tax_amount = fields.Monetary('Tax Amount', currency_field='company_currency', tracking=True)
    date_limit_pay = fields.Date('Limit Date')
    
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    @api.model
    def create(self, reg):
        if reg:
            if reg.get('credit_id', _('New')) == _('New'):
                reg['credit_id'] = self.env['ir.sequence'].next_by_code('extenss.credit') or _('New')
            result = super(Credits, self).create(reg)
            return result

    credit_expiry_ids = fields.One2many('extenss.credit.expiry_notices', 'credit_expiry_id', string=' ', tracking=True)

class ExtenssCreditExpiryNotices(models.Model):
    _name = 'extenss.credit.expiry_notices'
    _description = 'Expiry Notices'

    credit_expiry_id = fields.Many2one('extenss.credit', tracking=True, translate=True)
    payment_number = fields.Integer(string='Payment number', tracking=True, translate=True)
    expiry_not_number = fields.Integer(string='Expiry notice number', tracking=True, translate=True)
    due_not_date = fields.Date(string='Due notice date', tracking=True, translate=True)
    amount_not = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    total_paid_not = fields.Monetary(string='Total paid', currency_field='company_currency', tracking=True, translate=True)
    total_to_pay = fields.Monetary(string='Total to pay', currency_field='company_currency', tracking=True, translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    expiry_notice_ids = fields.One2many('extenss.credit.concepts_expiration', 'expiry_notice_id', string=' ', tracking=True)

class ExtenssCreditConceptsExpiration(models.Model):
    _name = 'extenss.credit.concepts_expiration'
    _description = 'Concepts Expiration Notices'

    expiry_notice_id = fields.Many2one('extenss.credit.expiry_notice', tracking=True, translate=True)
    name = fields.Char(string='Concept', tracking=True, translate=True)
    expiry_not_number_concept = fields.Integer(string='Expiry Notice Number', tracking=True, translate=True)
    amount_concept = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    concept = fields.Char(string='Concept', tracking=True, translate=True)
    total_paid_concept = fields.Monetary(string='Total paid', currency_field='company_currency', tracking=True, translate=True)
    full_paid = fields.Monetary(string='Full payment', currency_field='company_currency', tracking=True, translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    concept_pay_ids = fields.One2many('extenss.credit.concept_payments', 'concept_pay_id', string=' ', tracking=True)

class ExtenssCreditConceptPayments(models.Model):
    _name = 'extenss.credit.concept_payments'
    _description = 'Concept Payments'

    concept_pay_id = fields.Many2one('extenss.credit.concepts_expiration', tracking=True, translate=True)
    pay_id = fields.Char(string='Pay', tracking=True, translate=True)
    expiry_not_number_cp = fields.Integer(string='Expiry notice number', tracking=True, translate=True)
    concept_id_cp = fields.Char(string='Concept', tracking=True, translate=True)
    date_paid = fields.Date(string='Payment date', tracking=True, translate=True)
    total_paid_cp = fields.Monetary(string='Total paid', currency_field='company_currency', tracking=True, translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class ExtenssCreditAccount(models.Model):
    _name = 'extenss.credit.account'
    _description = 'Account'

    name = fields.Char(string='Account', copy=False, readonly=True, index=True, tracking=True, translate=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True, translate=True)
    date_opening = fields.Date(string='Account opening date', tracking=True, translate=True)
    status = fields.Selection([('active','Active'),('inactive','Inactive')], string='Status', tracking=True, translate=True) 
    balance = fields.Monetary(string='Balance', currency_field='company_currency', tracking=True, translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    @api.model
    def create(self, reg):
        if reg:
            if reg.get('account_id', _('New')) == _('New'):
                reg['name'] = self.env['ir.sequence'].next_by_code('extenss.credit.account') or _('New')
            result = super(ExtenssCreditAccount, self).create(reg)
            return result
    accnt_mov_ids = fields.One2many('extenss.credit.movements', 'accnt_mov_id', string=' ', tracking=True)
class ExtenssCreditMovements(models.Model):
    _name = 'extenss.credit.movements'
    _description = 'Account Movements'

    accnt_mov_id = fields.Many2one('extenss.credit.account', string='Account', tracking=True, translate=True)
    date_time_move = fields.Datetime(string='Movement date and time', tracking=True, translate=True)
    movement_type = fields.Selection([('cargo','Charge'),('abono','Payment')], string='Movement type', tracking=True, translate=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    initial_balance = fields.Monetary(string='Initial balance', currency_field='company_currency', tracking=True, translate=True)
    ending_balance = fields.Monetary(string='Ending balance', currency_field='company_currency', tracking=True, translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class CreditsAmortizationCS(models.Model):
    _name = 'extenss.credit.amortization'
    credit_id = fields.Many2one('extenss.credit')
    no_pay = fields.Integer('No Pay')
    expiration_date = fields.Date('Expiration Date')
    initial_balance = fields.Monetary('Initial Balance',currency_field='company_currency', tracking=True)
    capital = fields.Monetary('Capital',currency_field='company_currency', tracking=True)
    interest = fields.Monetary('Interest', currency_field='company_currency', tracking=True)
    iva_interest = fields.Monetary('IVA Interest',currency_field='company_currency', tracking=True)
    payment = fields.Monetary('Payment',currency_field='company_currency', tracking=True)
    iva_capital = fields.Monetary('IVA Capital',currency_field='company_currency', tracking=True)
    total_rent = fields.Monetary('Total Rent',currency_field='company_currency', tracking=True)
    iva_rent = fields.Monetary('IVA Rent',currency_field='company_currency', tracking=True)
    cs = fields.Boolean('CS')

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)