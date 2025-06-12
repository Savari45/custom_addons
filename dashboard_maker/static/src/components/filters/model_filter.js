import { Component, useState, onWillStart } from "@odoo/owl";
import { useService, useOwnedDialogs } from "@web/core/utils/hooks";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { Domain } from "@web/core/domain";
import { user } from "@web/core/user";
import { getValueEditorInfo } from "@web/core/tree_editor/tree_editor_value_editors";
import { DmFieldFilter } from "@dashboard_maker/components/filters/field_filter";


export class ModelFilters extends Component {
    static props = ["*"];
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
	    this.fieldService = useService("field");
	    this.addDialog = useOwnedDialogs();
	    this.model = this.props.filter_data.model;
	    this.model_name = this.props.filter_data.name;
	    this.filters_domain = "[]";
	    this.processed_domain = [];
	    this.fields_data = this.props.filter_data.fields_data;
	    this.fieldDefs = {};
	    this.quickFilters = {};
	    this.nodes = [];

	    if(this.fields_data.length!=0){
            var nodes = [];
            this.fields_data.forEach(item => {
                  nodes.push({
                            "type": "condition",
                            "path": item.name,
                            "negate": false,
                            "operator": item.operator,
                            "value": []
                        })
            });
            this.nodes = nodes;
	    }

	    onWillStart(async () => {
            await this.getModelFieldsInfo();
        });
	}

    // saves the data each time filter updated
    update_domain(domain) {
        let processed_domain = new Domain(domain).toList(user.context);
        this.processed_domain = JSON.stringify(processed_domain);
        this.filters_domain = domain;
        this.combineDomains();
        return domain;
    }

	// opens the view to select the filter for model
	onEditDialogBtnClick(ev) {
        ev.preventDefault();
        this.addDialog(DomainSelectorDialog, {
            resModel: this.model,
            domain: this.filters_domain,
            isDebugMode: true,
            onConfirm: this.update_domain.bind(this),
        });
    }

    // fetches all the fields data for specified model
    async getModelFieldsInfo() {
        this.fieldDefs = await this.fieldService.loadFields(this.model);
    }

     // gets the info about which data to load in autocomplete
	 getValueEditorInfo(node) {
        const fieldDef = this.fieldDefs[node.path];
        return getValueEditorInfo(fieldDef, node.operator);
    }

    // combines the quick filter domain and model domain and refresh the data on page
    combineDomains(){
        let combinedDomain = [];
        var quickFilters = this.quickFilters;
        for (const key in quickFilters) {
          if(quickFilters[key] && quickFilters[key].length != 0){
              combinedDomain.push(JSON.parse(quickFilters[key]));
          }
        }

        if(this.processed_domain.length != 0){
            combinedDomain.push(...JSON.parse(this.processed_domain));
        }

        this.props.onUpdate(combinedDomain, this.model);
    }

    onUpdateFilter(domain, path){
        this.quickFilters[path] = domain;
        this.combineDomains();
    }

}
ModelFilters.template = "ModelFiltersTemplate";
ModelFilters.components = { DmFieldFilter };
