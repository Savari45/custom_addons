import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { CheckboxItem } from "@web/core/dropdown/checkbox_item";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


export class ItemOptions extends Component {
    static props = ["*"];
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
	    this.actionService = useService("action");
	    this.dialogService = useService("dialog");
	    this.ormService = useService("orm");

        this.options = [{
            'name': 'edit',
            'title': 'Edit',
        },
        {
            'name': 'delete',
            'title': 'Delete',
        },
        {
            'name': 'copy_dash',
            'title': 'Copy Chart',
        },
        {
            'name': 'move_dash',
            'title': 'Move Chart',
        }]

	}

	performOptionOperation(option){
	    if(option === 'edit'){
	        this.editItem();
	    }
	    else if(option === 'delete'){
            this.onDeleteItem();
        }
        else if(option === 'copy_dash'){
            this.copyItem('copy');
        }
        else if(option === 'move_dash'){
            this.copyItem('move');
        }
	}

    copyItem(copy_type){
        return this.actionService.doAction({
            name: _t("Copy/Move Chart"),
            type: "ir.actions.act_window",
            res_model: "copy.dashboard.chart.wizard",
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
            context:{
                'default_chart_id': this.props.item_id,
                'default_operation': copy_type,
            }
        },
        {
            props: {
                onSave: (record, params) => {
                    browser.location.reload();
                }
            }
        });
    }

	editItem(){
	    this.actionService.doAction(
	    {
            name: _t("Edit Chart"),
            type: "ir.actions.act_window",
            res_model: 'dashboard.chart',
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
            res_id: this.props.item_id,
            context: {
                form_view_ref: 'dashboard_maker.dashboard_chart_view_form',
            }
        },
        {
            props: {
                onSave: (record, params) => {
                    browser.location.reload();
                }
            }
        }
        );
	}

	deleteItem(itemId){
        this.ormService.call(
            "dashboard.chart",
            "unlink",
            [[itemId]],
        ).then(() => {
            browser.location.reload();
        })
	}


	onDeleteItem(){
        const dialogProps = {
            title: _t("Warning"),
            body: _t("Are you sure that you want to delete this Item?"),
            confirmLabel: _t("Delete Item"),
            confirm: () => this.deleteItem(this.props.item_id),
            cancel: () => {},
        };
        this.dialogService.add(ConfirmationDialog, dialogProps);
	}


}
ItemOptions.template = "ItemOptions";
ItemOptions.components =  { CheckBox, Dropdown, CheckboxItem};
