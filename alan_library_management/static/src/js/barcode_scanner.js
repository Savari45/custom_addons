odoo.define('alan_library_management.barcode_scanner', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var _t = core._t;

    var BarcodeScanner = Widget.extend({
        template: 'LibraryBarcodeScanner',
        events: {
            'click .o_barcode_scanner_close': '_onClose',
        },

        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.model = options.model;
            this.method = options.method;
            this.res_id = options.res_id;
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._setupScanner();
            });
        },

        _setupScanner: function() {
            var self = this;
            this.$input = this.$('.o_barcode_scanner_input');
            this.$input.focus();

            this.$input.on('keypress', function(e) {
                if (e.which === 13) { // Enter key
                    var barcode = self.$input.val().trim();
                    if (barcode) {
                        self._processBarcode(barcode);
                    }
                    self.$input.val('');
                }
            });
        },

        _processBarcode: function(barcode) {
            var self = this;
            this._rpc({
                model: this.model,
                method: this.method,
                args: [barcode],
                kwargs: {context: {}},
            }).then(function(result) {
                if (result.success) {
                    self.do_notify(_t("Success"), result.message);
                } else {
                    self.do_warn(_t("Warning"), result.message);
                }
            });
        },

        _onClose: function() {
            this.trigger_up('close_dialog');
        },
    });

    core.action_registry.add('library_barcode_scanner', BarcodeScanner);

    return {
        BarcodeScanner: BarcodeScanner,
    };
});