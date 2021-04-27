from odoo import fields, models, api,_
from  odoo.exceptions import  UserError

class course(models.Model):
    _name = "course.record"
    name = fields.Char(string="Course Name", required=True)
    description = fields.Char(string="Course Description", required=True)
    start_date = fields.Date(string="Course Start", required=True)
    end_date = fields.Date(string="Course End", required=True)
    time_on = fields.Float(string="Time on", required=True)
    time_of = fields.Float(string="Time off", required=True)
    price = fields.Float(string="Course Price", required=True)
    traineds = fields.Many2one("trained.record", string="Trained Name", required=True)
    room_id = fields.Many2one("room.record", string="Room name", required=True)
    hours = fields.Float(string="Course Hours", required=True)
    hours_price = fields.Float(string="Hours Price", required=True)

    @api.constrains('start_date','room_id','time_on')
    def check_start_date(self):
        for rec in self:
            if self.search([('start_date','=',rec.start_date),
                            ('time_on', '=', rec.time_on),
                            ('room_id','=',rec.room_id.id),
                            ('id','!=',rec.id)]):
                raise UserError(_('Sorry, This Room Has Been Reserved and Time!'))

    # @api.constrains('time_on','room_id')
    # def check_time_on(self):
    #     for rec in self:
    #         if self.search([('time_on','=',rec.time_on),
    #                         ('room_id','=',rec.room_id.id),
    #                         ('id','!=',rec.id)]):
    #             raise UserError(_('Sorry This Room Has Been Reserved is Same Time'))


    # student_id = fields.Many2one("student.record", string="Student_ID")
    # course_descriptional = fields.Char(related="course.description")
    # course_start = fields.Date(related="course.start_date")
    # course_end = fields.Date(related="course.end_date")
    # course_price = fields.Float(related="course.price")
    # course_traineds = fields.Char(related="course.traineds")


class trained(models.Model):
    _name = "trained.record"
    name = fields.Char(string="Trained Name", required=True)
    id_number = fields.Char(string="ID Number", required=True)
    address = fields.Char(string="Trained Address")
    phone = fields.Char(string="Trained Phone", required=True)
    email = fields.Char(string="Trained Email")


