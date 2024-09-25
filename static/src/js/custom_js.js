
my js


odoo.define('travel_agency_app.many2one_numero_id', function (require) {
    'use strict';

    var relational_fields = require('web.relational_fields');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var FieldMany2One = relational_fields.FieldMany2One;

    FieldMany2One.include({
        _searchCreatePopup: function (viewInfo, context) {
            // get the user-entered value from the numero_id search input
            var userInput = this.$input.val();
            // add the user input as default_mobile to the context
            context['default_mobile'] = userInput;
            return this._super(viewInfo, context);
        }
    });

    field_registry.add('many2one_numero_id', FieldMany2One);
});

My xml field

 <field name="numero_id"  widget="many2one_numero_id"  context="{}"/>

