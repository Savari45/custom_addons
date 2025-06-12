import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillUpdateProps, markup, onWillStart } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { localization } from "@web/core/l10n/localization";
import { ItemOptions } from "@dashboard_maker/components/item_options/item_options";
import { parseDateTime } from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";
import { humanNumberFormatter } from "@dashboard_maker/js/number_formatter";
const formatters = registry.category("formatters");


export class DashboardListItem extends Component {
    static props = ["*"];
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
	   this.actionService = useService("action");
	   this.ormService = useService("orm");
	   this.fieldService = useService("field");
	   this.fieldDefs = [];
	   this.state = useState({
            data: {},
            offset: this.props.data.pager_data?.offset,
            limit: this.props.data.pager_data?.limit,
            is_last: this.props.data.pager_data?.is_last,
       });

       onWillStart(async () => {
            if(this.props.data.model){
                await this.getModelFieldsInfo();
            }
            if(!this.props.data.is_error){
                this.formatData(this.props.data.data);
            }
       });

       onWillUpdateProps(nextProps => {
           this.props.data = nextProps.data;
            if(!nextProps.data.is_error){
                this.formatData(nextProps.data.data);
                this.state.limit = nextProps.data.pager_data.limit;
                this.state.offset = nextProps.data.pager_data.offset;
                this.state.is_last = nextProps.data.pager_data.is_last;
            }

       });

	}

	getPreviousRecords(){
	    if(this.state.offset!==0){
            this.getListItemData('previous');
	    }
	}

	getNextRecords(){
	    if(!this.state.is_last){
            this.getListItemData('next');
	    }
	}

	getListItemData(navigation){
	    var self = this;
	    if(this.props.data.is_sql){
	        this.ormService.call(
                "dashboard.chart",
                "get_list_sql_data",
                [[this.props.item_id], this.props.data.list_domain, this.state.offset, navigation],
            ).then(function(result){
                self.props.data.data = result.data;
                if(!result.is_error){
                    self.formatData(result.data);
                    self.state.limit = result.pager_data.limit;
                    self.state.offset = result.pager_data.offset;
                    self.state.is_last = result.pager_data.is_last;
                }

            });
	    }else{
	        this.ormService.call(
                "dashboard.chart",
                "list_item_data",
                [[this.props.item_id], this.props.data.list_domain, this.state.offset, navigation],
            ).then(function(result){
                self.props.data.data = result.data;
                if(!result.is_error){
                    self.formatData(result.data);
                    self.state.limit = result.pager_data.limit;
                    self.state.offset = result.pager_data.offset;
                    self.state.is_last = result.pager_data.is_last;
                }

            });
	    }

	}

	// fetches all the fields data for specified model
    async getModelFieldsInfo() {
        this.fieldDefs = await this.fieldService.loadFields(this.props.data.model);
    }

    formatData(list_data) {
        const fields_data = this.props.data.field_types;

        this.state.data = list_data.map(row_data => {
            Object.keys(fields_data).forEach(key => {
                const value = row_data[key];

                if (!value) return;

                const fieldType = fields_data[key];

                switch (fieldType) {
                    case 'many2one':
                        if (Array.isArray(value) && value.length > 1) {
                            row_data[key] = value[1];
                        }
                        break;
                    case 'many2many':
                        if (Array.isArray(value) && value.length > 1) {
                            row_data[key] = value[1];
                        }
                        break;
                    case 'binary':
                        row_data[key] = `data:image/png;base64,${value}`;
                        break;
                    case 'html':
                        row_data[key] = markup(value);
                        break;
                    case 'integer':
                        row_data[key] = humanNumberFormatter(value, {decimals: 2, numberSystemData: this.props.data.number_system_data});
                        break;
                    case 'float':
                        row_data[key] = humanNumberFormatter(value, {decimals: 2, numberSystemData: this.props.data.number_system_data});
                        break;
                    case 'monetary':
                        row_data[key] = humanNumberFormatter(value, {decimals: 2, numberSystemData: this.props.data.number_system_data});
                        break;
                    case 'selection':
                        const formatter = formatters.get('selection');
                        row_data[key] = formatter(value, {
                                            selection: this.fieldDefs[key].selection,
                                        });
                        break;
                    case 'datetime':
                        try {
                            const parsedDate = parseDateTime(value, { format: "yyyy-MM-dd HH:mm:ss", tz: "utc" });
                            row_data[key] = parsedDate.isValid
                                ? parsedDate.toLocal().toFormat(localization.dateTimeFormat)
                                : value;
                        } catch {
                            row_data[key] = value;
                        }
                        break;
                    default:
                        row_data[key] = value;
                        break;
                }
            });
            return row_data;
        });
    }


	openSingleRecord(id){
        return this.actionService.doAction({
            name: _t(this.props.data.title),
            type: "ir.actions.act_window",
            res_model: this.props.data.model,
            views: [[false, "form"]],
            view_mode: "form",
            res_id: id,
            target: "new",
            context: {
                form_view_ref: this.props.data.form_view,
            }
        });

	}

	openGroupRecords(domain){
        return this.actionService.doAction({
            name: _t(this.props.data.title),
            type: "ir.actions.act_window",
            res_model: this.props.data.model,
            views: [[false, "list"], [false, "form"]],
            view_mode: "list, form",
            domain: domain,
            context: {
                form_view_ref: this.props.data.form_view,
                list_view_ref: this.props.data.list_view,
            }
        });
    }

}
DashboardListItem.template = "DashboardListItem";
DashboardListItem.components = { ItemOptions };
