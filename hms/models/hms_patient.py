from odoo import models, fields, api, _

class HMSPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread']  # For log history

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    birth_date = fields.Date(string='Birth Date')
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
    age = fields.Integer(string='Age')
    
    department_id = fields.Many2one('hms.department', string='Department', tracking=True)
    doctor_ids = fields.Many2many('hms.doctors', string='Doctors', tracking=True)
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ], string='State', default='undetermined', tracking=True)
    department_capacity = fields.Integer(string='Department Capacity', related='department_id.capacity', readonly=True)

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