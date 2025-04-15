from odoo import models, fields

class HMSDoctors(models.Model):
    _name = 'hms.doctors'
    _description = 'Hospital Doctors'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    image = fields.Binary(string='Image')