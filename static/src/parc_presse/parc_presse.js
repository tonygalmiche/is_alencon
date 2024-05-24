/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";

const { Component, useSubEnv, useState, onWillStart,onMounted,onWillUnmount } = owl;


console.log("## TEST 1 ##");

class ParcPresse extends Component {
    setup() {
        this.user_id = useService("user").context.uid;
        this.action  = useService("action");
        this.orm     = useService("orm");
        this.state   = useState({
            'equipements': {},
        });
        this._interval=null;

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
        this.display = {
            controlPanel: { "top-right": false, "bottom-right": false },
        };
        onWillStart(async () => {


            console.log('onWillStart');

            this.getParcPresse();
        });

        onMounted(() => {
            console.log('onMounted',this._interval);
            //Rafraichissement toutes les 60s *********************************
            if (!this._interval) {
                this._interval = setInterval(() => {
                    if (this._interval){
                        console.log('setInterval',Date.now(),this._interval);
                        this.getParcPresse();
                    }
                }, 1000 * 60);
            }
            //***************************************************************** */
        });
        onWillUnmount(() => {
            console.log('onWillUnmount',this._interval);
            //if (this._updateTimestampsInterval) {
            clearInterval(this._interval);
            this._interval=null;
            //}
        });
    } 

    OKclick(ev) {
        this.getParcPresse(true);
    }

 

    async getParcPresse(ok=false){
        var res = await this.orm.call("is.equipement", 'get_parc_presse', [false]);
        //console.log('getParcPresse : res=',res);
        this.state.equipements = res.equipements;
        this.state.taux_cycle  = res.taux_cycle;
        this.state.taux_fct    = res.taux_fct;
        this.state.taux_rebut  = res.taux_rebut;
        this.state.now_date    = res.now_date;
        this.state.now_heure   = res.now_heure;
    }
}

ParcPresse.components = { Layout };
ParcPresse.template = "is_alencon.parc_presse_template";
registry.category("actions").add("is_alencon.parc_presse_registry", ParcPresse);

console.log("## TEST 2  : registry=",registry);




