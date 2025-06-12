import { Component, useState, onWillStart } from "@odoo/owl";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useRecordObserver } from "@web/model/relational_model/utils";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { CardKpi } from "@dashboard_maker/components/card_kpi/card_kpi";
import { DashboardListItem } from "@dashboard_maker/components/list_item/list_item";
import { DashboardMakerChart } from "@dashboard_maker/components/dashboard_maker_chart/dashboard_maker_chart";
import { loadBundle } from "@web/core/assets";

export class DashboardMakerChartPreview extends Component {
    static template = "dashboard_maker.DashboardMakerChartPreview";
    static props = {
        ...standardFieldProps,
    };
    static components = { CardKpi, DashboardListItem, DashboardMakerChart };

    setup() {
        this.state = useState({
            value: {},
            json_value: {},
            id: 123
        });

        onWillStart(async () => {
          await loadBundle("dashboard_maker.dashboardmaker_lib");
        });

        useRecordObserver((record) => {
            this.state.value = {};
            this.state.value = record.data[this.props.name];
            this.state.json_value = JSON.parse(record.data[this.props.name]);
        });
    }

}

export const dashboardMakerChartPreview = {
    component: DashboardMakerChartPreview,
};

registry.category("fields").add("dashbaord_maker_chart_preview", dashboardMakerChartPreview);
