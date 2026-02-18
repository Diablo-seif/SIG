odoo.define('hr_organization_chart.OrgChart', function (require) {
    "use strict";
    var OrgChartController = require('hr_organization_chart.OrgChartController');
    var OrgChartModel= require('hr_organization_chart.OrgChartModel');
    var OrgChartRenderer= require('hr_organization_chart.OrgChartRenderer');
    var AbstractView = require('web.AbstractView');
    var ViewRegistry = require('web.view_registry');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _lt = core._lt;

    var OrgChartView  = AbstractView.extend({
        config: _.extend({}, AbstractView.prototype.config, {
            Controller: OrgChartController,
            Model: OrgChartModel,
            Renderer: OrgChartRenderer,
        }),
        viewType: 'org_chart',
        display_name: _lt('Chart'),
        icon: 'fa-sitemap',
        withSearchBar: false,
        searchMenuTypes: ['filter'],
        

    });
    ViewRegistry.add('org_chart', OrgChartView);
    return OrgChartView;
});


