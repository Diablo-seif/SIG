odoo.define('hr_organization_chart.OrgChartModel', function (require) {
    "use strict";
    var AbstractModel = require('web.AbstractModel');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _lt = core._lt;

    var OrgChartModel = AbstractModel.extend({
        get: function (id) {
            if(id){
               return {res_id:id}; 
            }
            else{
                return {mode:this.mode, data: this.data}
            }
        },
        
        reload: function (id, params) {
            return this._load(params)
        },
        load: function (params) {
            this.mode = params.mode? params.mode:"levels";

            return this._load(params)
        },
        getSchema: function(){
            var self = this;
            return this._rpc({
                model: 'hr.employee',
                method: 'get_schema',
            }).then(function (data) {
                self.data= [];
                _.each(data, function(item) {
                    self.data.push(item[1])
                })
            });
        },
        _load: function (params) {
            this.domain = params.domain || this.domain || [];
            self = this;
            this.mode = params.mode? params.mode:this.mode;
            if(this.mode == 'levels'){
                return this._rpc({
                    model: 'hr.employee',
                    method: 'get_employees',
                    kwargs: {
                        domain: params.domain || [],
                    },
                }).then(function (data) {
                    self.data= data;
                });
            } else if(this.mode == 'managers') {
                return this._rpc({
                    model: 'hr.employee',
                    method: 'get_employee_childs',
                    args: [false],
                    fields: ['id', 'name', 'image_1920', 'job_title'],
                    domain: params.domain
                }).then(function (result) {
                    self.data= result;
                });
            }
            else if(this.mode == 'schema'){
                return this.getSchema();
                }


        }
    });
    return OrgChartModel;
});


