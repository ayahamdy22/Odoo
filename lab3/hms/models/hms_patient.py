from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class HMSPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread']  # For log history

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    birth_date = fields.Date(string='Birth Date')
    email = fields.Char(string='Email', required=True, index=True)
    history = fields.Html(string='History')
    cr_ratio = fields.Float(string='CR Ratio')
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], string='Blood Type')
    pcr = fields.Boolean(string='PCR')
    image = fields.Binary(string='Image')
    address = fields.Text(string='Address')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    department_id = fields.Many2one('hms.department', string='Department', tracking=True)
    doctor_ids = fields.Many2many('hms.doctors', string='Doctors', tracking=True)
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ], string='State', default='undetermined', tracking=True)
    department_capacity = fields.Integer(string='Department Capacity', related='department_id.capacity', readonly=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True)

    # Compute name field from first_name and last_name
    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for patient in self:
            patient.name = (patient.first_name or '') + ' ' + (patient.last_name or '')

    # Compute age based on birth_date
    @api.depends('birth_date')
    def _compute_age(self):
        for patient in self:
            if patient.birth_date:
                today = date.today()
                birth_date = fields.Date.from_string(patient.birth_date)
                patient.age = today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day)
                )
            else:
                patient.age = 0

    # Constraint to ensure unique email
    _sql_constraints = [
        ('unique_patient_email', 'UNIQUE(email)', 'Email must be unique across all patients.')
    ]

    # Validate email format
    @api.constrains('email')
    def _check_email(self):
        for patient in self:
            if patient.email and '@' not in patient.email:
                raise ValidationError(_("The email address must contain an '@' symbol."))

    @api.onchange('age')
    def _onchange_age(self):
        if self.age and self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': 'PCR Checked',
                    'message': 'PCR has been automatically checked as age is below 30.',
                }
            }
        elif self.age and self.age >= 50:
            self.history = False

    @api.onchange('pcr')
    def _onchange_pcr(self):
        if self.pcr and not self.cr_ratio:
            return {
                'warning': {
                    'title': 'CR Ratio Required',
                    'message': 'CR Ratio is mandatory when PCR is checked.',
                }
            }

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id and not self.department_id.is_opened:
            return {
                'warning': {
                    'title': 'Closed Department',
                    'message': 'The selected department is closed. Please choose an open department.',
                }
            }

    @api.model
    def create(self, vals):
        record = super(HMSPatient, self).create(vals)
        if 'state' in vals:
            record._log_state_change(vals.get('state'))
        return record

    def write(self, vals):
        res = super(HMSPatient, self).write(vals)
        if 'state' in vals:
            self._log_state_change(vals.get('state'))
        return res

    def _log_state_change(self, new_state):
        self.message_post(body=f"State changed to {new_state.capitalize()}")