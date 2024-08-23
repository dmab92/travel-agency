# models/sales_dashboard.py
from odoo import models, fields, api

class SalesDashboard(models.Model):
    _name = 'sales.dashboard'
    _description = 'Sales Dashboard'

    name = fields.Char(string='Name')
    total_sales = fields.Float(string='Total Sales')
    sales_count = fields.Integer(string='Sales Count')
