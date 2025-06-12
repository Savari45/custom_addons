import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { loadBundle } from "@web/core/assets";
import { AccordionItem } from "@web/core/dropdown/accordion_item";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { CheckboxItem } from "@web/core/dropdown/checkbox_item";
import { DashboardListItem } from "@dashboard_maker/components/list_item/list_item";
import { CardKpi } from "@dashboard_maker/components/card_kpi/card_kpi";
import { ModelFilters } from "@dashboard_maker/components/filters/model_filter";
import { browser } from "@web/core/browser/browser";
import { DateTimeInput } from '@web/core/datetime/datetime_input';
import { Layout } from "@web/search/layout";
import { ItemOptions } from "@dashboard_maker/components/item_options/item_options";
import { DashboardMakerChart } from "@dashboard_maker/components/dashboard_maker_chart/dashboard_maker_chart";


export class DashboardMaker extends Component {
    static props = ["*"];
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
       this.uiService = useService("ui");
	   this.ormService = useService("orm");
	   this.notificationService = useService("notification");
	   this.actionService = useService("action");
	   this.dialogService = useService("dialog");

	   this.grid_data = [];
	   this.is_admin = false;

	   this.filters_domain = {};
	   this.processed_domain = {};
	   this.grid = false;
	   this.dashboard_id;
	   this.chart_ids;
	   this.current_date_filter = {};
	   this.datefilter_from;
	   this.datefilter_to;
	   this.filter_models_data = {};
	   this.date_fiter = {};
	   this.item_positions = {};
	   this.items_data = {}
       this.savedGrid = [];

       this.state = useState({
            date_filters: [],
       });

        onWillStart(async () => {
            await loadBundle("dashboard_maker.dashboardmaker_lib");
            this.dashboard_id = this.props.action.context.dashboard_record_id;
            await this.getDashboardBasicData();
            this.getDashboardData();
        });

        onWillUnmount(() =>{
           this.grid.destroy();
        });


