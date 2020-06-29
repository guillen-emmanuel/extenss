from odoo import fields, models, api, _, exceptions
from odoo.exceptions import Warning, UserError, ValidationError

from datetime import timedelta
from datetime import datetime, date

CREDIT_STATUS = [
    ('pending', 'Pending'),
    ('active', 'Active'),
    ('finished', 'Finished'),
    ('liquidated', 'Liquidated'),
    ('cancelled', 'Cancelled'),
]

CONCEPTS = [
    ('capital','Capital'),
    ('interest','Interest'),
    ('capvat','Capital VAT'),
    ('intvat','Interest VAT'),
    ('penalty_amount', 'Penalty Amount'),
    ('purchase_option', 'Purchase Option'),
    ('vat_option','Purchase Option VAT'),
    ('morint', 'Moratorium Interest'),
    ('morintvat', 'Moratorium Interest VAT'),
    ('payment', 'Payment'),
    ('paymentvat', 'VAT Payment'),
]

class Credits(models.Model):
    _name = 'extenss.credit'
    _description = 'Credit'

    def open_request_count(self):
        domain = [('credit_request_id', '=', [self.id])]
        return {
            'name': _('Request'),
            'view_type': 'form',
            'domain': domain,
            'res_model': 'extenss.credit.request',
            'type': 'ir.actions.act_window',
            #'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'tree,form',
            'context': "{'default_credit_request_id': %s}" % self.id
        }

    def get_request_count(self):
        count = self.env['extenss.credit.request'].search_count([('credit_request_id', '=', self.id)])
        self.request_count = count
    
    def action_new_request(self):
        action = self.env.ref("extenss_credit.action_menu_request").read()[0]
        action['context'] = {
            'default_credit_request_id': self.id,
        }
        return action
    
    name = fields.Char('Credit', related='credit_id')
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
    rate_arrears_interest = fields.Float('Factor', (2,1), tracking=True)
    factor_rate = fields.Float('Rate interest moratorium', (2,6), tracking=True)
    #default_factors = fields.Float('Default factors', (2,6), tracking=True, translate=True)##preguntar el nombre en ingles
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
    calculation_base = fields.Char('Calculation Base')
    request_count = fields.Integer(string='Request', compute='get_request_count', tracking=True)
    flag_early_settlement = fields.Boolean(string='Early settlement', default=False, tracking=True, translate=True)
    moras_ids = fields.One2many(
        'extenss.credit.moras', 
        'credit_id', 
        string='Moras Table')
    notice_date = fields.Date(string=u'Expiri Notices',
    default=fields.Date.context_today)

    payment_date = fields.Date(string=u'Register Payment',
    default=fields.Date.context_today)
    
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    @api.model
    def create(self, reg):
        if reg:
            if reg.get('credit_id', _('New')) == _('New'):
                reg['credit_id'] = self.env['ir.sequence'].next_by_code('extenss.credit') or _('New')
            result = super(Credits, self).create(reg)
            return result

    def check_credits(self):
        rec_en = self.env['extenss.credit.expiry_notices']
        rec_cp = self.env['extenss.credit.concepts_expiration']

        

        credit_rec = self.env['extenss.credit'].search([('credit_status', '=', 'active'),('flag_early_settlement', '=', False)])
        for reg in credit_rec:
            now =  reg.notice_date
            new_date = now + timedelta(days=1)
            records_amortization = self.env['extenss.credit.amortization'].search([('credit_id', '=', reg.id),('expiration_date', '=', new_date)])
            for rec in records_amortization:
                if reg.cs == False :
                    amount = rec.total_rent
                else:
                    amount = rec.payment

                rec_en.create({
                    'credit_expiry_id': reg.id,
                    'payment_number': rec.no_pay,
                    'due_not_date': rec.expiration_date,
                    'amount_not': amount,
                    'total_paid_not': 0,
                    'total_to_pay': 0,
                })

                rec_notice = self.env['extenss.credit.expiry_notices'].search([('payment_number', '=', rec.no_pay),('credit_expiry_id', '=', reg.id),('req_credit_id', '=', False)])
                for r in rec_notice:
                    if reg.af or reg.cs:
                        rec_cp.create({
                            'expiry_notice_id': r.id,
                            'concept': 'capital',
                            'amount_concept': rec.capital,
                            'total_paid_concept': 0,
                            'full_paid': 0,
                        })
                        rec_cp.create({
                            'expiry_notice_id': r.id,
                            'concept': 'interest',
                            'amount_concept': rec.interest,
                            'total_paid_concept': 0,
                            'full_paid': 0,
                        })
                        rec_cp.create({
                            'expiry_notice_id':r.id,
                            'concept': 'intvat',
                            'amount_concept': rec.iva_interest,
                            'total_paid_concept': 0,
                            'full_paid': 0,
                        })
                    if reg.af:
                        rec_cp.create({
                            'expiry_notice_id': r.id,
                            'concept': 'capvat',
                            'amount_concept': rec.iva_capital,
                            'total_paid_concept': 0,
                            'full_paid': 0,
                        })
                    if reg.ap:
                        rec_cp.create({
                            'expiry_notice_id': r.id,
                            'concept': 'payment',
                            'amount_concept': rec.payment,
                            'total_paid_concept': 0,
                            'full_paid': 0,
                        })
                        rec_cp.create({
                            'expiry_notice_id': r.id,
                            'concept': 'paymentvat',
                            'amount_concept': rec.iva_rent,
                            'total_paid_concept': 0,
                            'full_paid': 0,
                        })

    credit_expiry_ids = fields.One2many('extenss.credit.expiry_notices', 'credit_expiry_id', string=' ', tracking=True)     

    def register_payment(self):

        credit_rec = self.env['extenss.credit'].search([('credit_status', '=', 'active')])
        for cred in credit_rec:
            date_payment = cred.payment_date
            not_rec = self.env['extenss.credit.expiry_notices'].search([('due_not_date','<=',date_payment),('req_credit_id', '!=', False),('credit_expiry_id.id','=',cred.id)])
            amount=0
            for reg in not_rec:
                if reg.total_to_pay>0:
                    records_account = self.env['extenss.credit.account'].search([('customer_id', '=', reg.credit_expiry_id.customer_id.id)])
                    for act in records_account:
                        req=self.env['extenss.credit.request'].search([('id', '=', reg.req_credit_id),('type_request','=','early_settlement')])
                        if req.state == 'pending':
                            ex_no=self.env['extenss.credit.expiry_notices'].search([('credit_expiry_id.id','=',req.credit_request_id.id),('total_to_pay','>',0)])
                            over_balance=req.total_settle-req.overdue_balance
                            for exno in ex_no:
                                if exno.req_credit_id == False:
                                    over_balance=over_balance+exno.total_to_pay
                            over_balance=round(over_balance,2)
                            if act.balance>=over_balance:
                                req.write({
                                'state': 'applied'
                                })
                                reg.write({
                                'payment_date': date_payment
                                })
                                concepts_expiration = self.env['extenss.credit.concepts_expiration'].search([('expiry_notice_id','=',reg.id)])
                                for conexp in concepts_expiration :
                                    conexp.write({
                                    'total_paid_concept': round(conexp.amount_concept,2)
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(conexp.amount_concept,2))
                                    })
                                    amount=round(conexp.amount_concept,2)
                                    self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                                ex_no=self.env['extenss.credit.expiry_notices'].search([('credit_expiry_id.id','=',req.credit_request_id.id),('req_credit_id', '=', False)])
                                for exno in ex_no:
                                    concepts_expiration = self.env['extenss.credit.concepts_expiration'].search([('expiry_notice_id.id','=',exno.id)])
                                    for conexp in concepts_expiration :
                                        if conexp.full_paid == False:
                                            amount=round((conexp.amount_concept-conexp.total_paid_concept),2)
                                            conexp.write({
                                            'total_paid_concept': round(conexp.amount_concept,2)
                                            })
                                            conpay = self.env['extenss.credit.concept_payments']
                                            conpay.create({
                                            'concept_pay_id': conexp.id,
                                            'concept_id': exno.id,
                                            'date_paid': date_payment,
                                            'total_paid_cp': (round(amount,2))
                                            })
                                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                            else:
                                req.write({
                                'state': 'cancelled'
                                })
                                credit=self.env['extenss.credit'].search([('id','=',req.credit_request_id.id)])
                                credit.write({
                                'flag_early_settlement': False
                                })

            not_rec = self.env['extenss.credit.expiry_notices'].search([('due_not_date','<=',date_payment),('total_to_pay', '>', '0'),('req_credit_id', '=', False),('credit_expiry_id.id','=',cred.id)])
            for reg in not_rec:
                records_account = self.env['extenss.credit.account'].search([('customer_id', '=', reg.credit_expiry_id.customer_id.id)])
                for act in records_account:
                    calculation_base = self.env['extenss.credit'].search([('credit_expiry_ids.id','=',reg.id)]).calculation_base
                    cs = self.env['extenss.credit'].search([('credit_expiry_ids.id','=',reg.id)]).cs
                    ap = self.env['extenss.credit'].search([('credit_expiry_ids.id','=',reg.id)]).ap
                    vatf = self.env['extenss.credit'].search([('credit_expiry_ids.id','=',reg.id)]).vat_factor
                    int_rate = self.env['extenss.credit'].search([('credit_expiry_ids.id','=',reg.id)]).factor_rate
                    if calculation_base == '360/360' or calculation_base == '360/365' :
                        base=360
                    else:
                        base=365
                    concepts_expiration = self.env['extenss.credit.concepts_expiration']
                    exist_rec_mor = concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','morint')])
                    capital_pay =concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','capital')]).total_paid_concept
                    capital_ven =concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','capital')]).amount_concept
                    int_pay=concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','interest')]).full_paid

                    if ap == True :
                        capital_pay =concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','payment')]).total_paid_concept
                        capital_ven =concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','payment')]).amount_concept
                    capital_ven=capital_ven-capital_pay
                    int_mor=capital_ven * (int_rate/base/100)
                    if act.balance>0:
                        if not reg.payment_date:
                            dias_atr=(date_payment - reg.due_not_date).days
                        else:
                            dias_atr=(date_payment - reg.payment_date).days
                        if date_payment > reg.due_not_date and dias_atr>0 and reg.total_to_pay>0:
                            int_mor=round(int_mor*dias_atr,2)
                            amount_n=0
                            moras_table = self.env['extenss.credit.moras']
                            if not exist_rec_mor :
                                concepts_expiration.create({
                                'expiry_notice_id': reg.id,
                                'concept': 'morint',
                                'amount_concept': int_mor,
                                'total_paid_concept': 0,
                                'full_paid': 0,
                                })
                                amount_n=round(int_mor,2)
                                concepts_expiration.create({
                                'expiry_notice_id': reg.id,
                                'concept': 'morintvat',
                                'amount_concept':(round(int_mor * (vatf/100),2)),
                                'total_paid_concept': 0,
                                'full_paid': 0,
                                })
                                amount_n=amount_n+round(int_mor * (vatf/100),2)

                                moras_table.create({
                                    'credit_id': reg.credit_expiry_id.id,
                                    'init_date': reg.due_not_date,
                                    'end_date': date_payment,
                                    'days': (date_payment - reg.due_not_date).days,
                                    'past_due_balance': capital_ven,
                                    'rate':(int_rate/base/100),
                                    'interest':amount_n,
                                    'amount_to_payment':reg.amount_not+amount_n
                                })
                            else:
                                exist_rec_mor.write({
                                'amount_concept':(round(exist_rec_mor.amount_concept+int_mor,2)),
                                'full_paid': 0,
                                })
                                amount_n=round(int_mor,2)
                                exist_rec_morvat = concepts_expiration.search([('expiry_notice_id','=',reg.id),('concept','=','morintvat')])
                                exist_rec_morvat.write({
                                'amount_concept':(round(exist_rec_mor.amount_concept * (vatf/100),2)),
                                'full_paid': 0,
                                })
                                amount_n=amount_n+round(int_mor * (vatf/100),2)
                                moras_table=moras_table.search([('credit_id','=',reg.credit_expiry_id.id),('init_date','=',reg.due_not_date)])
                                moras_table.write({
                                    'end_date':date_payment,
                                    'days': (date_payment - reg.due_not_date ).days,
                                    'past_due_balance': capital_ven,
                                    'rate':(int_rate/base/100),
                                    'interest':moras_table.interest+amount_n,
                                    'amount_to_payment':reg.amount_not+amount_n
                                })
                            reg.write({
                                'amount_not':reg.amount_not+amount_n
                            })

                        concepts_expiration = self.env['extenss.credit.concepts_expiration'].search([('expiry_notice_id','=',reg.id)])
                        interest,intpay,intvat,intvatpay,capital,capay,capvat,capvatpay,morint,morintpay,morintvat,morintvatpay,payment,paypay,payvat,payvatpay,balance=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,act.balance
                        fpint,fpcap,fpmorint,fppay,fppayvat=True,True,True,True,True
                        for conexp in concepts_expiration :
                            if conexp.concept == 'morint' :
                                morint=conexp.amount_concept 
                                fpmorint=conexp.full_paid
                                morintpay=conexp.total_paid_concept
                            if conexp.concept == 'morintvat' :
                                morintvat=conexp.amount_concept 
                                morintvatpay=conexp.total_paid_concept
                            if conexp.concept == 'interest' :
                                interest=conexp.amount_concept 
                                fpint=conexp.full_paid
                                intpay=conexp.total_paid_concept
                            if conexp.concept == 'intvat' :
                                intvat=conexp.amount_concept 
                                intvatpay=conexp.total_paid_concept
                            if conexp.concept == 'capital' :
                                capital=conexp.amount_concept
                                fpcap=conexp.full_paid
                                capay=conexp.total_paid_concept
                            if conexp.concept == 'capvat' :
                                capvat=conexp.amount_concept
                                capvatpay=conexp.total_paid_concept
                            if conexp.concept == 'payment' :
                                payment=conexp.amount_concept
                                fppay=conexp.full_paid
                                paypay=conexp.total_paid_concept
                            if conexp.concept == 'paymentvat' :
                                payvat=conexp.amount_concept
                                fppayvat=conexp.full_paid
                                payvatpay=conexp.total_paid_concept
                        if balance >= ((morint+morintvat)-(morintpay+morintvatpay)) and fpmorint == False:
                            fpmorint=True
                            balance=balance-((morint+morintvat)-(morintpay+morintvatpay))
                            reg.write({
                            'payment_date': date_payment
                            })
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'morint' :
                                    conexp.write({
                                    'total_paid_concept': round(conexp.amount_concept,2)
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((conexp.amount_concept - morintpay),2))
                                    })
                                    amount=round((conexp.amount_concept - morintpay),2)
                                if conexp.concept == 'morintvat' :
                                    conexp.write({
                                    'total_paid_concept':(round(conexp.amount_concept,2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((conexp.amount_concept - morintvatpay),2))
                                    })
                                    amount=amount+round((conexp.amount_concept - morintvatpay),2)
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                        elif balance>0 and fpmorint == False :
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'morint' :
                                    conexp.write({
                                    'total_paid_concept': (round((balance/(1+(vatf/100)) + morintpay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(balance/(1+(vatf/100)),2))
                                    })
                                    amount=(round(balance/(1+(vatf/100)),2))
                                if conexp.concept == 'morintvat' :
                                    conexp.write({
                                    'total_paid_concept': (round((((balance/(1+(vatf/100)))*(vatf/100)) + morintvatpay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(((balance/(1+(vatf/100)))*(vatf/100)),2))
                                    })
                                    amount=amount+round(((balance/(1+(vatf/100)))*(vatf/100)),2)
                            balance=0
                            reg.write({
                            'payment_date': date_payment
                            })
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                        if balance > 0 and payvat>0 and  fpmorint == True and fppayvat==False:
                            if balance>= (payvat-payvatpay):
                                balance=balance-(payvat-payvatpay)
                                total_paid_concept=(payvat-payvatpay)
                            else:
                                total_paid_concept=balance
                                balance=0
                            if payvat == (total_paid_concept+payvatpay) :
                                fppayvat=True
                            reg.write({
                            'payment_date': date_payment
                            })
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'paymentvat' :
                                    conexp.write({
                                    'total_paid_concept': (round((total_paid_concept+payvatpay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(total_paid_concept,2))
                                    })
                                    amount=round(total_paid_concept,2)
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                        if balance > 0 and payment>0 and fppayvat==True and  fpmorint == True and fppay==False:
                            if balance>= (payment-paypay):
                                balance=balance-(payment-paypay)
                                total_paid_concept=(payment-paypay)
                            else:
                                total_paid_concept=balance
                                balance=0
                            reg.write({
                            'payment_date': date_payment
                            })
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'payment' :
                                    conexp.write({
                                    'total_paid_concept': (round((total_paid_concept+paypay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(total_paid_concept,2))
                                    })
                                    amount=round(total_paid_concept,2)
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                        if balance >= ((interest+intvat)-(intpay+intvatpay)) and interest>0 and fpmorint == True and fpint == False:
                            fpint=True
                            balance=balance-((interest+intvat)-(intpay+intvatpay))
                            reg.write({
                            'payment_date': date_payment
                            })
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'interest' :
                                    conexp.write({
                                    'total_paid_concept': (round(conexp.amount_concept,2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((conexp.amount_concept - intpay),2))
                                    })
                                    amount=round((conexp.amount_concept - intpay),2)
                                if conexp.concept == 'intvat' :
                                    conexp.write({
                                    'total_paid_concept': (round(conexp.amount_concept,2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({ 
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((conexp.amount_concept - intvatpay),2))
                                    })
                                    amount=amount+round((conexp.amount_concept - intvatpay),2)
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                        elif balance>0 and interest>0 and fpmorint == True and fpint == False:
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'interest' :
                                    conexp.write({
                                    'total_paid_concept': (round(((balance/(1+(vatf/100))) + intpay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(balance/(1+(vatf/100)),2))
                                    })
                                    amount=(round(balance/(1+(vatf/100)),2))
                                if conexp.concept == 'intvat' :
                                    conexp.write({
                                    'total_paid_concept': (round((((balance/(1+(vatf/100))))*(vatf/100) + intvatpay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round(((balance/(1+(vatf/100)))*(vatf/100)),2))
                                    })
                                    amount=amount+round(((balance/(1+(vatf/100)))*(vatf/100)),2)
                            balance=0
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                            reg.write({
                            'payment_date': date_payment
                            })
                        if balance >= ((capital+capvat)-(capay+capvatpay)) and fpint== True and fpcap == False :
                            balance=balance-((capital+capvat)-(capay+capvatpay))
                            reg.write({
                            'payment_date': date_payment
                            })
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'capital' :
                                    conexp.write({
                                    'total_paid_concept': (round(conexp.amount_concept,2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((conexp.amount_concept - capay),2))
                                    })
                                    amount=round((conexp.amount_concept - capay),2)
                                if conexp.concept == 'capvat' :
                                    conexp.write({
                                    'total_paid_concept': (round(conexp.amount_concept,2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((conexp.amount_concept - capvatpay),2))
                                    })
                                    amount=amount+round((conexp.amount_concept - capvatpay),2)
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                        elif balance>0 and fpint == True and fpcap == False:
                            total_paid_concept=balance + capay
                            amount=0
                            for conexp in concepts_expiration :
                                if conexp.concept == 'capital' :
                                    if cs == False:
                                        total_paid_concept = ((balance/(1+(vatf/100))) + capay)
                                    conexp.write({
                                    'total_paid_concept': (round(total_paid_concept,2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp': (round((total_paid_concept - capay),2))
                                    })
                                    amount=round((total_paid_concept - capay),2)
                                if conexp.concept == 'capvat' :
                                    conexp.write({
                                    'total_paid_concept': (round((((balance/(1+(vatf/100))))*(vatf/100) + capvatpay),2))
                                    })
                                    conpay = self.env['extenss.credit.concept_payments']
                                    conpay.create({
                                    'concept_pay_id': conexp.id,
                                    'concept_id': reg.id,
                                    'date_paid': date_payment,
                                    'total_paid_cp':(round(((balance/(1+(vatf/100)))*(vatf/100)),2))
                                    })
                                    amount=amount+round(((balance/(1+(vatf/100)))*(vatf/100)),2)
                            balance=0
                            self.env['extenss.credit.accounting_payments'].action_apply_movement(act.id, 'cargo', round(amount,2),'')
                            reg.write({
                            'payment_date': date_payment
                            })

class ExtenssCreditExpiryNotices(models.Model):
    _name = 'extenss.credit.expiry_notices'
    _description = 'Expiry Notices'

    credit_expiry_id = fields.Many2one('extenss.credit', tracking=True, translate=True)
    payment_number = fields.Integer(string='Payment number', tracking=True, translate=True)
    expiry_number = fields.Char(string='Expiry notice number', copy=False, readonly=True, index=True, tracking=True, translate=True, default=lambda self: _('New'))
    due_not_date = fields.Date(string='Due notice date', tracking=True, translate=True)
    amount_not = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    total_paid_not = fields.Monetary(string='Total paid', compute='_compute_total_paid_not', store=True, currency_field='company_currency', tracking=True, translate=True)
    total_to_pay = fields.Monetary(string='Total to pay', currency_field='company_currency', compute='_compute_total_to_pay', tracking=True, translate=True)
    payment_date = fields.Date(string='Payment date', tracking=True, translate=True)
    req_credit_id = fields.Char(string='Id Request')

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    @api.model
    def create(self, reg):
        if reg:
            if reg.get('expiry_number', _('New')) == _('New'):
                reg['expiry_number'] = self.env['ir.sequence'].next_by_code('extenss.credit.expiry_notices') or _('New')
            result = super(ExtenssCreditExpiryNotices, self).create(reg)
            return result

    @api.depends('amount_not','total_paid_not')
    def _compute_total_to_pay(self):
        for reg in self:
            reg.total_to_pay = reg.amount_not - reg.total_paid_not
            if reg.total_to_pay < 0 or reg.total_to_pay < .06 :
                reg.total_to_pay = 0


    @api.depends('expiry_notice_ids','expiry_notice_ids.total_paid_concept')
    def _compute_total_paid_not(self):
        for reg in self:
            reg.total_paid_not = sum([line.total_paid_concept for line in reg.expiry_notice_ids])

    expiry_notice_ids = fields.One2many('extenss.credit.concepts_expiration', 'expiry_notice_id', string=' ', tracking=True)

class ExtenssCreditConceptsExpiration(models.Model):
    _name = 'extenss.credit.concepts_expiration'
    _description = 'Concepts Expiration Notices'

    expiry_notice_id = fields.Many2one('extenss.credit.expiry_notices', tracking=True, translate=True)
    concept = fields.Selection(CONCEPTS, string='Concept', tracking=True, group_operator=True, translate=True)
    #expiry_num = fields.Char(string='Expiry Notice Number', copy=False, readonly=True, index=True, tracking=True, translate=True, default=lambda self: _('New'))
    amount_concept = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    total_paid_concept = fields.Monetary(string='Total paid', compute='_compute_total_paid', store=True, currency_field='company_currency', tracking=True, translate=True)
    full_paid = fields.Boolean(string='Full payment', default=False, tracking=True, translate=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    # @api.model
    # def create(self, reg):
    #     if reg:
    #         if reg.get('expiry_num', _('New')) == _('New'):
    #             reg['expiry_num'] = self.env['ir.sequence'].next_by_code('extenss.credit.concepts_expiration') or _('New')
    #         result = super(ExtenssCreditConceptsExpiration, self).create(reg)
    #         return result
    @api.depends('concept_pay_ids','concept_pay_ids.total_paid_cp')
    def _compute_total_paid(self):
        for reg in self:
            reg.total_paid_concept = sum([line.total_paid_cp for line in reg.concept_pay_ids])
            # reg.total_paid_concept = sum(reg.concept_pay_ids.mapped('total_paid_cp'))
            if round(reg.amount_concept,2) == round(reg.total_paid_concept,2):
                reg.full_paid = True

    concept_pay_ids = fields.One2many('extenss.credit.concept_payments', 'concept_pay_id', string=' ', tracking=True)

class ExtenssCreditConceptPayments(models.Model):
    _name = 'extenss.credit.concept_payments'
    _description = 'Concept Payments'

    concept_pay_id = fields.Many2one('extenss.credit.concepts_expiration', tracking=True, translate=True)
    concept_id = fields.Many2one('extenss.credit.expiry_notices', related='concept_pay_id.expiry_notice_id')
    expiry_number_en = fields.Char(string='Expiry notice number', related='concept_id.expiry_number')
    # expiry_not_number_cp = fields.Integer(string='Expiry notice number', tracking=True, translate=True)
    # concept_id_cp = fields.Char(string='Concept', tracking=True, translate=True)
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
            if reg.get('name', _('New')) == _('New'):
                reg['name'] = self.env['ir.sequence'].next_by_code('extenss.credit.account') or _('New')
            result = super(ExtenssCreditAccount, self).create(reg)
            return result
    
    accnt_mov_ids = fields.One2many('extenss.credit.movements', 'accnt_mov_id', string=' ', tracking=True)

class ExtenssCreditMovements(models.Model):
    _name = 'extenss.credit.movements'
    _description = 'Account Movements'
    _order = 'date_time_move desc'

    accnt_mov_id = fields.Many2one('extenss.credit.account', string='Account', tracking=True, translate=True)
    date_time_move = fields.Datetime(string='Movement date', tracking=True, translate=True)
    movement_type = fields.Selection([('cargo','Charge'),('abono','Credit')], string='Movement type', tracking=True, translate=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    initial_balance = fields.Monetary(string='Initial balance', currency_field='company_currency', tracking=True, translate=True)
    ending_balance = fields.Monetary(string='Ending balance', currency_field='company_currency', tracking=True, translate=True)
    comments = fields.Text(string='Comments', tracking=True, translate=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class CreditsAmortization(models.Model):
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

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class CreditsAmortizationMoras(models.Model):
    _name = 'extenss.credit.moras'
    credit_id = fields.Many2one('extenss.credit')
    init_date = fields.Date('Del')
    end_date = fields.Date('Al')
    days = fields.Integer('Days')
    past_due_balance = fields.Monetary('past due balance',currency_field='company_currency', tracking=True)
    rate = fields.Float('Rate', (2,6), tracking=True, translate=True)
    interest = fields.Monetary('IVA Interest',currency_field='company_currency', tracking=True)
    amount_to_payment = fields.Monetary('Payment',currency_field='company_currency', tracking=True)
    
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class CreditsRequest(models.Model):
    _name = 'extenss.credit.request'
    _description = 'Credit Request'

    @api.constrains('date_settlement')   
    def _check_date_settlement(self):
        for rec in self:
            if datetime.now().date() > rec.date_settlement:
                raise ValidationError(_('Settlement date must be greater or equal than Today'))

    def action_confirm_request(self):
        list_concepts = []
        amount = 0
        pay_rec = self.env['extenss.credit.expiry_notices'].search_count([('credit_expiry_id', '=', self.credit_request_id.id),('req_credit_id', '=', False)])
        num_rec = pay_rec + 1

        ec_id = self.env['extenss.credit'].browse(self.env.context.get('active_ids'))
        for rec in ec_id:
            id_accnt = rec.bill_id.id
            rec.flag_early_settlement = True
        if rec.cs or rec.af:
            if self.outstanding_balance > 0:
                list_concepts.append(['capital', self.outstanding_balance])
            if self.interests > 0:
                list_concepts.append(['interest', self.interests])
            if self.interests_vat > 0:
                list_concepts.append(['intvat', self.interests_vat])
        if rec.af:       
            if self.capital_vat > 0:
                list_concepts.append(['capvat', self.capital_vat])

        if rec.ap:
            payment = self.outstanding_balance + self.interests
            vat_payment = self.interests_vat + self.capital_vat
            list_concepts.append(['payment', payment])
            list_concepts.append(['paymentvat', vat_payment])
        
        if self.penalty_amount > 0:
            list_concepts.append(['penalty_amount', self.penalty_amount])
        if self.purchase_option > 0:
            list_concepts.append(['purchase_option', self.purchase_option])
        if self.vat_purchase_option > 0:
            list_concepts.append(['vat_option', self.vat_purchase_option])
        if self.interests_moratoriums > 0:
            list_concepts.append(['morint', self.interests_moratoriums])
        if self.vat_interest_mora > 0:
            list_concepts.append(['morintvat', self.vat_interest_mora])

        amount = self.security_deposit_balance + self.balance_income_deposit + self.total_settle - self.overdue_balance
        self.create_notice_expiry(num_rec, self.credit_request_id.id, amount, list_concepts, self.id,self.date_settlement)

        # #realiza trasacciones a la cuenta eje
        if self.security_deposit_balance > 0:
            self.env['extenss.credit.accounting_payments'].action_apply_movement(id_accnt, 'abono', self.security_deposit_balance, 'Security Deposit Balance payment')
        if self.balance_income_deposit > 0:
            self.env['extenss.credit.accounting_payments'].action_apply_movement(id_accnt, 'abono', self.balance_income_deposit, 'Balance Income on Deposit payment')

        self.state = 'pending'

    def action_calculate_request(self):
        out_balance = 0
        vat_capital = 0
        credit_id = self.env['extenss.credit'].browse(self.env.context.get('active_ids'))
        rcs = self.env['extenss.credit'].search([('id', '=', credit_id.id)])
        for rc in rcs:
            vat_credit = rc.vat_factor
            penalty_percentage = self.penalty
            poa = rc.purchase_option_amount
            gda = rc.total_guarantee_deposit #guarantee_dep_application
            bid = rc.total_deposit_income #balance_income_deposit
            int_mora = rc.factor_rate
            base_type = rc.calculation_base
            itr = rc.interest_rate

            if base_type == '360/360':
                base = 360
            if base_type == '365/365' or base_type == '360/365':
                base = 365

        past_due_balance = 0
        interest_mora = 0
        interest_mora_tmp = 0
        pay_num = 0
        vat_capital = 0
        amount_penalty = 0
        vat_poa = 0
        vat_interest_mora = 0
        days = 0
        interest_due = 0
        interest_mora_sum = 0
        records = self.env['extenss.credit.expiry_notices'].search([('credit_expiry_id', '=', credit_id.id),('req_credit_id', '=', False)])
        for rec_notice in records:
            past_due_balance += rec_notice.total_to_pay
            pay_num = rec_notice.payment_number

        pay_num_amort = pay_num+1

        reg_due = self.env['extenss.credit.amortization'].search([('no_pay', '=', pay_num),('credit_id', '=', credit_id.id)])
        for rec in reg_due:
            days = self.days_between(rec.expiration_date, self.date_settlement)

        rec_expirys = self.env['extenss.credit.expiry_notices'].search([('credit_expiry_id', '=', credit_id.id),('req_credit_id', '=', False)])
        for r_exp in rec_expirys:
            if r_exp.total_to_pay > 0:
                reg_mor = self.env['extenss.credit.amortization'].search([('no_pay', '=', r_exp.payment_number),('credit_id', '=', credit_id.id)])
                for rcs in reg_mor:
                    capital = rcs.capital
                    days_mora = self.days_between(rcs.expiration_date, self.date_settlement)
                    interest_mora = capital * ((int_mora/100)/base) * days_mora
                    interest_mora_sum += interest_mora

        vat_interest_mora = (vat_credit/100) * interest_mora_sum

        rec_amort = self.env['extenss.credit.amortization'].search([('no_pay', '=', pay_num_amort),('credit_id', '=', credit_id.id)])
        for record in rec_amort:
            out_balance = record.initial_balance
            if rc.cs:
                vat_capital = 0
            else:
                vat_capital = (vat_credit/100) * out_balance

            amount_penalty = (penalty_percentage/100) * out_balance
            vat_poa = (vat_credit/100) * poa

        int_tmp = out_balance * ((itr/100)/base) * days
        vat_int = (vat_credit/100) * int_tmp

        if rc.cs or rc.af:
            sum_total = out_balance + int_tmp + vat_int

        if rc.af: 
            sum_total += vat_capital

        if rc.ap:
            sum_total = out_balance + int_tmp + vat_int + vat_capital

        st = amount_penalty + past_due_balance + interest_mora_sum + vat_interest_mora + poa + vat_poa - gda - bid

        settle_total = sum_total + st

        #settle_total = out_balance + past_due_balance + int_tmp + interest_mora_sum + vat_interest_mora + vat_capital + vat_int + amount_penalty + poa + vat_poa - gda - bid

        self.outstanding_balance = out_balance
        self.overdue_balance = past_due_balance
        self.interests = int_tmp
        self.days_interest = days
        self.interests_moratoriums = interest_mora_sum
        self.vat_interest_mora = vat_interest_mora
        self.capital_vat = vat_capital
        self.interests_vat = vat_int
        self.penalty = penalty_percentage
        self.penalty_amount = amount_penalty
        self.purchase_option = poa
        self.vat_purchase_option = vat_poa
        self.security_deposit_balance = gda
        self.balance_income_deposit = bid
        self.total_settle = settle_total

    def create_notice_expiry(self, num_pay, credit_id, amount, list_concepts, id_req,due_not_date):
        rec_en = self.env['extenss.credit.expiry_notices']
        rec_cp = self.env['extenss.credit.concepts_expiration']
        rec_en.create({
                    'credit_expiry_id': credit_id,
                    'payment_number': num_pay,
                    'due_not_date': due_not_date,
                    'amount_not': amount,
                    'total_paid_not': 0,
                    'total_to_pay': 0,
                    'req_credit_id': id_req,
                })
        rec_notice = rec_en.search([('payment_number', '=', num_pay),('credit_expiry_id', '=', credit_id)])
        for r_notice in rec_notice:
            r_notice.id
        for rec in list_concepts:
            a=0
            b=1
            rec[a]
            rec[b]
            rec_cp.create({
                'expiry_notice_id': r_notice.id,
                'concept': rec[a],
                'amount_concept': rec[b],
                'total_paid_concept': 0,
                'full_paid': 0,
            })
            a += 1
            b += 1

    def days_between(self, d1, d2):
        # d1 = datetime.strptime(d1, "%Y-%m-%d")
        # d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    name = fields.Char(related='credit_request_id.credit_id', string='Credit', tracking=True, translate=True)
    credit_request_id = fields.Many2one('extenss.credit', string='Credit', tracking=True, translate=True)
    date_settlement = fields.Date(string='Settlement date', required=True, tracking=True, translate=True)
    type_request = fields.Selection([('early_settlement','Early settlement')], string='Type request', required=True, tracking=True, translate=True)
    penalty = fields.Float('Penalty', (2,6), tracking=True, translate=True)
    state = fields.Selection([('draft','Draft'),('pending','Pending'),('applied','Applied'),('cancelled','Cancelled')], string='State', default='draft', tracking=True, translate=True)

    outstanding_balance = fields.Monetary(string='Outstanding balance', currency_field='company_currency', tracking=True, translate=True)
    overdue_balance = fields.Monetary(string='Overdue Balance', currency_field='company_currency', tracking=True, translate=True)
    days_interest = fields.Integer(string='Days of interest', tracking=True, translate=True)
    interests = fields.Monetary(string='Interests', currency_field='company_currency', tracking=True, translate=True)
    interests_moratoriums = fields.Monetary(string='Interests moratoriums', currency_field='company_currency', tracking=True, translate=True)
    vat_interest_mora = fields.Monetary(string='Interest moratoriums VAT', currency_field='company_currency', tracking=True, translate=True)
    capital_vat= fields.Monetary(string='Capital VAT', currency_field='company_currency', tracking=True, translate=True)
    interests_vat = fields.Monetary(string='Interests VAT', currency_field='company_currency', tracking=True, translate=True)

    penalty_amount = fields.Monetary(string='Penalty Amount', currency_field='company_currency', tracking=True, translate=True)
    purchase_option = fields.Monetary(string='Purchase option', currency_field='company_currency', tracking=True, translate=True)
    vat_purchase_option = fields.Monetary(string='VAT Purchase option', currency_field='company_currency', tracking=True, translate=True)
    security_deposit_balance = fields.Monetary(string='Security Deposit Balance', currency_field='company_currency', tracking=True, translate=True)
    balance_income_deposit = fields.Monetary(string='Balance Income on Deposit', currency_field='company_currency', tracking=True, translate=True)
    total_settle = fields.Monetary(string='Total to Settle', currency_field='company_currency', tracking=True, translate=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)