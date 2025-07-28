import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

// Helper to parse currency string to float
function parseCurrency(val) {
    if (typeof val === "number") return val;
    if (!val) return 0;
    // Remove currency symbols, commas, spaces
    return parseFloat(val.replace(/[^\d\.\-]/g, "")) || 0;
}

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        result.headerData = result.headerData || {};
        const originalDate = new Date(result.date);
        const day = String(originalDate.getDate()).padStart(2, '0');
        const month = String(originalDate.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
        const year = originalDate.getFullYear();

        result.headerData.date = `${day}-${month}-${year}`;


        let real_lines = [];
        let global_discount = 0;
        let global_discount_percent = null;
        let orderline_discount = 0;
        let original_total = 0;
        for (const line of result.orderlines) {
            const name = line.productName || line.product_name || "";
            const price = parseCurrency(line.price);
            const unitPrice = parseCurrency(line.unitPrice);
            const priceWithoutDiscount = parseCurrency(line.price_without_discount) || unitPrice;
            const discount = parseFloat(line.discount) || 0;
            const qty = parseFloat(line.qty) || 1;

            // Global discount line
            if (
                name.toLowerCase().includes("discount") &&
                price < 0
            ) {
                global_discount += Math.abs(price);
                // Try to get percent from line.discount
                if (line.discount && line.discount > 0) {
                    global_discount_percent = line.discount;
                }
                // Fallback: Try to extract from name (if custom naming)
                const percentMatch = name.match(/(\d+(\.\d+)?)\s*%/);
                if (!global_discount_percent && percentMatch) {
                    global_discount_percent = percentMatch[1];
                }
            } else {
                // Calculate per-line discount amount using original price
                let discount_amount = 0;
                if (discount > 0) {
                    discount_amount = (priceWithoutDiscount * qty) * (discount / 100);
                    orderline_discount += discount_amount;
                }
                // Sum original price (before any discount)
                original_total += priceWithoutDiscount * qty;
                real_lines.push({
                    ...line,
                    discount_amount: discount_amount,
                    original_unit_price: priceWithoutDiscount,
                    original_line_total: priceWithoutDiscount * qty,
                });
            }
        }
        if (!global_discount_percent && this.global_discount && this.global_discount > 0) {
            global_discount_percent = this.global_discount;
        }
        // Final fallback: calculate from values
        if (!global_discount_percent && global_discount && original_total) {
             global_discount_percent = ((global_discount / original_total) * 100).toFixed(2);
        }

        result.real_orderlines = real_lines;
        result.total_discount = global_discount + orderline_discount;
        result.global_discount_percent = global_discount_percent;
        result.original_total = original_total;

        console.log('result',  result.headerData)
        console.log('Real Orderlines',result.real_orderlines)
        console.log('global_discount_percent ', result.global_discount_percent )
        console.log('Toatal discounts',result.total_discount)
        console.log('ressssssssssssssssslt',result)

        return result;
    },
});