        onMounted(()=>{

            let opts = {
              disableDrag: true,
              disableResize : true,
              cellHeight : 20,
            }
            if(this.uiService.isSmall){
                opts['column'] = 1;
            }else {
                opts['column'] = 24;
            }
            this.grid = GridStack.init(opts);
            var self = this;

            this.grid.on('change', function(event, items) {
                items.forEach(function(item) {
                    if(self.uiService.isSmall){
                        self.item_positions[item.id] = {"grid_mobile_h": item.h};
                    }else {
                        self.item_positions[item.id] = {"grid_x": item.x, "grid_y": item.y, "grid_w": item.w, "grid_h": item.h};
                    }

                    if(item.el.getAttribute('itemtype') !== 'card' && item.el.getAttribute('itemtype') !== 'list'){
                        try {
                            echarts.getInstanceByDom(document.getElementById('chart_' + item.id)).resize();
                        } catch (error) {
                        }
                    }
                });
            });

        });
	}

	 async getDashboardData(){
        var self = this;
	    const chunk_data = [];
	    const chunkSize = 3;
	    const chart_ids = this.chart_ids;

        for (let i = 0; i < chart_ids.length; i += chunkSize) {
            const chunk = chart_ids.slice(i, i + chunkSize);
            chunk_data.push(chunk);
        }

        const promises = chunk_data.map(chunk =>
            this.ormService.call(
                "dashboard.chart",
                "get_charts_data",
                [chunk, [this.processed_domain], this.date_filter],
            )
        );

        await Promise.all(promises)
            .then(results => {
                results.forEach(result => {
                    Object.assign(self.items_data, result);
                });
            });

        this.render();
	}

	async getDashboardBasicData() {
        // get the data to show on first attempt which are filters, grid positions, items basic data
        var self = this;
        await this.ormService.call(
            "dashboard.dashboard",
            "dashboard_basic_data",
            [[this.dashboard_id], this.uiService.isSmall],
        ).then(function(results){
            self.grid_data = results["grid_data"];
            self.filter_models_data = results['filter_models_data'];
            self.state.date_filters = results['date_filters'];
            self.chart_ids = self.grid_data.map(dict => dict['id']);
            self.is_admin = results['is_admin'];
        });

        let date_filter = self.state.date_filters.find(item => item.isActive === true);
        this.onChangeDateFilter(date_filter.id, false);
    }

	onClickAddItem(){
	    this.actionService.doAction(
	    {
            name: _t("Add New Chart"),
            type: "ir.actions.act_window",
            res_model: 'dashboard.chart',
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
            context: {
                form_view_ref: 'dashboard_maker.dashboard_chart_view_form',
                default_dashboard_id: this.dashboard_id
            }
        }
        );
	}

	onChangeDateFilter(filter_id, refreshNeeded=true){
        if(filter_id==0){
            this.date_filter = {
                'type': 'all'
            }
        }else{
            this.date_filter = {
                'type': 'record',
                'id': filter_id
            }
        }

        if(refreshNeeded){
            const updatedList = this.state.date_filters.map(item => {
                if (item.id === filter_id) {
                    return { ...item, isActive: true };
                }
                else{
                    return { ...item, isActive: false };
                }
            });
            this.state.date_filters = updatedList;
            this.getDashboardData();
        }
	}

	onChangeFromDate(datetime){
	    this.datefilter_from = datetime;
	}

	onChangeToDate(datetime){
	    this.datefilter_to = datetime;
	}

	onCustomDateFilterApply(){
	    var local_datetime_from = false;
        var local_datetime_to = false;
        var local_date_from = false;
        var local_date_to = false;
        if(this.datefilter_from){
            var local_datetime_from = this.datefilter_from.toUTC().toFormat("yyyy-MM-dd HH:mm:ss", { numberingSystem: 'latn' });
            var local_date_from = this.datefilter_from.toUTC().toFormat("yyyy-MM-dd", { numberingSystem: 'latn' });
        }
	    if(this.datefilter_to){
	        var local_datetime_to = this.datefilter_to.toUTC().toFormat("yyyy-MM-dd HH:mm:ss", { numberingSystem: 'latn' });
	        var local_date_to = this.datefilter_to.toUTC().toFormat("yyyy-MM-dd", { numberingSystem: 'latn' });
	    }

	    this.date_filter = {
            'type': 'custom',
            'datetime_start': local_datetime_from,
            'datetime_end': local_datetime_to,
            'date_start': local_date_from,
            'date_end': local_date_to,
        };

        const updatedList = this.state.date_filters.map(item => {
                return { ...item, isActive: false };
        });
        this.state.date_filters = updatedList;

        this.getDashboardData();
	}

	openSettings(){
	    this.actionService.doAction(
	    {
            name: _t("Dashboard Settings"),
            type: "ir.actions.act_window",
            res_model: 'dashboard.dashboard',
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
            res_id: this.dashboard_id,
            context: {
                form_view_ref: 'dashboard_maker.dashboard_view_form',
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

    onUpdateFilter(domain, model){
        this.processed_domain[model] = JSON.stringify(domain);
    }

    onApplyFilter(){
        this.getDashboardData();
    }

    // when user turn on edit mode then enable move and resize options
    turnEditMode(){
        if(this.uiService.isSmall){
            this.grid.enableResize(true);
        }else {
            this.grid.enableMove(true);
            this.grid.enableResize(true);
        }

        const discard_button = document.querySelector('.dash_discard_btn');
        const save_button = document.querySelector('.dash_save_btn');
        const edit_button = document.querySelector('.dash_edit_btn');
        if (discard_button) {
            discard_button.classList.remove('d-none');  // Remove the specific class
        }
        if (save_button) {
            save_button.classList.remove('d-none');  // Remove the specific class
        }
        if (edit_button) {
            edit_button.classList.add('d-none');  // Remove the specific class
        }
        this.savedGrid = this.grid.save(false, false);
    }

    // when user click on save option after edit then disable move and resize options
    async saveLayout(){
        this.uiService.block();
        this.grid.enableMove(false);
        this.grid.enableResize(false);
        for (const [key, value] of Object.entries(this.item_positions)) {
             await rpc("/web/dataset/call_kw/dashboard.chart/write", {
                model: 'dashboard.chart',
                method: 'write',
                args: [parseInt(key), value],
                kwargs: {},
            });
        }
        const discard_button = document.querySelector('.dash_discard_btn');
        const save_button = document.querySelector('.dash_save_btn');
        const edit_button = document.querySelector('.dash_edit_btn');
        if (discard_button) {
            discard_button.classList.add('d-none');  // Remove the specific class
        }
        if (save_button) {
            save_button.classList.add('d-none');  // Remove the specific class
        }
        if (edit_button) {
            edit_button.classList.remove('d-none');  // Remove the specific class
        }
        this.item_positions = {};
        this.savedGrid = [];
        this.uiService.unblock();
    }

    discardLayout(){
        this.grid.load(this.savedGrid);
        this.grid.enableMove(false);
        this.grid.enableResize(false);
        const discard_button = document.querySelector('.dash_discard_btn');
        const save_button = document.querySelector('.dash_save_btn');
        const edit_button = document.querySelector('.dash_edit_btn');
        if (discard_button) {
            discard_button.classList.add('d-none');  // Remove the specific class
        }
        if (save_button) {
            save_button.classList.add('d-none');  // Remove the specific class
        }
        if (edit_button) {
            edit_button.classList.remove('d-none');  // Remove the specific class
        }
        this.savedGrid = [];
        this.item_positions = {};
    }

}
DashboardMaker.template = "DynamicDashboard";
DashboardMaker.components = {  MultiRecordSelector, DomainSelectorDialog, AccordionItem, CheckBox, Dropdown, CheckboxItem, DashboardListItem, DashboardMakerChart, DateTimeInput, ModelFilters, CardKpi, Layout, ItemOptions};
registry.category("actions").add("dashboard_maker", DashboardMaker)
