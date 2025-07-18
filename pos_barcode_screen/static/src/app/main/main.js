/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { renderToString } from "@web/core/utils/render";
import { patch } from "@web/core/utils/patch";
import { onMounted, useState } from "@odoo/owl";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";

patch(ProductScreen.prototype, {
	setup() {
		super.setup(...arguments);
		this.uiState = useState({
			clicked: false,
		});
		onMounted(() => {
			var self = this;
			self.display_orderline();
			$('.pad_tg').click(function () {
				if ($('.subpads').is(':hidden') == false) {
					$('.subpads').addClass('removebuttons');
					$('.pads').addClass('removebuttons');
				} else {
					$('.subpads').removeClass('removebuttons');
					$('.pads').removeClass('removebuttons');
				}
			})
			if (self.pos.config.show_barcode_screen) {
				self.pos.show_barcode_screen = false;
				$('.order-container').attr("style", "display: none !important");
				$('.order-summary').attr("style", "display: none !important");
				$('.product-screen .rightpane').attr("style", "display: none !important");
				$('.wk_barcode_screen').show()
				$('.wk_barcode_screen').attr("style", "width:69%");
			} else {
				self.pos.show_barcode_screen = true;
				$('.order-container').attr("style", "display: block !important");
				$('.order-summary').attr("style", "display: block !important");
				$('.product-screen .rightpane').show()
				$('.wk_barcode_screen').hide();
			}
			const firstLine = $(".wk-order-line").first();
			if (firstLine.length) {
				self.line_select(firstLine, firstLine.attr('data-id'));
			}
			$('.wk-order-list-contents').on('click', '.wk-order-line', function (event) {
				event.stopImmediatePropagation();
				self.line_select($(this), $(this).attr('data-id'));
			});
			$(".pos-topheader .pos-rightheader .search-bar-portal .search-box input").on("click", function (event) {
				if (self.pos.show_barcode_screen) {
					self.pos.show_barcode_screen = false
					$('.wk_barcode_screen_status').removeClass('oe_green');
					self.showScreen('PaymentScreen', { return: true })
				}
			})
		});
	},
	display_orderline() {
		var self = this;
		var order = self.pos.get_order();
		var contents = $('.wk-order-list-contents');
		var wk_orderline_list = order.get_orderlines();
		self.pos._update_summary(contents, wk_orderline_list)
	},
	line_select($line, id) {
		var self = this;
		var order = self.pos.get_order();
		var orderline = (order && id) ? order.get_orderline(id) : false;
		if (id && order && orderline) {
			$('.wk-order-line.wk_highlight').removeClass('wk_highlight');
			$line.addClass('wk_highlight');
			if (orderline.product_id.description_sale) {
				$(".wk_product_description").show();
				$(".wk_product_description .product_desc").text(orderline.product_id.description_sale);
			} else {
				$(".wk_product_description").hide();
			}
			order.select_orderline(orderline);
		}
	},
	get_selected_line_product_url(product) {
		if (product) {
			return (`/web/image?model=product.product&field=image_128&id=${product.id}&unique=${this.write_date}`);
		}
		else {
			return;  
		}
	}
});
patch(OrderWidget.prototype, {
	get get_selected_line_product() {
		var self = this;
		var order = self.pos.get_order();
		if (order && order.get_selected_orderline()) {
			if (order.get_selected_orderline().product_id) {	
				$(".wk_selected_product_name").text(order.get_selected_orderline().product_id.display_name)
				return ((order.get_selected_orderline().product_id.image_128 && `/web/image?model=product.product&field=image_128&id=${order.get_selected_orderline().product_id.id}&unique=${order.get_selected_orderline().product_id.write_date}`) || "");
			}
			else
				return;
		}
	},
	setup() {
		var self = this;
		self.pos = usePos();
		super.setup();
		onMounted(this.wkOnMounted);
	},
	wkOnMounted() {
		var self = this;
		if (self.props.total && self.props.tax) {
			var order = self.pos.get_order();
			var total = order ? order.get_total_with_tax() : 0;
			var taxes = order ? total - order.get_total_without_tax() : 0;
			$('.wk_summary .wk_entry .wk_total').text(self.env.utils.formatCurrency(total));
			$('.wk_summary .wk_entry .subentry.value').text(self.env.utils.formatCurrency(taxes));
			var order_line = order.get_selected_orderline()
			if (order) {
				if (order_line && !order_line.wk_node) {
					var wk_node = order_line.wk_node;
					if (wk_node && wk_node.parentNode) {
						wk_node.parentNode.replaceChild(wk_replacement_line, wk_node);
						$('.wk-order-line.wk_highlight').removeClass('wk_highlight');
						$(wk_replacement_line).addClass('wk_highlight');
					}
				}
				if (self.pos.show_barcode_screen) {
					if (order_line) {
						let product = order_line.product_id;
						$('.wk_image_box').show();
						$(".wk_selected_product_name").text(product.display_name);
						if (product.description_sale) {
							$(".wk_product_description").show();
							$(".wk_product_description .product_desc").text(product.description_sale);
						} else {
							$(".wk_product_description").hide();
						}
					}
				} else {
					$('.wk_image_box').hide();
				}
			}
		}
	},
});
patch(Navbar.prototype, {
	setup() {
		var self = this;
		self.pos = usePos();
		self.pos.show_barcode_screen = true;
		super.setup();
	},
	click_barcode_button(event) {
		var self = this;
		var order = self.pos.get_order();
		if (self.pos.show_barcode_screen == true) {	
			$('.order-container').attr("style", "display: none !important");
			$('.order-summary').attr("style", "display: none !important");
			$('.wk_image_box').attr("style", "display: block !important");
			$($(".product-screen .rightpane")).attr("style", "display: none !important");
			$(".product-screen .rightpane.wk_barcode_screen").show()
			$('.product-screen .rightpane.wk_barcode_screen').attr("style", "width:69%");
			$('.wk_barcode_screen_status').addClass('oe_green');
			$('.selected_product_details').attr("style", "display: block !important");
			var self = this;
			var contents = $('.wk-order-list-contents');
			contents[0].innerHTML = "";
			var wk_orderline_list = order.get_orderlines();
			self.pos._update_summary(contents, wk_orderline_list)
		}
		else {
			$('.wk_barcode_screen_status').removeClass('oe_green');
			$($(".product-screen .rightpane")).show()
			$(".product-screen .rightpane.wk_barcode_screen").hide()
			$('.wk_image_box').attr("style", "display: none !important");
			$('.order-container').attr("style", "display: block !important");
			$('.order-summary').attr("style", "display: block !important");
			if (order.get_selected_orderline() && order.get_selected_orderline().product_id) {
				let product = order.get_selected_orderline().product_id;
				$(".wk_cart_product").attr("src", self.get_selected_line_product_url(product));
				$(".wk_selected_product_name").text(product.display_name);
				if (product.description_sale) {
					$(".wk_product_description").show();
					$(".wk_product_description .product_desc").text(product.description_sale);
				}
				else
					$(".wk_product_description").hide();
			}
		}
		this.pos.show_barcode_screen = !this.pos.show_barcode_screen;
	},
	get_selected_line_product_url(product) {
		if (product) {
			return (
				(
					`/web/image?model=product.product&field=image_128&id=${product.id}&unique=${product.write_date}`)
			);
		}
		else {
			return;
		}
	},
})
patch(PosStore.prototype, {
	async _update_summary(contents, wk_orderline_list) {
		var self = this;
		contents[0].innerHTML = "";
		wk_orderline_list.forEach(function (orderline) {
			var orderline_html = renderToString('pos_barcode_screen.Wk-OrderLine', {
				widget: self,
				wk_orderline: orderline
			});
			var wk_orderline = Object.assign(document.createElement("tbody"), { orderline_html });
			wk_orderline.innerHTML = orderline_html;
			wk_orderline = wk_orderline.childNodes[0];
			orderline.wk_node = wk_orderline;
			var el_lot_icon = wk_orderline.querySelector('.line-lot-icon');
			if (el_lot_icon) {
				el_lot_icon.addEventListener('click', (function () {
				}.bind(this)));
			}
			if (orderline.selected) {
				$('.wk-order-line.wk_highlight').removeClass('wk_highlight');
				$(wk_orderline).addClass('wk_highlight');
			}
			contents[0].appendChild(wk_orderline);
		});
		var order = self.get_order();
		var total = order ? order.get_total_with_tax() : 0;
		var taxes = order ? total - order.get_total_without_tax() : 0;
		$('.wk_summary .wk_entry .wk_total').text(this.env.utils.formatCurrency(total));
		$('.wk_summary .wk_entry .subentry.value').text(this.env.utils.formatCurrency(taxes));
	},
	async addLineToCurrentOrder(vals, opt = {}, configure = true) {
		var self = this;
		var result = await super.addLineToCurrentOrder(vals, opt, configure);
		var contents = $('.wk-order-list-contents');
		var wk_orderline_list = self.get_order().get_orderlines();
		await self._update_summary(contents, wk_orderline_list) 
		if (!this.show_barcode_screen && $('.wk_barcode_screen').is(":visible")) {
			$(".wk_barcode_screen_status.oe_icon.oe_green").click();
			$(".wk_barcode_screen_status.oe_icon").click();
		}
		return result

	},
});
patch(OrderSummary.prototype, {
	async _setValue(val) {
		const self = this;
		var result = super._setValue(...arguments);
		var contents = $('.wk-order-list-contents');
		var wk_orderline_list = self.pos.get_order().get_orderlines();
		self.pos._update_summary(contents, wk_orderline_list)
		return result
	}
}),
patch(PosOrderline.prototype, {
	setup(vals) {
		var result = super.setup(...arguments);
		this.wk_node =  null
		return result;
	},
});
patch(PosOrder.prototype, {
	removeOrderline(line) {
		super.removeOrderline(...arguments);
		if (line && line.wk_node)
			this.wk_remove_orderline(line.wk_node)
		if (line.length == 0) {
			$('.order-container').attr("style", "display: none !important");
		}
	},
	wk_remove_orderline(wk_node) {
		if (wk_node.parentNode)
			wk_node.parentNode.removeChild(wk_node);
	},
});
