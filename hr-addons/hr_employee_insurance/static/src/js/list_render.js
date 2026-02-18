odoo.define('hr_employee_insurance.ListRenderer', function (require) {
    "use strict";
    var ListRenderer = require('web.ListRenderer');
    var config = require('web.config');
    var field_utils = require('web.field_utils');

    ListRenderer.include({

        _renderAggregateCells: function (aggregateValues) {
            var self = this;
            return _.map(this.columns, function (column) {
                var $cell = $('<td>');
                if (config.isDebug()) {
                    $cell.addClass(column.attrs.name);
                }
                if (column.attrs.editOnly) {
                    $cell.addClass('oe_edit_only');
                }
                if (column.attrs.readOnly) {
                    $cell.addClass('oe_read_only');
                }
                if (column.attrs.name in aggregateValues) {
                    var field = self.state.fields[column.attrs.name];
                    var value = aggregateValues[column.attrs.name].value;
                    var help = aggregateValues[column.attrs.name].help;
                    var text = aggregateValues[column.attrs.name].text;
                    var formatFunc = field_utils.format[column.attrs.widget];
                    if (!formatFunc) {
                        formatFunc = field_utils.format[field.type];
                    }
                    var formattedValue = formatFunc(value, field, { escape: true });
                    $cell.addClass('o_list_number').attr('title', help).html('<span>'+ (text? text + ': ': '') +'</span>' + formattedValue);
                }
                return $cell;
            });
        },

        _computeColumnAggregates: function (data, column) {
            this._super.apply(this, arguments);
            var attrs = column.attrs;
            var field = this.state.fields[attrs.name];
            if (!field) {
                return;
            }
            var type = field.type;
            if (type !== 'integer' && type !== 'float') {
                return;
            }
            var func = attrs.date;
            if (func) {
                var years_tot = 0;
                var months_tot = 0;
                var days_tot = 0;
                _.each(data, function (d) {
                    years_tot += (d.type === 'record') ? d.data['duration_years'] : d.aggregateValues['duration_years'];
                    months_tot += (d.type === 'record') ? d.data['duration_months'] : d.aggregateValues['duration_months'];
                    days_tot += (d.type === 'record') ? d.data['duration_days'] : d.aggregateValues['duration_days'];
                });
                // Average days at month
                var month_days= 30.4375;
                var days = days_tot % month_days;
                var months = (months_tot + parseInt(days_tot / month_days)) % 12;
                var years = years_tot +  parseInt((months_tot + parseInt(days_tot / month_days)) / 12);
                _.each(this.columns, function (column) {
                    if(column.attrs.date === 'Years'){
                        column.aggregate = {
                            help: column.attrs.date ,
                            text: column.attrs.date ,
                            value: years ,
                        };
                    }
                    else if(column.attrs.date === 'Months'){
                        column.aggregate = {
                            help: column.attrs.date ,
                            text: column.attrs.date ,
                            value: months ,
                        };
                    }
                    else if(column.attrs.date === 'Days'){
                        column.aggregate = {
                            help: column.attrs.date ,
                            text: column.attrs.date ,
                            value: days ,
                        };
                    }
                });
            }
        }
    })
});