class student(models.Model):
    _name = "student.record"
    _rec_name = 'code'
    code = fields.Char(default=lambda self: ('Serial_Number'), readonly=True)
    name = fields.Char(string="Name")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Char(string="Address")
    Training_name = fields.Many2one("course.record",string="Select Course")
    std_description = fields.Char(string="Course description")
    std_start = fields.Date(string="Start date")
    std_end = fields.Date(string="End date")
    std_price = fields.Float(string="Course Price")
    std_traineds = fields.Many2one("trained.record", string="Trained name")
    std_room = fields.Many2one("room.record", string="Room name")
    std_time_on = fields.Float(string="Time on")
    std_time_of = fields.Float(string="Time of")
    # unit_total = fields.Float()
    # course_id = fields.Many2many("course.record")
    # student_infor_id = fields.One2many("student.infor.record","student_id")
    # line_cost = fields.Float(string="Course Price")
    line_amount = fields.Float(string="Student Price")
    total = fields.Float(string="Total Rest", compute="_compute_total")
    # pay_ids = fields.One2many("pay.record", "student_ids", string="Trained name")
    # pay_ids = fields.Many2one("pay.record", string="pay_id")

    state = fields.Selection([
        ('draft','Draft'),
        ('confirm','Confirm'),
        ('done','Done'),
        ('cancel','Cancel'),
    ], string='Status', readonly=True, default='draft')


    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.depends('std_price','line_amount')
    def _compute_total(self):
        for line in self:
            line.total = (line.std_price - line.line_amount)

    @api.onchange('Training_name')
    def set_std_price(self):
        for rec in self:
            if rec.Training_name:
                rec.std_price = rec.Training_name.price

    @api.onchange('Training_name')
    def set_std_time_on(self):
        for rec in self:
            if rec.Training_name:
                rec.std_time_on = rec.Training_name.time_on

    @api.onchange('Training_name')
    def set_std_time_of(self):
        for rec in self:
            if rec.Training_name:
                rec.std_time_of = rec.Training_name.time_of

    @api.onchange('Training_name')
    def set_std_description(self):
        for rec in self:
            if rec.Training_name:
                rec.std_description = rec.Training_name.description

    @api.onchange('Training_name')
    def set_std_start(self):
        for rec in self:
            if rec.Training_name:
                rec.std_start = rec.Training_name.start_date

    @api.onchange('Training_name')
    def set_std_end(self):
        for rec in self:
            if rec.Training_name:
                rec.std_end = rec.Training_name.end_date

    @api.onchange('Training_name')
    def set_std_traineds(self):
        for rec in self:
            if rec.Training_name:
                rec.std_traineds = rec.Training_name.traineds

    @api.onchange('Training_name')
    def set_std_room(self):
        for rec in self:
            if rec.Training_name:
                rec.std_room = rec.Training_name.room_id

    @api.model
    def create(self, vals):
        if vals.get('code', ('Serial_Number')) == ('Serial_Number'):
            vals['code'] = self.env['ir.sequence'].next_by_code('student.record') or ('Serial_Number')
            dlat = super(student, self).create(vals)
            # dlat = super(lounge, self).create(vals)
            return dlat

    def action_view_invoice(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        default_account = self.env['account.journal'].search([('type', '=', 'purchase')],
                                                             limit=1).default_debit_account_id or False

        Training_name = []
        for line in self.Training_name:
            Training_name.append((0, 0, {
                'price_unit' : line.price,
                'quantity': 1,
                'name': line.name,
                'account_id' : default_account.id if default_account else False,
            }))
            print(Training_name)
            result['context'] = {
                'default_type' : 'in_invoice',
                'default_line_ids' : Training_name,
            }
            view_id = self.env.ref('account.view_move_form', False)
            form_view = [(view_id and view_id.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            result['name'] = self.code
            result['context']['default_invoice_origin'] = self.code
            result['context']['default_ref'] = self.code
            return result






    # @api.depends('student_infor_id')
    # def _compute_total(self):
    #     for std in self:
    #         line_amount = line_cost = 0.0
    #         for line in std.student_infor_id:
    #             line_amount += line.amount
    #             line_cost += line.cost
    #             std.update({
    #                 'line_cost':line_cost,
    #                 'line_amount':line_amount,
    #                 'total':line_cost - line_amount,
    #             })
#
#
# class student_infor(models.Model):
#     _name = "student.infor.record"
#     name = fields.Many2one("course.record", string="Course Name")
#     amount = fields.Float(string="Amount Price")
#     cost = fields.Float(string="Course cost")
#     total = fields.Float(string="Total Rest", compute="_compute_total")
#     student_id = fields.Many2one("student.record")
#
#     @api.depends('cost','amount')
#     def _compute_total(self):
#         for line in self:
#             line.total = (line.cost - line.amount)

class room(models.Model):
    _name = "room.record"
    name = fields.Char(string="Room name", required=True)
    responsible = fields.Many2one("employee.record", required=True, string="Responsible Room")
    size = fields.Selection(selection=[('bigger','Bigger'),('medium','Medium'),('small','Small')], default='bigger', string="Room size", required=True)
    type = fields.Selection(selection=[('meeting room','Meeting Room'),('lap room','Lap Room'),('lecture room','Lecture Room')], default='meeting room', string="Room Type", required=True)
    seats = fields.Float(string="Number of Seats", required=True)
    seats_number = fields.Float(string="Seats Maximum", required=True)

class employee(models.Model):
    _name = "employee.record"
    name = fields.Char(string="Employee name", required=True)
    department = fields.Many2one("hr.department", string="Department", required=True)
    position = fields.Many2one("hr.job", string="Job position", required=True)
    phone = fields.Char(string="Mobile", required=True)
    email = fields.Char(string="Email", required=True)
    gender = fields.Selection(selection=[('male','Male'),('female','Female')], default='male', string="Gender")
    salary = fields.Float(string="Salary", required=True)
    user_id = fields.Many2one("res.users", string="Related user")

class pay(models.Model):
    _name = "pay.record"
    _rec_name = 'code'
    code = fields.Char(default=lambda self: ('Serial_Number'), readonly=True)
    admin = fields.Many2one("res.users", string="Admin name", required=True, default=lambda self:self.env.user)
    date = fields.Date(string="Date", required=True, default=fields.Date.today())
    # student_ids = fields.One2many("student.record","pay_ids",string="Select Trained")
    payment_ids = fields.One2many("payment.record", "pay_ids", string="Select Trained")
    line_pay_total = fields.Float(string="Sub Total", compute="_compute_total", store=True)
    line_pay_hours = fields.Float(string="Number of hours", compute="_compute_total", store=True)
    line_pay_hours_price = fields.Float(string="Hours Price", compute="_compute_total", store=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('approve','Approve'),
    ], string='Status', readonly=True, default='draft')

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('code', ('Serial_Number')) == ('Serial_Number'):
            vals['code'] = self.env['ir.sequence'].next_by_code('pay.record') or ('Serial_Number')
            dlat = super(pay, self).create(vals)
            # dlat = super(student, self).create(vals)
            # dlat = super(lounge, self).create(vals)
            return dlat


    @api.depends('payment_ids')
    def _compute_total(self):
        for pay in self:
            line_pay_hours = line_pay_hours_price = 0.0
            for line in pay.payment_ids:
                line_pay_hours += line.pay_hours
                line_pay_hours_price += line.pay_hours_price
                pay.update({
                    'line_pay_hours': line_pay_hours,
                    'line_pay_hours_price': line_pay_hours_price,
                    'line_pay_total': line_pay_hours * line_pay_hours_price,
                })

    def action_view_payment(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        default_journal = self.env['account.journal'].search([('type', '=', 'sale')],
                                                             limit=1)
        print(default_journal, " journal")
        default_account = self.env['account.journal'].search([('type', '=', 'sale')],
                                                             limit=1).default_debit_account_id or False

        payment_ids = []
        for line in self.payment_ids:
            payment_ids.append((0, 0, {
                'price_unit' : line.pay_total,
                'quantity' : 1,
                'name' : line.pay_course,
                'account_id' : default_account.id if default_account else False,
            }))
            print(payment_ids)
            result['context'] = {
                'default_type' : 'out_invoice',
                'default_line_ids' : payment_ids,
            }
            view_id = self.env.ref('account.view_move_form', False)
            form_view = [(view_id and view_id.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            result['name'] = self.code
            result['context']['default_invoice_origin'] = self.code
            result['context']['default_ref'] = self.code
            if default_journal:
                result['context']['journal_id'] = default_journal.id or False
                result['context']['default_journal_id'] = default_journal.id or False
            return result

class payment(models.Model):
    _name = "payment.record"
    pay_name = fields.Many2one("trained.record", string="Trained name", required=True)
    pay_course = fields.Many2one("course.record", string="Course name", required=True)
    pay_total = fields.Float(string="Sub Total", required=True, compute="_compute_total")
    pay_hours = fields.Float(string="Course hours", required=True)
    pay_hours_price = fields.Float(string="Hours price", required=True)
    pay_ids = fields.Many2one("pay.record")

    @api.depends('pay_hours','pay_hours_price')
    def _compute_total(self):
        for line in self:
            line.pay_total = (line.pay_hours * line.pay_hours_price)

    @api.onchange('pay_course')
    def set_pay_name(self):
        for rec in self:
            if rec.pay_course:
                rec.pay_name = rec.pay_course.traineds

    @api.onchange('pay_course')
    def set_pay_hours(self):
        for rec in self:
            if rec.pay_course:
                rec.pay_hours = rec.pay_course.hours

    @api.onchange('pay_course')
    def set_pay_hours_price(self):
        for rec in self:
            if rec.pay_course:
                rec.pay_hours_price = rec.pay_course.hours_price




