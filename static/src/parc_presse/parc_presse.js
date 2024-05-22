/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";

const { Component, useSubEnv, useState, onWillStart } = owl;


console.log("## TEST 1 ##");

class ParcPresse extends Component {
    setup() {
        this.user_id = useService("user").context.uid;
        this.action  = useService("action");
        this.orm     = useService("orm");
        this.state   = useState({
            'equipements': {},
        });

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
            this.getParcPresse();
        });
    } 

    OKclick(ev) {
        this.getParcPresse(true);
    }

 

    async getParcPresse(ok=false){
        var res = await this.orm.call("is.equipement", 'get_parc_presse', [false]);
        this.state.equipements = res.equipements;
        console.log('getParcPresse : res=',res);
    }
}

ParcPresse.components = { Layout };
ParcPresse.template = "is_alencon.parc_presse_template";
registry.category("actions").add("is_alencon.parc_presse_registry", ParcPresse);

console.log("## TEST 2  : registry=",registry);




