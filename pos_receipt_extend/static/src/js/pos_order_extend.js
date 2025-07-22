
/** @odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

export class PosOrderWithTax extends PosOrder {
    getSortedOrderlines() {
        const sortedLines = super.getSortedOrderlines();
        console.log('Original sorted lines:', sortedLines);

        // Add tax information to each line
        const enhancedLines = sortedLines.map(line => {
            const lineData = line.getDisplayData ? line.getDisplayData() : line;
            const taxes = line.get_all_prices ? line.get_all_prices().taxesData : [];

            console.log('Line taxes:', taxes);

            return {
                ...lineData,
                line_taxes: taxes.map(taxData => ({
                    name: taxData.tax.name,
                    amount: taxData.tax.amount,
                    percentage: taxData.tax.amount + '%'
                }))
            };
        });

        console.log('Enhanced sorted lines:', enhancedLines);
        return enhancedLines;
    }
}

// Register the new class in the registry, replacing the original
import { registry } from "@web/core/registry";
registry.category("pos_available_models").add(PosOrderWithTax.pythonModel, PosOrderWithTax);