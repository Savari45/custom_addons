import { Component, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ItemOptions } from "@dashboard_maker/components/item_options/item_options";
import { humanNumberFormatter } from "@dashboard_maker/js/number_formatter";


export class CardKpi extends Component {
    static props = ["*"];

	setup() {

	    this.actionService = useService("action");
        if(!this.props.data.is_error){
            this.props.data = this.valueFormat(this.props.data);
        }

       onWillUpdateProps(nextProps => {
            this.props.data = nextProps.data;
            if(!nextProps.data.is_error){
              this.props.data = this.valueFormat(nextProps.data);
            }
       });

	}

	valueFormat(card_data) {
	    card_data['value'] = humanNumberFormatter(card_data['value'], {decimals: 2, numberSystemData: this.props.data.number_system_data});
        return card_data;
    }

	onClickValue(){
        return this.actionService.doAction({
            name: this.props.data.title,
            type: "ir.actions.act_window",
            res_model: this.props.data.model,
            views: [[false, "list"], [false, "form"]],
            view_mode: "list, form",
            domain: this.props.data.domain,
            context: {
                form_view_ref: this.props.data.form_view,
                list_view_ref: this.props.data.list_view,
            }
        });
	}

}
CardKpi.template = "CardKpiTemplate";
CardKpi.components = { ItemOptions };
