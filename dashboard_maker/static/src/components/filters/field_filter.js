import { Component, useState } from "@odoo/owl";
import { getValueEditorInfo } from "@web/core/tree_editor/tree_editor_value_editors";


export class DmFieldFilter extends Component {
static props = ["*"];
	setup() {

        this.state = useState({
            node: this.props.node,
       });

	}

	getValueEditorInfo(node) {
        const fieldDef = this.props.fieldDef;
        return getValueEditorInfo(fieldDef, node.operator);
    }

    updateLeafValues(value) {
        this.state.node["value"] = value;
        var operator = this.state.node.operator;
        var path = this.state.node.path;
        var domain = false
         if(operator === "in" && value.length !=0){
            domain = `["${path}", "${operator}", ${JSON.stringify(value)}]`;
         }else if(value.length !=0 && operator === "ilike" || operator === "="){
            domain = `["${path}", "${operator}", "${value}"]`;
         }
         this.props.onUpdate(domain, path);
    }

}
DmFieldFilter.template = "DmFieldFilter";
