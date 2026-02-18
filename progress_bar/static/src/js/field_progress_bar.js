odoo.define('progress_bar.progress_bar', function (require) {
    "use strict";
    var basicFields = require('web.basic_fields');

    return basicFields.FieldProgressBar.includes({
        _render: function () {
            var self = this;
        },
        init: function () {
            this._super.apply(this, arguments);
            if (this.nodeOptions.percentage) {
                this.value = this.value / 100;
                this.max_value = 1;
            }
        },
    });
});
