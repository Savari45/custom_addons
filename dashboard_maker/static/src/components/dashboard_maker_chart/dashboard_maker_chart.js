import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUpdateProps, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { humanNumberFormatter } from "@dashboard_maker/js/number_formatter";
import { ItemOptions } from "@dashboard_maker/components/item_options/item_options";


export class DashboardMakerChart extends Component {
static props = ["*"];
	setup() {
	   this.actionService = useService("action");
	   this.chartInstance = null;
       this.domainsData = this.props.data.data_domains;

       onMounted(async () => {
           if(!this.props.data.is_error){
               await this.initializeChart();
               this.updateChartOptions();
               this.chartInstance.resize();
           }
       });

        onWillUpdateProps(nextProps => {
            this.props.data = nextProps.data;
            if(!this.chartInstance){
                if(!nextProps.data.is_error){
                    this.initializeChart();
                }
            }

            if(!this.props.data.is_error){
                this.chartInstance.setOption(nextProps.data.chart_basic_info, true);
                this.chartInstance.setOption(nextProps.data.options);
                this.domainsData  = nextProps.data.data_domains;
            }

       });

       onWillUnmount(() =>{
           if(this.chartInstance){
               this.chartInstance.dispose();
               this.chartInstance = null;
           }
       });
	}

    updateChartOptions(){
        this.chartInstance.setOption(this.props.data.chart_basic_info, true);
        if(this.props.data.type === "h_bar"){
           var new_options = this.props.data.options;
           const temp = new_options['xAxis'];
           new_options['xAxis'] = new_options['yAxis'];
           new_options['yAxis'] = temp;
           this.chartInstance.setOption(new_options);
       }else{
            this.chartInstance.setOption(this.props.data.options);
       }

       if(this.props.data.type==='pie' || this.props.data.type === 'doughnut' || this.props.data.type ==='h_doughnut' || this.props.data.type ==='h_pie'){
            this.chartInstance.setOption(this.pieValueFormat());
       }else if(this.props.data.type==='bar' || this.props.data.type==='line' || this.props.data.type==='area' || this.props.data.type==='h_bar' || this.props.data.type==='line'){
            this.chartInstance.setOption(this.barValueFormat());
       }else if(this.props.data.type==='scatter'){
            this.chartInstance.setOption(this.scatterValueFormat());
       }
    }

    async initializeChart(){
        var self = this;
        const chartDom = document.getElementById('chart_' + this.props.item_id);
        const myChart = echarts.init(chartDom, null, { width : 'auto', height : 'auto' });
        this.chartInstance = myChart;

        if(this.props.data.show_records){
            myChart.on('click', function(params) {
                var data_domain = false;
                if(self.props.data.type === 'bar' || self.props.data.type === 'line' || self.props.data.type === 'area' || self.props.data.type === 'h_bar'){
                    const bar_type = self.props.data.bar_type;
                    if(bar_type === 'simple' || bar_type === 'field_grouped' || (bar_type === 'field_stacked' && !self.props.data.sub_available)){
                        data_domain = self.domainsData[params.dataIndex];
                    }else if(bar_type === 'group_grouped'){
                        data_domain = self.domainsData[params.seriesIndex][params.dataIndex][0];
                    }else if(bar_type === 'field_stacked'){
                        let series_index = Math.floor(params.seriesIndex/(self.domainsData.length))
                        data_domain = self.domainsData[series_index][params.dataIndex][0];
                    }else if(bar_type === 'group_stacked' || bar_type === 'stacked_stacked' || bar_type === 'grouped_grouped'){
                        data_domain = self.domainsData[Math.floor(params.seriesIndex/self.props.data.fields_count)][params.dataIndex][0];
                    }
                }else if(self.props.data.type==='pie' || self.props.data.type==='doughnut' || self.props.data.type==='h_doughnut' || self.props.data.type==='h_pie'){
                    data_domain = self.domainsData[params.seriesIndex][params.dataIndex]
                }else if(self.props.data.type==='scatter'){
                    data_domain = self.domainsData[params.dataIndex];
                }
                if(data_domain){
                    self.openDataView(data_domain);
                }
            });
        }
	}

	barValueFormat(){
	    var self = this;
	    var format_data = {
            yAxis: {
                axisLabel: {
                    formatter: function (value, index) {
                        return humanNumberFormatter(value, {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    }
                }
            },
            tooltip: {
                valueFormatter: function (value) {
                    return humanNumberFormatter(value, {decimals: 2, numberSystemData: self.props.data.number_system_data});
                }
            }
        }

        if(this.props.data.type === "h_bar"){
            format_data['xAxis'] = format_data['yAxis'];
            format_data['yAxis'] = false;
        }
	    return format_data;
	}

    pieValueFormat(){
	    var self = this;
	    var format_data = {
                tooltip: {
                    valueFormatter: function (value) {
                    return humanNumberFormatter(value, {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    }
                }
            };

        if(this.props.data.display_label){
            format_data['label'] = {
                show: true,
                formatter: function(params){
                    if(self.props.data.label_format === 'name'){
                        return params['name']
                    }else if(self.props.data.label_format === 'value'){
                        return humanNumberFormatter(params['value'], {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    }else if(self.props.data.label_format === 'per'){
                        return params['percent'] + '%';
                    }else if(self.props.data.label_format === 'name_value'){
                        return params['name'] + ': ' + humanNumberFormatter(params['value'], {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    }else if(self.props.data.label_format === 'name_per'){
                        return params['name'] + ' (' + params['percent'] + '%)';
                    }else{
                       return params['name']
                    }
                }
            }
        }

	    return format_data;
	}

    scatterValueFormat(){
	    var self = this;
	    var format_data = {
                tooltip: {
                    formatter: function (params) {
                        return ''+ humanNumberFormatter(params['data'][0], {decimals: 2, numberSystemData: self.props.data.number_system_data}) + ' : ' + humanNumberFormatter(params['data'][1], {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    },
                },
             yAxis: {
                axisLabel: {
                    formatter: function (value, index) {
                        return humanNumberFormatter(value, {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    }
                }
            },
            xAxis: {
                axisLabel: {
                    formatter: function (value, index) {
                        return humanNumberFormatter(value, {decimals: 2, numberSystemData: self.props.data.number_system_data});
                    }
                }
            }
            };

	    return format_data;
	}

    openDataView(data_domain){
        return this.actionService.doAction({
            name: _t("Chart Data"),
            type: "ir.actions.act_window",
            res_model: this.props.data.model,
            views: [[false, "list"], [false, "form"]],
            view_mode: "list, form",
            domain: data_domain,
            context: {
                form_view_ref: this.props.data.form_view,
                list_view_ref: this.props.data.list_view,
            }
        });
	}

}
DashboardMakerChart.template = "DashboardMakerChart";
DashboardMakerChart.components = { ItemOptions };
