import { localization as l10n } from "@web/core/l10n/localization";
import { insertThousandsSep } from "@web/core/utils/numbers";

export function humanNumberFormatter(number, options = {}) {
    const decimals = options.decimals || 0;
    const minDigits = options.minDigits || 1;
    const d2 = Math.pow(10, decimals);
    number = Math.round(number * d2) / d2;
    const sign = Math.sign(number);
    number = Math.abs(number);
    let symbol = "";
    for (const numberData of options.numberSystemData) {
        const s = Math.pow(10, numberData[0]);
        if (s <= number / Math.pow(10, minDigits - 1)) {
            number = Math.round((number * d2) / s) / d2;
            symbol = numberData[1];
            break;
        }
    }
    const { decimalPoint, grouping, thousandsSep } = l10n;
    const decimalsToKeep = number%1 === 0 ? 0 : decimals;
    number = sign * number;
    const [integerPart, decimalPart] = number.toFixed(decimalsToKeep).split(".");
    const int = insertThousandsSep(integerPart, thousandsSep, grouping);

    if (!decimalPart) {
        return int + symbol;
    }
    return int + decimalPoint + decimalPart + symbol;
}