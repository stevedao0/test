function viThreeDigits(n, full = false) {
  const ones = [
    "", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"
  ];

  const tram = Math.floor(n / 100);
  const chuc = Math.floor((n % 100) / 10);
  const donvi = n % 10;

  const parts = [];

  if (tram > 0 || full) {
    parts.push(`${ones[tram]} trăm`);
  }

  if (chuc === 0) {
    if (donvi !== 0 && (tram > 0 || full)) {
      parts.push("lẻ");
    }
  } else if (chuc === 1) {
    parts.push("mười");
  } else {
    parts.push(`${ones[chuc]} mươi`);
  }

  if (donvi === 0) {
    return parts.join(" ").trim();
  }

  if (donvi === 1) {
    if (chuc >= 2) {
      parts.push("mốt");
    } else {
      parts.push("một");
    }
    return parts.join(" ").trim();
  }

  if (donvi === 4) {
    if (chuc >= 2) {
      parts.push("tư");
    } else {
      parts.push("bốn");
    }
    return parts.join(" ").trim();
  }

  if (donvi === 5) {
    if (chuc >= 1) {
      parts.push("lăm");
    } else {
      parts.push("năm");
    }
    return parts.join(" ").trim();
  }

  parts.push(ones[donvi]);
  return parts.join(" ").trim();
}

function moneyToVietnameseWords(n) {
  if (n === 0) {
    return "Không đồng";
  }
  if (n < 0) {
    return "Âm " + moneyToVietnameseWords(-n);
  }

  const units = [
    [1000000000, "tỷ"],
    [1000000, "triệu"],
    [1000, "nghìn"]
  ];

  const parts = [];
  let remainder = n;
  let started = false;

  for (const [base, name] of units) {
    const block = Math.floor(remainder / base);
    remainder = remainder % base;

    if (block === 0) {
      continue;
    }

    started = true;
    parts.push(`${viThreeDigits(block, false)} ${name}`);
  }

  if (remainder > 0) {
    parts.push(viThreeDigits(remainder, started));
  }

  let text = parts.filter(p => p).join(" ").trim();
  if (text) {
    text = text[0].toUpperCase() + text.slice(1);
  }

  return `${text} đồng`;
}

function formatMoney(num) {
  return num.toLocaleString('vi-VN') + ' VNĐ';
}

function parseMoney(str) {
  return parseInt(str.replace(/[^\d]/g, '') || '0');
}

class MoneyCalculator {
  constructor(container) {
    this.container = container;
    this.preVatInput = container.querySelector('[data-money-input]');
    this.vatInput = container.querySelector('[data-vat-input]');
    this.preVatPreview = container.querySelector('[data-preview-pre-vat]');
    this.vatPreview = container.querySelector('[data-preview-vat]');
    this.totalPreview = container.querySelector('[data-preview-total]');
    this.wordsPreview = container.querySelector('[data-preview-words]');

    if (this.preVatInput) {
      this.init();
    }
  }

  init() {
    this.preVatInput.addEventListener('input', () => {
      this.formatInput(this.preVatInput);
      this.calculate();
    });

    if (this.vatInput) {
      this.vatInput.addEventListener('input', () => {
        this.calculate();
      });
    }

    this.calculate();
  }

  formatInput(input) {
    const cursorPosition = input.selectionStart;
    const oldLength = input.value.length;

    let value = input.value.replace(/[^\d]/g, '');
    if (value) {
      const numValue = parseInt(value);
      value = numValue.toLocaleString('vi-VN');
    }

    input.value = value;

    const newLength = input.value.length;
    const diff = newLength - oldLength;
    input.setSelectionRange(cursorPosition + diff, cursorPosition + diff);
  }

  calculate() {
    const preVat = parseMoney(this.preVatInput.value);
    const vatPercent = this.vatInput ? parseFloat(this.vatInput.value) || 0 : 0;

    const vat = Math.round(preVat * vatPercent / 100);
    const total = preVat + vat;

    if (this.preVatPreview) {
      this.preVatPreview.textContent = formatMoney(preVat);
    }

    if (this.vatPreview) {
      this.vatPreview.textContent = formatMoney(vat);
    }

    if (this.totalPreview) {
      this.totalPreview.textContent = formatMoney(total);
    }

    if (this.wordsPreview) {
      this.wordsPreview.textContent = moneyToVietnameseWords(total);
    }
  }
}

function initMoneyCalculators() {
  document.querySelectorAll('[data-money-calculator]').forEach(container => {
    new MoneyCalculator(container);
  });
}

if (typeof window !== 'undefined') {
  window.MoneyCalculator = MoneyCalculator;
  window.initMoneyCalculators = initMoneyCalculators;
  window.moneyToVietnameseWords = moneyToVietnameseWords;
  window.formatMoney = formatMoney;
  window.parseMoney = parseMoney;
}
