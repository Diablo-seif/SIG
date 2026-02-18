odoo.define('hr_organization_chart.OrgChartRenderer', function (require) {
    "use strict";
    let AbstractRenderer = require('web.AbstractRenderer');
    let core = require('web.core');
    let QWeb = core.qweb;
    let _lt = core._lt;

    
    let OrgChartRenderer = AbstractRenderer.extend({
        events:{
            'click .tree .card': '_onClick',
        },
        _onClick: function(ev) {
            let id = $(ev.currentTarget).data('id');
            if (id) {
                this.trigger_up('open_record', { id: id });
            }
        },
        _renderFunnel() {
            let container = this.$el[0];
            container.className = ("text-center") 
            $(container).css("margin-top","5px")
            $(container).append("<div style='font-size:30px;margin-bottom:6px'>Organization Schema</div>");
            let options= {
                hoverEffects: true,
                isInverted: true,
                isCurved: false,
                bottomWidth: 0,
                height: 850,
                bottomPinch: 0,
                width: 1280,
                fillType: "solid",
                curveHeight: 0,
                fontSize: "25px",
                onClickBlock: function(e){
                    e.object.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'hr.employee',
                        name: 'Employee',
                        views: [[false, 'list'], [false, 'form']],
                        domain:[e.domain],
                        context: {'search_default_filter_group_level': 1}
                    });
                },
            }
 
            let values = this.state.data
            let self = this;
            _.each(values, function(item) {
                item.push(self)
            })
            let counts = [];
            _.each(values, function(item) {
                counts.push(item[1])
            })
            let svg = d3.select(container)
                .append('svg').attr('height', '50%')
                .attr('width', '55%')
                .attr('id', "funnel").attr('preserveAspectRatio', 'xMinYMin')
                .attr('viewBox', '0 0 ' + options.width + ' ' + options.height);
            let funnel = new D3Funnel(values,options, counts);
            funnel.draw("#funnel");
        },
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            this.inDOM = true;
            this._render();
        },
        /**
        * @override
        */
        on_detach_callback: function () {
            this._super.apply(this, arguments);
            this.inDOM = false;
        },
        _render: function(){
            this.$el.html(QWeb.render('org_chart', {mode:this.state.mode, data: this.state.data}));
            if (this.inDOM) {
                let self = this;
                return this._super.apply(this, arguments).then(function(){
                    if(self.state.mode == "schema") {
                        self._renderFunnel() 
                    }
                })
            }
            else{
                return this._super.apply(this, arguments)
            }
        }
    });

    return OrgChartRenderer;
});


