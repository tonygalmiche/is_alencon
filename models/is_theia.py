# -*- coding: utf-8 -*-
from odoo import models,fields,api,tools
import random

class is_equipement(models.Model):
    _inherit = 'is.equipement'


    def get_parc_presse(self):
        print('get_parc_presse', self)


        lines = self.env['is.equipement'].search([('ordre','>',0)], order="ordre,numero_equipement")

        equipements=[]
        for line in lines:
            print(line.ordre, line.numero_equipement,line.couleur)
            key="%s-%s"%(str(line.ordre).zfill(5),line.numero_equipement)

            cycle  = str(int(100*random.random()))+"%"
            fct    = str(int(100*random.random()))+"%"
            rebut  = str(int(100*random.random()))+"%"
            avance = str(int(100*random.random()))

            equipements.append({
                'key'              : key,
                'ordre'            : line.ordre,
                'designation'      : line.designation,
                'numero_equipement': line.numero_equipement,
                'etat'             : line.etat_presse_id.name5x5,
                'etat_style'       : 'background-color: %s'%line.couleur,
                'cycle'            : cycle,
                'fct'              : fct,
                'rebut'            : rebut,
                'avance'           : avance,
            })


        res={}
        res['equipements'] = equipements
        return res






    # def get_analyse_cbn(self):
    #     mem_product_id = product_id
    #     cr = self._cr
    #     debut=datetime.now()
    #     _logger.info('Début')




    #     #** Résultat **********************************************************
    #     debut2=datetime.now()
    #     result1 = self._get_FS_SA(filtre)
    #     result2 = self._get_CF_CP(filtre)
    #     result3 = self._get_FL(filtre)
    #     result4 = self._get_FM(filtre)
    #     result5 = self._get_SF(filtre)
    #     result = result1+result2+result3+result4+result5
    #     if valorisation:
    #         result+=self._get_stock(filtre)
    #     result = result1+result2+result3+result4+result5
    #     res={}
    #     for row in result:
    #         product_id = row["product_id"]
    #         code    = row["code_pg"]
    #         if type_rapport=='Achat':
    #             code_fournisseur=Fournisseurs.get(product_id,"0000")
    #             key="%s/%s"%(code_fournisseur,code)
    #             k = code_fournisseur+'/'+str(product_id)
    #             t=TypeCde.get(k)
    #             if t:
    #                 Code = "%s / %s / %s (%s)"%(code_fournisseur,code,row["moule"],t)
    #             else:
    #                 Code = "%s / %s / %s "%(code_fournisseur,code,row["moule"])
    #         else:
    #             key="%s/%s"%(row["moule"],code)
    #             Code = "%s / %s"%(row["moule"],code)
    #         cout=0
    #         if valorisation=="Oui":
    #             cout = Couts.get(product_id,0)
    #             Code = "%s (%s)"%(Code, cout)

    #         if key not in res:
    #             product_id = row["product_id"]
    #             product = self.env['product.product'].browse(product_id)
    #             product_tmpl = product.product_tmpl_id
    #             if type_rapport=='Achat':
    #                 Delai=Delai_Fournisseurs.get(product_id,0)
    #             else:
    #                 Delai=row["produce_delay"]
    #             res[key] = {
    #                 "key"        : key,
    #                 "Code"       : Code,
    #                 "product_id" : product_id,
    #                 "product_tmpl_id": product_tmpl.id,
    #                 "code_pg"    : row["code_pg"],
    #                 "designation": row["designation"],
    #                 "cout"       : cout,
    #                 "lot_mini"   : row["lot_mini"],
    #                 "multiple"   : row["multiple"],
    #                 "StockSecu"  : row["is_stock_secu"],
    #                 "Delai"      : Delai,
    #                 "StockA"     : int(StocksA.get(product_id,0)),
    #                 "StockQ"     : int(StocksQ.get(product_id,0)),
    #                 "typeod"     : {},
    #             }

    #             #Ajout des colonnes pour le stock *****************************
    #             res[key]["typeod"]["90-Stock"]={
    #                 "key"        : "90-Stock",
    #                 "typeod"     : "90-Stock",
    #                 "name_typeod": "Stock",
    #                 "cols"  : {}
    #             }
    #             for d in TabSemaines:
    #                 res[key]["typeod"]["90-Stock"]["cols"][d]={
    #                     "key"     : d,
    #                     "qt_signe": 0,
    #                     "qt_txt"  : "",
    #                     "od"       : []
    #                 }
    #             #**************************************************************

    #             #Ajout des colonnes pour le stock valorisé ********************
    #             if valorisation=="Oui":
    #                 lig="92-Stock Valorisé"
    #                 res[key]["typeod"][lig]={
    #                     "key"        : lig,
    #                     "typeod"     : lig,
    #                     "name_typeod": "Valorisation",
    #                     "cols"  : {}
    #                 }
    #                 for d in TabSemaines:
    #                     res[key]["typeod"][lig]["cols"][d]={
    #                         "key"     : d,
    #                         "qt": 0,
    #                         "qt_signe": 0,
    #                         "qt_txt"  : "",
    #                         "od"       : []
    #                     }
    #             #**************************************************************

    #         typeod = row["typeod"]
    #         key2   = self._get_name_typeod(typeod)
    #         if key2 not in res[key]["typeod"]:
    #             res[key]["typeod"][key2] = {
    #                 "key"        : key2,
    #                 "typeod"     : row["typeod"],
    #                 "name_typeod": key2[3:],
    #                 "cols"  : {}
    #             }
    #             for d in TabSemaines:
    #                 res[key]["typeod"][key2]["cols"][d]={
    #                     "key"   : d,
    #                     "qt"    : 0,
    #                     "qttxt" : "",
    #                     "od"    : {},
    #                     #"ids"   : [],
    #                 }
    #         if calage=='' or calage=='Date de fin':
    #             DateLundi=self.datelundi(row["date_fin"], TabSemaines)
    #         else:
    #             DateLundi=self.datelundi(row["date_debut"], TabSemaines)
    #         if DateLundi:
    #             if DateLundi in TabSemaines:
    #                 v=round(row["qt"],6)
    #                 if row["typeod"]=='FL' and v<0:
    #                     v=0
    #                 qt = res[key]["typeod"][key2]["cols"][DateLundi]["qt"]+v
    #                 #qt = res[key]["typeod"][key2]["cols"][DateLundi]["qt"]+round(row["qt"],6)
    #                 color_qt = self._get_color_qt(key2,qt)
    #                 qt_signe = qt * self._get_sens(typeod)
    #                 qt_txt=""
    #                 if qt>0:
    #                     qt_txt = int(qt_signe)

    #                 #if row["numod"] not in res[key]["typeod"][key2]["cols"][DateLundi]["ids"]:
    #                 #    res[key]["typeod"][key2]["cols"][DateLundi]["ids"].append(row["numod"])

    #                 #** Afficher l'icon trash si un seul OD et du type accecpté *********
    #                 trash=False
    #                 if qt_txt!="" and key2[3:] in ['FS','SA']:
    #                     trash=True
    #                 #********************************************************************
    #                 numod = row["numod"]
    #                 v={
    #                     "numod": numod,
    #                     "name" : row["name"],
    #                     "qt"   : round(row["qt"],4),
    #                     "trash": trash,
    #                 }
    #                 res[key]["typeod"][key2]["cols"][DateLundi]["od"][numod] = v


    #                 #if row["name"] not in res[key]["typeod"][key2]["cols"][DateLundi]["od"]:
    #                 #    res[key]["typeod"][key2]["cols"][DateLundi]["od"].append(row["name"])
    #                 #od_txt = ", ".join(res[key]["typeod"][key2]["cols"][DateLundi]["od"])

    #                 #** Afficher l'icon trash si un seul OD et du type accecpté *********
    #                 # trash=False
    #                 # if qt_txt!="":
    #                 #     if len(res[key]["typeod"][key2]["cols"][DateLundi]["od"])==1:
    #                 #         if key2[3:] in ['FL','FS','SA']:
    #                 #             trash=True
    #                 # #********************************************************************

    #                 res[key]["typeod"][key2]["cols"][DateLundi].update({
    #                     "qt"      : qt,
    #                     "color_qt": color_qt,
    #                     "qt_txt"  : qt_txt,
    #                     "qt_signe": qt_signe,
    #                     #"od_txt"  : od_txt,
    #                     #"trash"   : trash,
    #                 })
    #         #res[key]["typeod"][key2]["colslist"] = list(res[key]["typeod"][key2]["cols"].values())
    #     _logger.info("Résultat (durée=%.2fs)"%(datetime.now()-debut2).total_seconds())
    #     #**********************************************************************

    #     #Convertir un dictionnaire en list (pour owl) avec un tri sur les clés => Voir pour optimiser le temps de traitement
    #     debut2=datetime.now()
    #     for key in res:
    #         res[key]["typeodlist"]=[]
    #         for line in dict(sorted(res[key]["typeod"].items())):
    #             res[key]["typeodlist"].append(res[key]["typeod"][line])
    #         res[key]["rowspan"]    = len(res[key]["typeodlist"])
    #     _logger.info("Convertir un dictionnaire en list (durée=%.2fs)"%(datetime.now()-debut2).total_seconds())
    #     #**********************************************************************

    #     #** Calcul du total des besoins par date ******************************
    #     debut2=datetime.now()
    #     totaux={}
    #     for p in res:
    #         totaux[p]={}
    #         for t in res[p]["typeod"]:
    #             if t not in["90-Stock","92-Stock Valorisé"]:
    #                 typeod = res[p]["typeod"][t]["typeod"]
    #                 for c in TabSemaines:
    #                     qt=res[p]["typeod"][t]["cols"][c]["qt"]
    #                     qt_signe = qt * self._get_sens(typeod)
    #                     if c not in totaux[p]:
    #                         totaux[p][c]=0
    #                     totaux[p][c]+=qt_signe
    #     #print(json.dumps(totaux, indent = 4))
    #     _logger.info("Calcul du total des besoins par date (durée=%.2fs)"%(datetime.now()-debut2).total_seconds())
    #     #**********************************************************************

    #     #** Calcul du stock cumulé par date ***********************************
    #     debut2=datetime.now()
    #     for p in totaux:
    #         ct=0
    #         cumul=0
    #         for c in TabSemaines:
    #             if ct==0:
    #                 if valorisation=="Oui":
    #                     cumul = res[p]["StockA"]+res[p]["StockQ"]
    #                 else:
    #                     cumul = res[p]["StockA"]-res[p]["StockSecu"]
    #             cumul+=totaux[p][c]

    #             val = cumul*res[p]["cout"]
    #             if val<0:
    #                 val=0

    #             color="Gray"
    #             if cumul<0:
    #                 color='Red'
    #             res[p]["typeod"]["90-Stock"]["cols"][c]["qt_signe"]=cumul
    #             res[p]["typeod"]["90-Stock"]["cols"][c]["color_qt"]=color
    #             res[p]["typeod"]["90-Stock"]["cols"][c]["qt_txt"] = int(res[p]["typeod"]["90-Stock"]["cols"][c]["qt_signe"])
    #             if valorisation=="Oui":
    #                 res[p]["typeod"]["92-Stock Valorisé"]["cols"][c]["qt_txt"] = int(val)

    #             ct+=1
    #         #res[p]["typeod"]["90-Stock"]["colslist"] = list(res[p]["typeod"]["90-Stock"]["cols"].values())
    #         #if valorisation=="Oui":
    #         #    res[p]["typeod"]["92-Stock Valorisé"]["colslist"] = list(res[p]["typeod"]["92-Stock Valorisé"]["cols"].values())
    #     _logger.info("Calcul du stock cumulé par date (durée=%.2fs)"%(datetime.now()-debut2).total_seconds())
    #     #**********************************************************************







    #     #** Ajout de la couleur des lignes ************************************
    #     debut2=datetime.now()
    #     sorted_dict = dict(sorted(res.items())) 
    #     trcolor=""
    #     for k in sorted_dict:
    #         if trcolor=="#ffffff":
    #             trcolor="#f2f3f4"
    #         else:
    #             trcolor="#ffffff"
    #         if mem_product_id:
    #             trcolor="#00FAA2"
    #         trstyle="background-color:%s"%(trcolor)
    #         sorted_dict[k]["trstyle"] = trstyle
    #     #lines = list(sorted_dict.values())
    #     _logger.info("Ajout de la couleur des lignes (durée=%.2fs)"%(datetime.now()-debut2).total_seconds())
    #     #**********************************************************************


    #     duree = datetime.now()-debut
    #     _logger.info("Fin (durée=%.2fs)"%(datetime.now()-debut).total_seconds())
    #     res={
    #         "titre"       : titre,
    #         "dict"        : sorted_dict,
    #       
    #     }
    #     return res