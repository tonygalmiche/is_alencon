# -*- coding: utf-8 -*-
from odoo import models,fields,api,tools
from datetime import datetime
from dateutil import tz
import random
import logging
_logger = logging.getLogger(__name__)



class is_equipement(models.Model):
    _inherit = 'is.equipement'


    def get_color_indicateur(self,indicateur,val):
        color="gray"
        company = self.env.user.company_id
        for line in company.is_indicateur_ids:
            if line.indicateur==indicateur and val>=line.limite:
                color = line.color
                break
        return color


    def get_afficher_indicateur(self,indicateur,etat_id):
        afficher=True
        company = self.env.user.company_id
        for line in company.is_affichage_indicateur_ids:
            if etat_id==line.etat_id:
                afficher = getattr(line, indicateur)
                break
        return afficher




    def get_parc_presse(self):
        cr = self._cr
        FRA = tz.gettz('Europe/Paris')
        now    = datetime.now()
        now_local = now.astimezone(tz=FRA)
        company = self.env.user.company_id

        #** Rechecher des états à exclure *************************************
        etats=(
            'ABSENCE CHARGE PLANNING',
            'ESSAI MÉTHODES',
            'PRÉPARATION POSTE',
            'CHANGEMENT MOULE',
            'CHANGEMENT VERSION',
            'MAINTENANCE PRÉVENTIVE MOULE N1',
            'MAINTENANCE PRÉVENTIVE MOULE N2',
            'MAINTENANCE PRÉVENTIVE PRESSE N1',
            'MAINTENANCE PRÉVENTIVE PRESSE N2',
            'MAINTENANCE PREVENTIVE TPM N1',
        )
        filtre=[('name5x5','in', etats)]
        lines = self.env['is.etat.presse'].search(filtre, order="name5x5")
        etats_ids=[]
        for line in lines:
            etats_ids.append(str(line.id))
        etats_ids = ','.join(etats_ids)
        #**********************************************************************

        filtre=[
            ('ordre','>',0),
            #('designation','like','85T'),
        ]
        lines = self.env['is.equipement'].search(filtre, order="ordre,numero_equipement",limit=300)
        equipements=[]
        for line in lines:
            filtre=[
                ('presse_id','=',line.id),
                ('heure_debut', '!=', False),
                ('heure_fin', '=', False),
            ]
            ofs = self.env['is.of'].search(filtre, order="name desc", limit=1)
            tx_avance = 0
            tx_cycle  = 0
            tx_rebut = 0
            tx_fct = 0
            qt_declaree = qt_rebut = 0
            nb_empreintes = of_cycle_gamme =  cadence_horaire = quantite_theorique_effective = duree_effective_totale = 0
            if len(ofs)>0:
                of = ofs[0]
                of_cycle_gamme = of.cycle_gamme
                nb_empreintes  = of.nb_empreintes
                if of.qt>0:
                    tx_avance = int(100 * of.qt_declaree / of.qt)
                cycle_gamme = of.nb_empreintes*of.cycle_gamme
                if cycle_gamme>0:
                    tx_cycle = int(100 * (1 - ((of.cycle_moyen - cycle_gamme)/cycle_gamme)))
                    if tx_cycle<0:
                        tx_cycle=0


                #** Durée effective *******************************************
                duree_effective_totale = 0
                SQL="""
                    select id,type_arret_id,date_heure,tps_arret , (date_heure + (interval '1 hour' * tps_arret)) heure_fin 
                    from is_presse_arret 
                    where 
                        presse_id=%s
                        and (date_heure + (interval '1 hour' * tps_arret))>='%s'
                        and type_arret_id not in (%s) 
                    order by id desc
                    -- limit 20;
                """%(line.id,of.heure_debut, etats_ids)
                cr.execute(SQL)
                result = cr.dictfetchall()
                ct=0
                for row in result:
                    duree = (row['heure_fin'] -  row['date_heure'])
                    duree_effective = duree
                    if row['date_heure']<of.heure_debut:
                        duree_effective = row['heure_fin'] - of.heure_debut
                    if row['tps_arret']==0 and ct==0:
                        duree_effective = now - row['date_heure']
                    duree_effective = round(duree_effective.total_seconds()/3600,2)
                    duree_effective_totale += duree_effective
                    msg='Durée effective : %s : %s : %s : %s : %s : %s : %s'%(str(ct).zfill(3),line.numero_equipement,of.name,row["id"],row['date_heure'],round(duree_effective,2),round(duree_effective_totale,2))
                    _logger.info(msg)
                    ct+=1
                duree_effective_totale = round(duree_effective_totale,2)
                #**************************************************************

                #** Taux de fonctionnement ************************************
                cadence_horaire =  round(3600 / of.cycle_gamme,2)
                quantite_theorique_effective = cadence_horaire * duree_effective_totale
                if quantite_theorique_effective>0:
                    tx_fct = int(100 * of.qt_declaree / quantite_theorique_effective)
                #**************************************************************

                msg="Résultat : %s:%s:duree_effective_total=%s:cadence_horaire=%s:quantite_theorique_effective=%s:tx_fct=%s"%(line.numero_equipement,of.name,duree_effective_totale,cadence_horaire,quantite_theorique_effective,tx_fct)
                _logger.info(msg)


                #** Taux de rebuts ********************************************
                if (of.qt_declaree + of.qt_rebut)>0:
                    qt_declaree = of.qt_declaree
                    qt_rebut    = of.qt_rebut
                    tx_rebut  = round(100 * qt_rebut / (qt_declaree + qt_rebut),1)
                #**************************************************************


            #** Couleurs des indicateurs **************************************
            color_tx_avance = self.get_color_indicateur('tx_avance', tx_avance)
            color_tx_cycle  = self.get_color_indicateur('tx_cycle' , tx_cycle)
            color_tx_fct    = self.get_color_indicateur('tx_fct'   , tx_fct)
            color_tx_rebut  = self.get_color_indicateur('tx_rebut' , tx_rebut)
            #******************************************************************

            #** Affichage des indicateurs *************************************
            afficher_tx_avance = afficher_tx_cycle = afficher_tx_fct = afficher_tx_rebut = False
            if len(ofs)>0:
                afficher_tx_avance = self.get_afficher_indicateur('tx_avance', line.etat_presse_id)
                afficher_tx_cycle  = self.get_afficher_indicateur('tx_cycle' , line.etat_presse_id)
                afficher_tx_fct    = self.get_afficher_indicateur('tx_fct'   , line.etat_presse_id)
                afficher_tx_rebut  = self.get_afficher_indicateur('tx_rebut' , line.etat_presse_id)
            #******************************************************************

            #** Résultats de la presse ****************************************
            key="%s-%s"%(str(line.ordre).zfill(5),line.numero_equipement)
            numero_equipement = line.numero_equipement.replace('MENG','').replace('MNB','')
            equipements.append({
                'key'              : key,
                'ordre'            : line.ordre,
                'designation'      : line.designation,
                'numero_equipement': numero_equipement,
                'etat'             : line.etat_presse_id.name5x5 or '',
                'etat_style'       : 'background-color: %s'%line.couleur,
                'qt_declaree'      : qt_declaree,
                'qt_rebut'         : qt_rebut,

                'nb_empreintes'               : nb_empreintes,
                'of_cycle_gamme'              : of_cycle_gamme,
                'cadence_horaire'             : round(cadence_horaire,2),
                'quantite_theorique_effective': round(quantite_theorique_effective,2),
                'duree_effective_totale'      : round(duree_effective_totale,2),

                # #** Taux de fonctionnement ************************************
                # #cadence_horaire =  round(of.nb_empreintes * 3600 / of.cycle_gamme,2)
                # cadence_horaire =  round(3600 / of.cycle_gamme,2)
                # quantite_theorique_effective = cadence_horaire * duree_effective_totale
                # if quantite_theorique_effective>0:
                #     tx_fct = int(100 * of.qt_declaree / quantite_theorique_effective)
                # #**************************************************************

                'tx_avance'        : tx_avance,
                'tx_cycle'         : tx_cycle,
                'tx_fct'           : tx_fct,
                'tx_rebut'         : tx_rebut,

                'style_tx_avance'  : 'color:black;background-color:%s; width:%s%%'%(color_tx_avance,tx_avance),
                'style_tx_cycle'   : 'color: %s'%color_tx_cycle,
                'style_tx_fct'     : 'color: %s'%color_tx_fct,
                'style_tx_rebut'   : 'color: %s'%color_tx_rebut,

                'afficher_tx_avance'        : afficher_tx_avance,
                'afficher_tx_cycle'         : afficher_tx_cycle,
                'afficher_tx_fct'           : afficher_tx_fct,
                'afficher_tx_rebut'         : afficher_tx_rebut,


            })
            #******************************************************************

        #** Taux de cycle PARC ************************************************
        cycles=[]
        for  equipement in equipements:
            if equipement['tx_cycle']>0 and equipement['afficher_tx_cycle']:
                cycles.append(equipement['tx_cycle'])
        tx_cycle_parc = 0
        if len(cycles)>0:
            for cycle in cycles:
                tx_cycle_parc +=cycle
            tx_cycle_parc = tx_cycle_parc / len(cycles)
        tx_cycle_parc = round(tx_cycle_parc)
        #***********************************************************************

        #** Taux de fonctionnement PARC ****************************************
        fcts=[]
        for  equipement in equipements:
            if equipement['tx_fct']>0 and equipement['afficher_tx_fct']:
                fcts.append(equipement['tx_fct'])
        tx_fct_parc = 0
        if len(fcts)>0:
            for fct in fcts:
                tx_fct_parc +=fct
            tx_fct_parc = tx_fct_parc / len(fcts)
        tx_fct_parc = round(tx_fct_parc)
        #***********************************************************************

        #** Taux de rebuts PARC ************************************************
        rebuts=[]
        total_rebut = total_declaree = tx_rebut_parc = 0
        for  equipement in equipements:
            if equipement['afficher_tx_rebut']:
                total_rebut    += equipement['qt_rebut']
                total_declaree += equipement['qt_declaree']
        if (total_declaree + total_rebut)>0:
            tx_rebut_parc  = round(company.is_coeff_tx_rebut_parc*100 * total_rebut / (total_declaree + total_rebut),1)
        #***********************************************************************

        #** Couleurs des indicateurs **************************************
        color_tx_cycle_parc = self.get_color_indicateur('tx_cycle_parc' , tx_cycle_parc)
        color_tx_fct_parc   = self.get_color_indicateur('tx_fct_parc'   , tx_fct_parc)
        color_tx_rebut_parc = self.get_color_indicateur('tx_rebut_parc' , tx_rebut_parc)
        #******************************************************************

        res={
            'equipements'  : equipements,
            'now_date'     : now_local.strftime("%d/%m/%Y"),
            'now_heure'    : now_local.strftime("%H:%M"),

            'tx_cycle_parc': tx_cycle_parc,
            'tx_fct_parc'  : tx_fct_parc,
            'tx_rebut_parc': tx_rebut_parc,

            'style_tx_cycle_parc'   : 'background-color: %s'%color_tx_cycle_parc,
            'style_tx_fct_parc'     : 'background-color: %s'%color_tx_fct_parc,
            'style_tx_rebut_parc'   : 'background-color: %s'%color_tx_rebut_parc,
        }
        return res

