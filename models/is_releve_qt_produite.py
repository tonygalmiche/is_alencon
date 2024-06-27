# -*- coding: utf-8 -*-
from odoo import models,fields,api
from datetime import datetime, timedelta
import pytz
import csv
import base64


class is_releve_qt_produite(models.Model):
    _name='is.releve.qt.produite'
    _inherit=['mail.thread']
    _description="Relevé des quantités produites"
    _order='name desc'


    name        = fields.Char('N°relevé', readonly=True, tracking=True)
    date_debut  = fields.Date("Date de début"          ,required=True, tracking=True)
    date_fin    = fields.Date("Date de fin"            ,required=True, tracking=True)
    heure_debut = fields.Float("Heure de début(>=) (HH:MM)",required=True, tracking=True)
    heure_fin   = fields.Float("Heure de fin (<) (HH:MM)"  ,required=True, tracking=True)
    state       = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('valide'   , 'Validé'),
    ], "Etat", default="brouillon", tracking=True)
    ligne_ids = fields.One2many('is.releve.qt.produite.ligne', 'releve_id', 'Lignes', tracking=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('is.releve.qt.produite')
        return super().create(vals_list)


    def creer_lignes_action(self):
        cr=self._cr
        for obj in self:
            obj.ligne_ids.unlink()
            #** Rechecher des états à inclure *********************************
            filtre=[('couleur','=', 'vert')]
            lines = self.env['is.etat.presse'].search(filtre, order="name5x5")
            etats_ids=[]
            for line in lines:
                etats_ids.append(str(line.id))
            etats_ids = ','.join(etats_ids)
            #******************************************************************
            SQL="""
                SELECT  
                    ie.ordre,
                    io.name,
                    io.id of_id,
                    io.moule,
                    io.code_article,
                    io.designation,
                    io.presse_id,
                    io.qt,
                    sum(iod.qt_bonne) qt_bonne,
                    sum(iod.qt_rebut) qt_rebut
                FROM is_of io join is_of_declaration iod on io.id=iod.of_id
                              join is_equipement      ie on io.presse_id=ie.id
                WHERE 
                    iod.name>=%s 
                    and iod.name<%s 
                    -- and io.id=1340
                GROUP BY
                    ie.ordre,
                    io.name,
                    io.id,
                    io.moule,
                    io.code_article,
                    io.designation,
                    io.presse_id,
                    io.qt
                ORDER BY ie.ordre,io.name
            """
            def get_date_utc(ladate,heure):
                HH = str(int(heure)).zfill(2)
                MM = str(round((heure - int(heure))*60)).zfill(2)
                date_str = '%s %s:%s:00'%(ladate,HH,MM)
                date_locale = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                offset = int(pytz.timezone('Europe/Paris').localize(date_locale).utcoffset().total_seconds()/3600)
                date_utc = date_locale - timedelta(hours=offset)
                return date_utc
            date_debut = get_date_utc(obj.date_debut, obj.heure_debut)
            date_fin   = get_date_utc(obj.date_fin  , obj.heure_fin)
            cr.execute(SQL,[date_debut,date_fin])
            rows = cr.dictfetchall()
            ct=1
            for row in rows:
                #** Recherche des cumuls **************************************
                of_id = row['of_id']
                SQL="""
                    SELECT sum(qt_bonne) qt_bonne, sum(qt_rebut) qt_rebut
                    FROM is_of_declaration
                    WHERE of_id=%s and name<%s
                """
                cr.execute(SQL,[of_id,date_fin])
                rows2 = cr.dictfetchall()
                cumul_qt_bonne = cumul_qt_rebut = 0
                for row2 in rows2:
                    cumul_qt_bonne = row2['qt_bonne']
                    cumul_qt_rebut = row2['qt_rebut']
                #**************************************************************

                #** Recherche tps production effective ************************
                duree_effective_totale = 0
                SQL="""
                    select 
                        ipa.date_heure heure_debut,
                        (ipa.date_heure + (interval '1 hour' * ipa.tps_arret)) heure_fin,
                        ipa.tps_arret
                    from is_presse_arret ipa  join is_presse_arret_of_rel rel on ipa.id=rel.is_of_id
                    where 
                        date_heure>=%s and date_heure<%s and rel.is_presse_arret_id=%s
                        and ipa.type_arret_id in ("""+etats_ids+""") 
                    order by ipa.id desc
                """
                cr.execute(SQL,[date_debut,date_fin,of_id])
                rows2 = cr.dictfetchall()
                ct=duree_effective_totale=0
                for row2 in rows2:
                    duree = (row2['heure_fin'] -  row2['heure_debut'])
                    duree_effective = duree
                    if row2['heure_debut']<date_debut:
                        duree_effective = row2['heure_fin'] - date_debut
                    if row2['heure_fin']>date_fin:
                        duree_effective = date_fin-row2['heure_debut']
                    if row2['tps_arret']==0 and ct==0:
                        duree_effective = date_fin - row2['heure_debut']
                    duree_effective = round(duree_effective.total_seconds()/3600,2)
                    duree_effective_totale += duree_effective
                    ct+=1
                #**************************************************************
                vals={
                    'releve_id'     : obj.id,
                    'sequence'      : ct,
                    'equipement_id' : row['presse_id'],
                    'of_id'         : row['of_id'],
                    'moule'         : row['moule'],
                    'code_article'  : row['code_article'],
                    'designation'   : row['designation'],
                    'qt_lancement'  : row['qt'],
                    'qt_bonne'      : row['qt_bonne'],
                    'qt_rebut'      : row['qt_rebut'],
                    'cumul_qt_bonne': cumul_qt_bonne,
                    'cumul_qt_rebut': cumul_qt_rebut,
                    'tps_production': round(duree_effective_totale,2),
                    'date_debut'    : obj.date_debut,
                    'heure_debut'   : obj.heure_debut,
                    'date_fin'      : obj.date_fin,
                    'heure_fin'     : obj.heure_fin,
                }
                self.env['is.releve.qt.produite.ligne'].create(vals)
                ct+=1
            return obj.voir_lignes_action()
    

    def voir_lignes_action(self):
        for obj in self:
            return {
                'name': 'Lignes',
                'view_mode': 'tree',
                'res_model': 'is.releve.qt.produite.ligne',
                'domain': [
                    ('releve_id','=',obj.id),
                ],
                'type': 'ir.actions.act_window',
                'limit': 2000,
            }


    def vers_valide_action(self):
        "Création du fichier d'exportation et validation de la fiche pour bloquer les modifications"
        for obj in self:
            filename="releve-qt-produite-%s.csv"%obj.name         
            with open("/tmp/%s"%filename, 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter='\t') #,quotechar='|', quoting=csv.QUOTE_MINIMAL)
                val=[
                    "Date de début",
                    "Heure de début",
                    "Date de fin",
                    "Heure de fin",
                    "Equipement",
                    "LCT",
                    "N°Moule",
                    "Référence pièce",
                    "Désignation",
                    "QT du LCT",
                    "QT bonnes",
                    "Qt rebuts",
                    "Cumul Qt bonnes",
                    "Cumul Qt rebuts",
                    "Tps de production effective",
                ]
                spamwriter.writerow(val)
                for line in obj.ligne_ids:
                    val=[
                        line.date_debut,
                        line.heure_debut,
                        line.date_fin,
                        line.heure_fin,
                        line.equipement_id.numero_equipement,
                        line.of_id.name,
                        line.moule,
                        line.code_article,
                        line.designation,
                        line.qt_lancement,
                        line.qt_bonne,
                        line.qt_rebut,
                        line.cumul_qt_bonne,
                        line.cumul_qt_rebut,
                        line.tps_production,
                    ]
                    spamwriter.writerow(val)

            # ** Creation ou modification de la pièce jointe ******************
            attachment_obj = self.env['ir.attachment']
            model=self._name
            attachments = attachment_obj.search([('res_model','=',model),('res_id','=',obj.id),('name','=',filename)])
            datas = open("/tmp/%s"%filename,'rb').read()
            vals = {
                'name':        filename,
                'type':        'binary',
                'res_model':   model,
                'res_id':      obj.id,
                'datas':       base64.b64encode(datas),
            }
            if attachments:
                for attachment in attachments:
                    attachment.write(vals)
            else:
                attachment = attachment_obj.create(vals)
            #******************************************************************
            obj.state="valide"


class is_releve_qt_produite_ligne(models.Model):
    _name='is.releve.qt.produite.ligne'
    _description="Lignes des relevé des quantités produites"
    _order='sequence,id'

    releve_id         = fields.Many2one('is.releve.qt.produite', 'Relevé', required=True, ondelete='cascade')
    state             = fields.Selection(related="releve_id.state")
    sequence          = fields.Integer("Ordre")
    equipement_id     = fields.Many2one('is.equipement', "Equipement", required=True)
    of_id             = fields.Many2one('is.of', "LCT"               , required=True)
    moule             = fields.Char("Moule")
    code_article      = fields.Char("Code article")
    designation       = fields.Char("Désignation")
    qt_lancement      = fields.Integer("Qt du LCT")
    qt_bonne          = fields.Integer("Qt bonnes")
    qt_rebut          = fields.Integer("Qt rebuts")
    cumul_qt_bonne    = fields.Integer("Cumul Qt bonnes")
    cumul_qt_rebut    = fields.Integer("Cumul Qt rebuts")

    date_debut        = fields.Date("Date début")
    heure_debut       = fields.Float("Heure début")
    date_fin          = fields.Date("Date fin")
    heure_fin         = fields.Float("Heure fin")
    tps_production    = fields.Float("Tps production", help="Tps de production effective")
    alerte            = fields.Text("Alerte", compute='_compute', store=True, readonly=True)


    @api.depends('qt_lancement','cumul_qt_bonne')
    def _compute(self):
        for obj in self:
            alerte = False
            if obj.cumul_qt_bonne>obj.qt_lancement:
                alerte="Qt bonne > Qt Lct"
            obj.alerte=alerte


    def is_alerte_action(self):
        return