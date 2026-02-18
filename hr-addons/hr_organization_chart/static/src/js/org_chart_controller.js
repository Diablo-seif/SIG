odoo.define('hr_organization_chart.OrgChartController', function (require) {
    "use strict";
    var AbstractController = require('web.AbstractController');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _lt = core._lt;

    var OrgChartController = AbstractController.extend({

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },

        renderButtons: function ($node) {
            this.$buttons = $(QWeb.render('empView.buttons'));
            this.$buttons.click(this._onButtonClick.bind(this));
            this.$buttons.appendTo($node);
        },
        _setMode: function (mode) {
            this.update({mode: mode});
            this._updateButtons();
        },
        _updateButtons: function () {

            if (!this.$buttons) {
                return;
            }
            var state = this.model.get();
            this.$buttons.find('.o_emp_button').removeClass('active');
            if (state.mode != 'levels')
                this.$el.find('.o_filters_menu_button').hide();
            else {
                this.$el.find('.o_filters_menu_button').show();
            }
            this.$buttons
                .find('.o_emp_button[data-mode="' + state.mode + '"]')
                .addClass('active');

        },

        _onButtonClick: function (ev) {
            var target = $(ev.target);
            this._setMode(target.data('mode'));
        },


    });
    return OrgChartController;
});


