from odoo import fields, models, exceptions, api, _
from odoo.exceptions import Warning, UserError, ValidationError

class ExtenssRequestDestination(models.Model):
    _name =  'extenss.request.destination'
    _order = 'name'
    _description = 'Destination loan'

    name = fields.Char(string='Destination loan', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestSalesChannelId(models.Model):
    _name = 'extenss.request.sales_channel_id'
    _order = 'name'
    _description ='Sales channel'

    name = fields.Char(string='Sales channel', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestCategoryAct(models.Model):
    _name = 'extenss.request.category_act'
    _order = 'name'
    _description = 'Category'

    name = fields.Char(strig='Category', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestCategoryPas(models.Model):
    _name = 'extenss.request.category_pas'
    _order = 'name'
    _description = 'Category'

    name = fields.Char(strig='Category', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestHipoteca(models.Model):
    _name = 'extenss.request.hipoteca'
    _order = 'name'
    _description = 'Tipo de hipoteca'

    name = fields.Char(string='Tipo de hipoteca', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestTipoIngreso(models.Model):
    _name = 'extenss.request.tipo_ingreso'
    _order = 'name'
    _description = 'Tipo de ingreso'

    name = fields.Char(string='Tipo de ingreso', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestTipoGasto(models.Model):
    _name = 'extenss.request.tipo_gasto'
    _order = 'name'
    _description = 'Tipo de gasto'

    name = fields.Char(string='Tipo de gasto', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestFrecuencia(models.Model):
    _name = 'extenss.request.frecuencia'
    _order = 'name'
    _description = 'Frecuencia'

    name = fields.Char(string='Frecuencia', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class ExtenssRequestBase(models.Model):
    _name = 'extenss.request.base'
    _order = 'name'
    _description = 'Base'

    name = fields.Char(string='Base', required=True, translate=True)
    shortcut = fields.Char(string='Abbreviation', translate=True)

class Lead(models.Model):
    _inherit = "crm.lead"

    @api.constrains('owners_phone')
    def _check_prin_phone(self):
        for reg in self:
            if not reg.owners_phone == False:
                digits1 = [int(x) for x in reg.owners_phone if x.isdigit()]
                if len(digits1) != 10:
                    raise ValidationError(_('The principal phone must be a 10 digits'))
    
    @api.constrains('months_residence')
    def _check_years(self):
        for reg_years in self:
            if reg_years.months_residence > 999:
                raise ValidationError(_('The Years residence must be a 3 digits'))

    @api.constrains('stage_id')
    def _check_stage_id(self):
        self.validations()
        self.user_send_req = self.env.user.id
        #self.stage_id =  2

    def open_docs_count(self):
        domain = ['|', ('lead_id', '=', [self.id]), ('partner_id', '=', self.partner_id.id)]
        return {
            'name': _('Documents'),
            'view_type': 'kanban',
            'domain': domain,
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            #'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'kanban,tree,form',
            'context': "{'default_folder_id': %s}" % self.ids
        }

    def get_document_count(self):
        count = self.env['documents.document'].search_count(['|', ('lead_id', '=', self.id), ('partner_id', '=', self.partner_id.id)])
        self.document_count = count

    def action_send_sale(self):
        self.validations()
        self.send_crm = 'Sending'
        self.user_send_req = self.env.user.id
        self.stage_id = 2

    def action_activation(self):
        self.stage_id = 4  

    def validations(self):
        docs = self.env['documents.document'].search([('lead_id', '=', self.id)])
        for reg_docs in docs:
            if not reg_docs.attachment_id:
                raise ValidationError(_('Attach the corresponding documents'))

        quotations = self.env['sale.order'].search([('opportunity_id', '=', self.id),('state', '=', 'sale')])
        #if quotations:
        for reg in quotations:
            if not reg.signature:
                raise ValidationError(_('Missing the quote signature %s' % reg.name))

            if self.partner_type == 'company':
                if reg.product_id.financial_situation:
                    reg_fs = self.env['extenss.crm.lead.financial_sit'].search([('financial_id', '=', self.id)])
                    if not reg_fs:
                        raise ValidationError(_('Enter a record in Financial situation tab'))
                    if reg_fs.activos_totales <= 0.0:
                        raise ValidationError(_('Enter data in the Assets tab in any of the sections'))
                    if reg_fs.pasivo_total_capital_contable <= 0.0:
                        raise ValidationError(_('Enter data in Liabilities tab in any of the sections'))
                    if not reg_fs.beneficios_ope_totales:
                        raise ValidationError(_('Enter data in Income statement tab in any of the sections'))
            if self.partner_type == 'person':
                if reg.product_id.endorsement:
                    cont_reg_av = 0
                    reg_pf = self.env['extenss.customer.personal_ref'].search([('personal_ref_id', '=', self.id)])
                    if not reg_pf:
                        raise ValidationError(_('Add an Aval type record in the Personal References tab'))
                    for r in reg_pf:
                        reg_p = self.env['extenss.customer.type_refbank'].search([('id', '=', r.type_reference_personal_ref.id)])
                        if reg_p.shortcut == 'AV':
                            cont_reg_av += 1
                    if cont_reg_av <= 0:
                        raise ValidationError(_('Enter a Endorsement type record in Personal references tab for quotation number %s' % reg.name))
                if reg.product_id.guarantee:
                    reg_w = self.env['extenss.crm.lead.ownership'].search([('ownership_id', '=', self.id)])
                    if not reg_w:
                        raise ValidationError(_('Enter a record in Ownership tab %s' % reg.name))
                if reg.product_id.socioeconomic_study:
                    reg_source = self.env['extenss.crm.lead.source_income'].search([('surce_id', '=', self.id)])
                    reg_exp = self.env['extenss.crm.lead.source_income'].search([('gasto_id', '=', self.id)])
                    if not reg_source:
                        raise ValidationError(_('Enter a record in Source income tab in the section of Income for quotation number %s' % reg.name))
                    if not reg_exp:
                        raise ValidationError(_('Enter a record in Source income tab in the section of Expenses for quotation number %s' % reg.name))
                if reg.product_id.beneficiaries:
                    cont_reg_bf = 0
                    reg_benef = self.env['extenss.customer.personal_ref'].search([('personal_ref_id', '=', self.id)])
                    if not reg_benef:
                        raise ValidationError(_('Add a beneficiary type record in the Personal References tab'))
                    for r in reg_benef:
                        reg_p = self.env['extenss.customer.type_refbank'].search([('id', '=', r.type_reference_personal_ref.id)])
                        if reg_p.shortcut == 'BF':
                            cont_reg_bf += 1
                    if cont_reg_bf <= 0:
                        raise ValidationError(_('Enter a Beneficiaries type record in Personal references tab for quotation number %s' % reg.name))
                if reg.product_id.financial_situation:
                    reg_pos = self.env['extenss.crm.lead.financial_pos'].search([('financial_pos_id', '=', self.id)])
                    reg_pas = self.env['extenss.crm.lead.financial_pos'].search([('financial_pas_id', '=', self.id)])
                    if not reg_pos:
                        raise ValidationError(_('Enter a record in Financial position tab in the section Assets for quotation number %s' % reg.name))
                    if not reg_pas:
                        raise ValidationError(_('Enter a record in Financial position tab in the section Passives for quotation number %s' % reg.name))

                if reg.product_id.patrimonial_relationship:
                    if self.total_resident <= 0.0:
                        raise ValidationError(_('Enter data in Residence profile tab for quotation number %s' % reg.name))
                if reg.product_id.obligated_solidary:
                    cont_reg_os = 0
                    reg_os = self.env['extenss.customer.personal_ref'].search([('personal_ref_id', '=', self.id)])
                    if not reg_os:
                        raise ValidationError(_('Add a record of type bound by solidarity in the Personal References tab'))
                    for r in reg_os:
                        reg_p = self.env['extenss.customer.type_refbank'].search([('id', '=', r.type_reference_personal_ref.id)])
                        if reg_p.shortcut == 'OS':
                            cont_reg += 1
                    if cont_reg <= 0:
                        raise ValidationError(_('Enter a Solidarity bound type record in Personal references tab for quotation number %s' % reg.name))
            if reg.state == 'sale':
                if self.stage_id.id == 4:
                    request_ids = self.env['sign.request.item'].search([('partner_id', '=', self.partner_id.id)]).mapped('sign_request_id')
                    for df in reg.product_id.rec_docs_ids:
                        doc_fal = df.catalog_recru_docs.name
                        for ref in request_ids:
                            doc_name=ref.reference[-10:-4]
                            if doc_name == quotations.name :
                                doc_name=ref.reference[0:-11]
                                if doc_name == 'Contrato': doc_name='CON'
                                if doc_name == 'Pagare': doc_name='PAY'
                                if doc_name == df.catalog_recru_docs.shortcut :
                                    doc_fal=''
                                    doc_name=ref.reference[-10:-4]
                                    if doc_name == quotations.name :
                                        no_documents=1
                                        if ref.state != 'signed' :
                                            raise ValidationError(_('unsigned document %s' % ref.reference))
                                    break
                        if len(doc_fal) > 0:
                            raise ValidationError(_('must add %s' % doc_fal))       

    def action_autorize_sale(self):
        self.user_auth_req = self.env.user.id
        self.stage_id = 3

    def action_refuse_sale(self):
        self.user_refuse_req = self.env.user.id

    destination_id = fields.Many2one('extenss.request.destination', string='Destination loan', tracking=True, translate=True)
    name = fields.Char(string='Request number', required=True, copy=False, readonly=True, index=True, tracking=True, translate=True, default=lambda self: _('New'))
    sales_channel_id = fields.Many2one('extenss.request.sales_channel_id', tracking=True, translate=True)
    create_date = fields.Date(string='Create date', readonly=True, tracking=True, translate=True)
    closed_date = fields.Date(string='Closed date', readonly=True, tracking=True, translate=True)
    product_id = fields.Many2one('product.template', string='Product', tracking=True, translate=True)
    user_id = fields.Many2one('res.users')
    partner_type = fields.Selection('res.partner', related='partner_id.company_type')
    #team_id = fields.Char(string='Office')
    #planned_revenue = fields.Char(string='Request amount', translate=True)
    description = fields.Text(string='Comments', tracking=True, translate=True)
    document_count = fields.Integer("Documentos", compute='get_document_count', tracking=True)
    #stage_id = fields.Many2one('crm.stage', string='Stage', tracking=True, translate=True)
    partner_id = fields.Many2one('res.partner', translate=True)
    send_crm = fields.Char(string='Request send', tracking=True, translate=True)
    user_send_req = fields.Many2one('res.users', string='User sending', tracking=True, translate=True)
    user_auth_req = fields.Many2one('res.users', string='Authorizing user', tracking=True, translate=True)
    user_refuse_req = fields.Many2one('res.users', string='User rejecting', tracking=True, translate=True)
    #Resident Profile
    housing_type_rp = fields.Selection([('rented', 'Rented'),('own','Own')], string='Housing type', tracking=True, translate=True)
    owners_name = fields.Many2one('res.partner', string='Owners name', tracking=True, translate=True)
    owners_phone = fields.Char(string='Owners phone', tracking=True, translate=True)
    montly_rent = fields.Monetary(string='Montly rent', currency_field='company_currency', tracking=True, translate=True)
    months_residence = fields.Integer(string='Months in Residence', tracking=True, translate=True)
    residency_profile = fields.Char(string='Residency profile', tracking=True, translate=True)

    rent = fields.Monetary(string='Rent', currency_field='company_currency', tracking=True, translate=True)
    first_mortage = fields.Monetary(string='First mortage', currency_field='company_currency', tracking=True, translate=True)
    another_finantiation = fields.Monetary(string='Another finantiation', currency_field='company_currency', tracking=True, translate=True)
    risk_insurance = fields.Monetary(string='Risk insurance', currency_field='company_currency', tracking=True, translate=True)
    real_state_taxes = fields.Monetary(string='Real state taxes', currency_field='company_currency', tracking=True, translate=True)
    mortage_insurance = fields.Monetary(string='Mortage insurance', currency_field='company_currency', tracking=True, translate=True)
    debts_cowners = fields.Monetary(string='Debts co-owners', currency_field='company_currency', tracking=True, translate=True)
    other = fields.Monetary(string='Other', currency_field='company_currency', tracking=True, translate=True)
    total_resident = fields.Monetary(string='Total', compute='_compute_total_resident', store=True, currency_field='company_currency')

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    @api.depends('rent','first_mortage','another_finantiation','risk_insurance','real_state_taxes','mortage_insurance','debts_cowners','other')
    def _compute_total_resident(self):
        for reg in self:
            reg.total_resident = reg.rent + reg.first_mortage + reg.another_finantiation + reg.risk_insurance + reg.real_state_taxes + reg.mortage_insurance + reg.debts_cowners + reg.other

    @api.model
    def create(self, reg):
        if reg:
            if reg.get('name', _('New')) == _('New'):
                reg['name'] = self.env['ir.sequence'].next_by_code('crm.lead') or _('New')
            result = super(Lead, self).create(reg)
            return result

    fin_sit_ids = fields.One2many('extenss.crm.lead.financial_sit', 'financial_id', string=' ', tracking=True)
    fin_pos_ids = fields.One2many('extenss.crm.lead.financial_pos', 'financial_pos_id', string=' ')
    fin_pas_ids = fields.One2many('extenss.crm.lead.financial_pos', 'financial_pas_id', string=' ')
    owner_ids = fields.One2many('extenss.crm.lead.ownership', 'ownership_id', string=' ')
    surce_ids = fields.One2many('extenss.crm.lead.source_income', 'surce_id', string=' ')
    exp_ids = fields.One2many('extenss.crm.lead.source_income', 'gasto_id', string=' ')
    personal_ref_ids = fields.One2many('extenss.customer.personal_ref', 'personal_ref_id', string=' ')

class ExtenssDocuments(models.Model):
    _inherit = "documents.document"

    lead_id = fields.Char(string="Lead Id")
    doc_prod_id = fields.Char(string="Document Prod Id")

class ExtenssCrmLeadFinancialSit(models.Model):
    _name = "extenss.crm.lead.financial_sit"
    _description = "Financial situation"

    financial_id = fields.Many2one('crm.lead', tracking=True)#modelo padre
    date_fin_sit = fields.Date(string='Date', required=True, tracking=True, translate=True)
    #partner_name = fields.Char(string='Company', translate=True)
    partner_id = fields.Many2one('res.partner', string='Customer')#, default=lambda self: self.env.user.partner_id.id)#default=10)#default=lambda self: self.env.partner_id)#
    #partner_name = fields.Char(related='partner_id.name', string='Company', translate=True)
    base = fields.Many2one('extenss.request.base', string='Base', tracking=True, translate=True)
    frequency = fields.Many2one('extenss.request.frecuencia', string='Frequency', tracking=True, translate=True)
    description = fields.Char(string='Description', tracking=True, translate=True)
    #Assets
    efectivo = fields.Monetary(string='Cash', currency_field='company_currency', tracking=True, translate=True)
    cuentas_cobrar = fields.Monetary(string='Accounts receivable', currency_field='company_currency', tracking=True, translate=True)
    inventario = fields.Monetary(string='Inventory', currency_field='company_currency', tracking=True, translate=True)
    activo_adicional1_tipo = fields.Char(string='Additional asset 1 Type', tracking=True, translate=True)
    activo_adicional1_importe = fields.Monetary(string='Additional asset 1 Amount', currency_field='company_currency', tracking=True, translate=True)
    activo_adicional2_tipo = fields.Char(string='Additional asset 2 Type', translate=True)
    activo_adicional2_importe = fields.Monetary(string='Additional asset 2 Amount', currency_field='company_currency', tracking=True, translate=True)
    activo_otras_cuentas = fields.Monetary(string='Assets from other accounts', currency_field='company_currency', tracking=True, translate=True)
    total_activo_circulante = fields.Monetary(string='Total surrounding assets', currency_field='company_currency', compute='_compute_total_circulante', store=True, tracking=True, translate=True)

    activos_fijos = fields.Monetary(string='Fixed assets', currency_field='company_currency', tracking=True, translate=True)
    depreciacion = fields.Monetary(string='Depreciation', currency_field='company_currency', tracking=True, translate=True)
    activos_intangibles = fields.Monetary(string='Intangible assets', currency_field='company_currency', tracking=True, translate=True)
    total_activos_fijos = fields.Monetary(string='Total fixed assets', currency_field='company_currency', compute='_compute_total_af', store=True, tracking=True, translate=True)

    otros_activos = fields.Monetary(string='Other assets', currency_field='company_currency', tracking=True, translate=True)
    otro_activo_adicional = fields.Char(string='Other additional asset, asset type', tracking=True, translate=True)
    otro_activo_importe = fields.Monetary(string='Other additional asset, asset amount', currency_field='company_currency', tracking=True, translate=True)
    total_otros_activos = fields.Monetary(string='Total other assets', currency_field='company_currency', compute='_compute_total_oa', store=True, tracking=True, translate=True)

    activos_totales = fields.Monetary(string='Total assets', currency_field='company_currency', compute='_compute_total_activos', store=True, tracking=True, translate=True)
    verifica_importes = fields.Boolean(string='Check amounts', compute='_compute_flag_vi', store=True, default=False, readonly=True, tracking=True, translate=True)#(Activo=Pasivo+Capital)
    #Liabilities
    proveedores	= fields.Monetary(string='Providers', currency_field='company_currency', tracking=True, translate=True)
    pasivo_tipo = fields.Char(string='Type liabilities', tracking=True, translate=True)
    pasivo_importe = fields.Monetary(string='Liabilities amount', currency_field='company_currency', tracking=True, translate=True)
    parte_corto_plazo = fields.Monetary(string='Short-term share of long-term debt', currency_field='company_currency', tracking=True, translate=True)
    otro_pasivo_circulante = fields.Monetary(string='Other current liabilities', currency_field='company_currency', tracking=True, translate=True)
    pasivo_total_circulante = fields.Monetary(string='Total current liabilities', currency_field='company_currency', compute='_compute_pasivo_tc', store=True, tracking=True, translate=True)

    deuda_largo_plazo = fields.Monetary(string='Long-term debt', currency_field='company_currency', tracking=True, translate=True)
    deuda_adicional_actual_tipo	= fields.Char(string='Current additional debt type', tracking=True, translate=True)
    deuda_adicional_actual_importe = fields.Monetary(string='Current additional debt amount', currency_field='company_currency', tracking=True, translate=True)
    otro_pasivo_no_circulante = fields.Monetary(string='Other non-current liabilities', currency_field='company_currency', tracking=True, translate=True)
    pasivo_total_no_circulante	= fields.Monetary(string='Total non-current liabilities', currency_field='company_currency', compute='_compute_pasivo_tnc', store=True, tracking=True, translate=True)

    capital	= fields.Monetary(string='Capital', currency_field='company_currency', tracking=True, translate=True)
    capital_desembolso = fields.Monetary(string='Disbursement capital', currency_field='company_currency', tracking=True, translate=True)
    utilidades_perdidas_acumuladas = fields.Monetary(string='Accumulated profit (loss)', currency_field='company_currency', tracking=True, translate=True)
    utilidad_ejercicio = fields.Monetary(string='Profit for the year', currency_field='company_currency', tracking=True, translate=True)
    total_capital_contable = fields.Monetary(string='Total stockholders equity', currency_field='company_currency', compute='_compute_total_cc', store=True, tracking=True, translate=True)
    
    pasivo_total_capital_contable = fields.Monetary(string='Total liabilities and Stockholders equity', currency_field='company_currency', compute='_compute_pasivo_tcc', store=True, tracking=True, translate=True)

    #Income Statement
    ventas_netas = fields.Monetary(string='Net sales', currency_field='company_currency', tracking=True, translate=True)

    costo_ventas = fields.Monetary(string='Sales cost', currency_field='company_currency', tracking=True, translate=True)
    ganancia_bruta = fields.Monetary(string='Gross profit', currency_field='company_currency', compute='_compute_ganancia_bruta', store=True, tracking=True, translate=True)

    otros_ingresos_is = fields.Monetary(string='Other income', currency_field='company_currency', tracking=True, translate=True)
    ingresos_adicionales_tipo = fields.Char(string='Additional operating income, type of income', tracking=True, translate=True)
    ingresos_adicionales_importe = fields.Monetary(string='Additional operating income, amount of income', currency_field='company_currency', tracking=True, translate=True)
    gastos_ope_ad_1_tipo= fields.Char(string='Additional operating expenses 1, type of expenses', tracking=True, translate=True)
    gastos_ope_ad_1_importe = fields.Monetary(string='Additional operating expenses 1, amount of expenses', currency_field='company_currency', tracking=True, translate=True)
    gastos_ope_ad_2_tipo = fields.Char(string='Additional operating expenses 2, type of expenses', tracking=True, translate=True)
    gastos_ope_ad_2_importe = fields.Monetary(string='Additional operating expenses 2, amount of expenses', currency_field='company_currency', tracking=True, translate=True)
    beneficios_ope_totales = fields.Monetary(string='Total operating profit', currency_field='company_currency', compute='_compute_beneficios', store=True, tracking=True, translate=True)

    interes = fields.Monetary(string='Interest', currency_field='company_currency', tracking=True, translate=True)
    otros_gastos = fields.Monetary(string='Other expenses', currency_field='company_currency', tracking=True, translate=True)
    depreciación = fields.Monetary(string='Depreciation', currency_field='company_currency', tracking=True, translate=True)
    impuestos = fields.Monetary(string='Taxes', currency_field='company_currency', tracking=True, translate=True)
    utilidad_neta = fields.Monetary(string='Net profit', currency_field='company_currency', tracking=True, translate=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

    @api.depends('ventas_netas','costo_ventas')
    def _compute_ganancia_bruta(self):
        for reg in self:
            reg.ganancia_bruta = reg.ventas_netas - reg.costo_ventas

    @api.depends('otros_ingresos_is','ingresos_adicionales_importe','gastos_ope_ad_1_importe','gastos_ope_ad_2_importe')
    def _compute_beneficios(self):
        for reg in self:
            reg.beneficios_ope_totales = reg.otros_ingresos_is + reg.ingresos_adicionales_importe - reg.gastos_ope_ad_1_importe - reg.gastos_ope_ad_2_importe

    @api.depends('proveedores','pasivo_importe','parte_corto_plazo','otro_pasivo_circulante')
    def _compute_pasivo_tc(self):
        for reg in self:
            reg.pasivo_total_circulante = reg.proveedores + reg.pasivo_importe + reg.parte_corto_plazo + reg.otro_pasivo_circulante

    @api.depends('deuda_largo_plazo','deuda_adicional_actual_importe','otro_pasivo_no_circulante')
    def _compute_pasivo_tnc(self):
        for reg in self:
            reg.pasivo_total_no_circulante = reg.deuda_largo_plazo + reg.deuda_adicional_actual_importe + reg.otro_pasivo_no_circulante

    @api.depends('capital','capital_desembolso','utilidades_perdidas_acumuladas','utilidad_ejercicio')
    def _compute_total_cc(self):
        for reg in self:
            reg.total_capital_contable = reg.capital + reg.capital_desembolso + reg.utilidades_perdidas_acumuladas + reg.utilidad_ejercicio

    @api.depends('pasivo_total_circulante','pasivo_total_no_circulante','total_capital_contable')
    def _compute_pasivo_tcc(self):
        for reg in self:
            reg.pasivo_total_capital_contable = reg.pasivo_total_circulante + reg.pasivo_total_no_circulante + reg.total_capital_contable

    @api.depends('efectivo','cuentas_cobrar','inventario','activo_adicional1_importe','activo_adicional2_importe','activo_otras_cuentas')
    def _compute_total_circulante(self):
        for reg in self:
            reg.total_activo_circulante = reg.efectivo + reg.cuentas_cobrar + reg.inventario + reg.activo_adicional1_importe + reg.activo_adicional2_importe + reg.activo_otras_cuentas

    @api.depends('activos_fijos','depreciacion','activos_intangibles')
    def _compute_total_af(self):
        for reg in self:
            reg.total_activos_fijos = reg.activos_fijos + reg.depreciacion + reg.activos_intangibles
    
    @api.depends('otros_activos','otro_activo_importe')
    def _compute_total_oa(self):
        for reg in self:
            reg.total_otros_activos = reg.otros_activos + reg.otro_activo_importe

    @api.depends('total_activo_circulante','total_activos_fijos','total_otros_activos')
    def _compute_total_activos(self):
        for reg in self:
            reg.activos_totales = reg.total_activo_circulante + reg.total_activos_fijos + reg.total_otros_activos
    
    @api.depends('activos_totales','pasivo_total_capital_contable')
    def _compute_flag_vi(self):
        for reg in self:
            if reg.activos_totales == reg.pasivo_total_capital_contable:
                reg.verifica_importes = True
            if reg.activos_totales != reg.pasivo_total_capital_contable:
                reg.verifica_importes = False

class ExtenssCrmLeadFinancialPos(models.Model):
    _name = "extenss.crm.lead.financial_pos"
    _description = "Financial position"

    financial_pos_id = fields.Many2one('crm.lead')#modelo padre
    category_act = fields.Many2one('extenss.request.category_act', string='Category', tracking=True, translate=True)
    value_act = fields.Monetary(string='Value', currency_field='company_currency', tracking=True, translate=True)
    description_act = fields.Char(string='Description', tracking=True, translate=True)
    institution_act = fields.Many2one('res.bank', string='Institution', tracking=True, translate=True)#catalogo de bancos
    account_number_act = fields.Char(string='Account number', tracking=True, translate=True)
    verify_act = fields.Boolean(string='Verify', tracking=True, translate=True)
    #total_activos_act = fields.Monetary(string='Total activos', currency_field='company_currency', compute='_compute_total_act', store=True, tracking=True, translate=True)

    financial_pas_id = fields.Many2one('crm.lead')#modelo padre
    category_pas = fields.Many2one('extenss.request.category_pas', string='Category', tracking=True, translate=True)
    value_pas = fields.Monetary(string='Value', currency_field='company_currency', tracking=True, translate=True)
    pago_mensual_pas = fields.Monetary(string='Monthly payment', currency_field='company_currency', tracking=True, translate=True)
    description_pas = fields.Char(string='Description', tracking=True, translate=True)
    institution_pas = fields.Many2one('res.bank', string='Institution', tracking=True, translate=True)#catalogo de bancos
    account_number_pas = fields.Char(string='Account number', tracking=True, translate=True)
    tipo_hipoteca = fields.Many2one('extenss.request.hipoteca', string='Type of mortgage', tracking=True, translate=True)
    #total_pasivos = fields.Monetary(string='Total pasivos', currency_field='company_currency', compute='_compute_pasivos', store=True, tracking=True, translate=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class ExtenssCrmLeadSourceIncome(models.Model):
    _name = "extenss.crm.lead.source_income"
    _description = "Source of income"

    surce_id = fields.Many2one('crm.lead')
    tipo_ingreso = fields.Many2one('extenss.request.tipo_ingreso', string='Type of income', tracking=True, translate=True)
    importe_ing= fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    persona_ing	= fields.Many2one('res.partner', string='Person', tracking=True, translate=True)
    importe_mensual_ing = fields.Monetary(string='Monthly amount', currency_field='company_currency', tracking=True, translate=True)
    frecuencia_ing = fields.Many2one('extenss.request.frecuencia', string='Frequency', tracking=True, translate=True)#catalogo
    sujeto_impuestos_ing = fields.Boolean(string='Subject to tax', tracking=True, translate=True)
    comentarios_ing	= fields.Char(string='Comments', tracking=True, translate=True)
    total_ingresos = fields.Monetary(string='Total income', currency_field='company_currency', tracking=True, translate=True)
    
    gasto_id = fields.Many2one("crm.lead")
    tipo_gasto = fields.Many2one('extenss.request.tipo_gasto', string='Expense type', tracking=True, translate=True)
    importe_gas = fields.Monetary(string='Amount', currency_field='company_currency', tracking=True, translate=True)
    persona_gas = fields.Many2one('res.partner', string='Person', tracking=True, translate=True)
    importe_mensual_gas = fields.Monetary(string='Monthly amount', currency_field='company_currency', tracking=True, translate=True)
    frecuencia_gas = fields.Many2one('extenss.request.frecuencia', string='Frequency', tracking=True, translate=True)	
    comentarios_gas = fields.Char(string='Comments', tracking=True, translate=True)
    total_gastos = fields.Monetary(string='Total spends', currency_field='company_currency', tracking=True, translate=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class ExtenssCrmLeadOwnership(models.Model):
    _name = "extenss.crm.lead.ownership"
    _description = "Ownership"

    ownership_id = fields.Many2one('crm.lead')#modelo padre
    description_own = fields.Char(string='Description', tracking=True, translate=True)
    percentage_properties = fields.Float(string='Percentage in properties', digits=(2,6), tracking=True, translate=True)
    purchace_price = fields.Monetary(string='Purchace price', currency_field='company_currency', tracking=True, translate=True)
    bookvalue = fields.Monetary(string='Bookvalue', currency_field='company_currency', tracking=True, translate=True)
    market_value = fields.Monetary(string='Market value', currency_field='company_currency', tracking=True, translate=True)
    stock_exchange_value = fields.Monetary(string='Stock exchange value', currency_field='company_currency', tracking=True, translate=True)
    mortages_own = fields.Monetary(string='Mortages', currency_field='company_currency', tracking=True, translate=True)

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

class ExtenssCrmPersonalReferences(models.Model):
    _inherit = "extenss.customer.personal_ref"

    personal_ref_id = fields.Many2one('crm.lead')#modelo padre
    # type_reference_personal_ref = fields.Many2one('extenss.customer.type_refbank', string='Type reference', required=True,translate=True)
    # #type_reference_personal_ref = fields.Char(string='Type reference', required=True,translate=True)
    # reference_name_personal_ref = fields.Char(string='Reference name', required=True, translate=True)
    # phone_personal_ref = fields.Char(string='Phone', translate=True)
    # cell_phone_personal_res = fields.Char(string='Cell phone', translate=True)
    # email_personal_ref = fields.Char(string='Email', translate=True)