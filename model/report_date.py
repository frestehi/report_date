# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2015 Peru Software Factory. (<http://peruswfactory.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models, api

import calendar

class ReportDate(models.Model):
    '''
    This class create model of Report Date
    '''
    _name = 'crm.reportdate' 

    name = fields.Char(string='Report Name', required=True)
    start_date = fields.Datetime(related ='create_date', string="Create On", readonly=True)
    report_of_photo_ids = fields.One2many('crm.photo', 'report_date_id', readonly=True)
    note = fields.Text(string='Note')
    state = fields.Selection([('draft', 'Draft'),
                                ('confirmed', 'Confirmed'),
                                ('locked', 'Locked'),
                                ('unlocked', 'Unlocked'),
                                ], default='draft', readonly=True)


    @api.multi
    def button_confirm(self):
        
        leads = self.env['crm.lead'].search([('date_deadline', '>=', self.start_date),
                                             ('stage_id.name', 'not in',['Lost','Descarted'] ),
                                             ('state_forecast', '!=','none' )])
        for lead in leads:
            self.env['crm.photo'].create({
            'lead_id': lead.id,
            'report_date_id':self.id,
            'name':  lead.name,
            'planned_revenue': lead.planned_revenue,
            'date_deadline': lead.date_deadline,
            'user_id': lead.user_id.id,
            'partner_id': lead.partner_id.id,
            'section_id': lead.section_id.id,
            'stage_id': lead.stage_id.id,
            'state_forecast': lead.state_forecast
        })
        month_report = self.start_date[5:7]

        #cmrAjustMonth
        dic_month = (('01', "January"),
                                ('02', "Febrary"),
                                ('03', "March"),
                                ('04', "April"),
                                ('05', "May"),
                                ('06', "June"),
                                ('07', "July"),
                                ('08', "August"),
                                ('09', "September"),
                                ('10', "Octuber") ,
                                ('11', "November"),
                                ('12', "December"),
                                )
        sales_teams = self.env['crm.case.section'].search([('active','=', True)])

        for month in dic_month:
            if month[0] >= month_report:
                ajust_month_obj = self.env['crm.ajust.month'].create({
                                                    'name' : self._get_name_crm_ajust(month[1]),
                                                    'report_id' :self.id,
                                                    'month' : month[0]
                                                    })
                
                for sale_team in sales_teams:                    
                    self.env['crm.ajust.month.line'].create({
                                                'name': ajust_month_obj.name + sale_team.name,
                                                'ajust_month_id' :ajust_month_obj.id,  
                                                'director' : sale_team.user_id.id,
                                                'amount_forecast_month' :self._get_amount(sale_team.id, month[0],self.start_date ),
                                                'amount_ajust':self._get_amount(sale_team.id, month[0],self.start_date ),
                                                'color':1
                                                    })

           
    def _get_name_crm_ajust(self, month):
        return  self.name + month
    
    def _get_amount(self, sale_team_id,month, start_date ):
        
        if month == start_date[5:7]:
            day = start_date[8:10]
        else:
            day = '01'
        year = start_date[0:4]
        date_start = year +'-'+ month+'-' +day
        day=calendar.monthrange(int(year), int(month))[1]
        
        date_end = year +'-'+ month+'-' +str(day)

        photos = self.env['crm.photo'].search([('section_id','=',sale_team_id),('date_deadline','>=',date_start),('date_deadline','<=',date_end)])
        amount_forecast_month = 0.00
        for photo in photos:
            amount_forecast_month += photo.planned_revenue
        return amount_forecast_month

class CRMPhoto(models.Model):
    '''
    This class create model of CRM Photo
    '''
    _name = 'crm.photo' 
    lead_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type', '=', 'opportunity')]")
    report_date_id = fields.Many2one('crm.reportdate', 'Report')
    name = fields.Char('Foto de Oportunidad')
    planned_revenue = fields.Float('Expected Revenue', track_visibility='always')
    date_deadline = fields.Date('Expected Closing', help="Estimate of the date on which the opportunity will be won.")
    user_id = fields.Many2one('res.users', 'Salesperson', select=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', ondelete='set null', string='Cliente')
    section_id = fields.Many2one('crm.case.section', 'Sale Team')
    stage_id = fields.Many2one('crm.case.stage','Crm Stage')
    state_forecast = fields.Selection((('committed', 'Committed'),('included - not committed','Included - not committed'),('none','None')),'Forecast State')
    



class cmrAjustMonth(models.Model):
        _name = 'crm.ajust.month'

        name = fields.Char("Ajust by Month")
        report_id = fields.Many2one('crm.reportdate', string = "Report", required=True)
        month =  fields.Selection([('01', "January"),
                                ('02', "Febrary"),
                                ('03', "March"),
                                ('04', "April"),
                                ('05', "May"),
                                ('06', "June"),
                                ('07', "July"),
                                ('08', "August"),
                                ('09', "September"),
                                ('10', "Octuber") ,
                                ('11', "November"),
                                ('12', "December"),
                                ], default='01', readonly=True)
        line_ids = fields.One2many('crm.ajust.month.line', 'ajust_month_id', string="Ajust Line")

class cmrAjustMonthLine(models.Model):
        _name = 'crm.ajust.month.line'

        name = fields.Char("Ajust by Motnh")
        ajust_month_id = fields.Many2one('crm.ajust.month')  
        director = fields.Many2one('res.users') 
        amount_forecast_month = fields.Float(string ="Forecast mounth", store = True, readonly=True)
        amount_ajust = fields.Float(string ="Ajust")
        amount_ajust_child = fields.Float(string ="Ajust")
        #parent_id = fields.Many2one('crm.ajust.month.line', 'Parent Ajust', select=True)
        #child_ids = fields.One2many('crm.ajust.month.line', 'parent_id', 'Child Ajust')
        color = fields.Integer()

        def action_ajust(self, cr, uid, id, value, context=None):
            return self.write(cr, uid, [id], {'amount_ajust': round(float(value))}, context=context)




