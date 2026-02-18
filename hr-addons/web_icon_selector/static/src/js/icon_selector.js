odoo.define('web_icon_selector.widget', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var utils = require('web.utils');

    var FieldChar = basic_fields.FieldChar;

    var IconSelector = FieldChar.extend({
        className: 'oe_icon_selector',
        cssLibs: [
            '/web_icon_selector/static/src/css/fontawesome-iconpicker.css',
            '/web_icon_selector/static/src/css/icon_selector.css',
        ],
        jsLibs: [
            '/web_icon_selector/static/src/js/fontawesome-iconpicker.js',
        ],
        commitChanges: function () {
            // NOTE: commit value manually becaue main element isn't <input>
            // anymore (instead it's a <div>).
            this._setValue(this._getValue());
        },
        _renderEdit: function () {
            var res = this._super();
            var input = this.$input;
            this.$input = input;
            // NOTE: surround the input element with <div> to support
            // fontawesome picker (to detect a container upon initialization).
            this.$el = $("<div/>");
            var div_el = $("<div/>");
            input.addClass('oe_inline');
            div_el.addClass('oe_inline');
            div_el.addClass('fa');
            div_el.addClass(this.value);
            this.$el.append(div_el);
            this.$el.append(input);
            this.$input.iconpicker();
            return res
        },
        _renderReadonly: function () {
            var res = this._super();
            // NOTE: render the icon in the <span> element.
            this.$el.addClass('fa');
            this.$el.addClass(this.value);
            // NOTE: remove the text value.
            this.$el.text('');
            return res;
        },
    })

    field_registry.add("icon_selector", IconSelector);
    return IconSelector;
});
