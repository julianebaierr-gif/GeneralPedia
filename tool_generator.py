# -*- coding: utf-8 -*-
"""
Interactive Tool & Calculator Engine for GeneralPedia.
Detects calculator, tool, conversion, estimator, and lookup keywords
and generates self-contained, responsive, client-side interactive widgets
with real-time calculation, instant DOM updates, and professional UI.
"""
import re

CALCULATOR_KEYWORDS = [
    "calculator", "tool", "converter", "conversion", "estimator",
    "lookup", "payoff", "amortization", "payment", "interest",
    "tracker", "bmi", "mortgage", "loan", "tax", "percentage",
    "countdown", "counter", "generator", "formula"
]

def is_tool_or_calculator_topic(primary_kw, semantic_kws=None):
    """
    Determines if a topic warrants an embedded interactive tool or calculator.
    """
    text = (primary_kw or "").lower()
    if any(k in text for k in CALCULATOR_KEYWORDS):
        return True
    if semantic_kws:
        for sk in semantic_kws:
            sk_lower = (sk or "").lower()
            if any(k in sk_lower for k in CALCULATOR_KEYWORDS):
                return True
    return False

def generate_interactive_tool_html(primary_kw):
    """
    Generates tailored, beautiful, 100% self-contained interactive widget HTML + JS.
    Supports:
    1. Loan Payoff / Debt / Mortgage / Amortization Calculator
    2. Currency / Unit / Temperature / Weight Converter
    3. Health / BMI / Calorie / Metabolic Estimator
    4. Percentage / Tax / Financial Growth Estimator fallback
    """
    kw = (primary_kw or "").lower()

    # 1. Loan Payoff / Mortgage / Auto Loan / Debt Calculator
    if any(term in kw for term in ["loan", "payoff", "mortgage", "debt", "interest", "payment", "car loan", "auto loan"]):
        return '''
<div class="gp-interactive-tool-box" id="gp-loan-calculator">
    <div class="gp-tool-header">
        <h3 class="gp-tool-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M7 15h0M2 9.5h20"/></svg>
            Interactive Loan Payoff Calculator
        </h3>
        <span class="gp-tool-badge">Live Tool</span>
    </div>
    <div class="gp-tool-grid">
        <div class="gp-tool-group">
            <label class="gp-tool-label">Remaining Balance ($)</label>
            <input type="number" id="gp-calc-balance" class="gp-tool-input" value="18500" min="100" step="100" oninput="calculateLoanPayoff()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Annual Interest Rate (%)</label>
            <input type="number" id="gp-calc-rate" class="gp-tool-input" value="6.5" min="0.1" max="99" step="0.1" oninput="calculateLoanPayoff()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Monthly Payment ($)</label>
            <input type="number" id="gp-calc-payment" class="gp-tool-input" value="450" min="10" step="10" oninput="calculateLoanPayoff()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Extra Monthly Payment ($)</label>
            <input type="number" id="gp-calc-extra" class="gp-tool-input" value="100" min="0" step="25" oninput="calculateLoanPayoff()">
        </div>
    </div>
    <button type="button" class="gp-tool-btn" onclick="calculateLoanPayoff()">Recalculate Payoff Schedule</button>
    <div class="gp-tool-results">
        <div class="gp-result-item">
            <span class="gp-result-label">Time to Debt Free</span>
            <span class="gp-result-value" id="gp-res-months">38 Months</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">Total Interest Paid</span>
            <span class="gp-result-value" id="gp-res-interest">$2,415</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">Interest Saved with Extra</span>
            <span class="gp-result-value" style="color: #10b981;" id="gp-res-savings">$890</span>
        </div>
    </div>
    <p class="gp-tool-note">Note: Figures represent standard compound amortization. Actual lender calculations may slightly vary based on daily accrual rules.</p>
</div>
<script>
function calculateLoanPayoff() {
    var bal = parseFloat(document.getElementById('gp-calc-balance').value) || 0;
    var rate = (parseFloat(document.getElementById('gp-calc-rate').value) || 0) / 100 / 12;
    var pmt = parseFloat(document.getElementById('gp-calc-payment').value) || 0;
    var extra = parseFloat(document.getElementById('gp-calc-extra').value) || 0;

    var totalPmt = pmt + extra;
    if (bal <= 0 || totalPmt <= 0) return;

    var monthlyInterest = bal * rate;
    if (totalPmt <= monthlyInterest) {
        document.getElementById('gp-res-months').innerText = "Payment too low";
        document.getElementById('gp-res-interest').innerText = "Accruing";
        document.getElementById('gp-res-savings').innerText = "$0";
        return;
    }

    function runSim(principal, monthlyPmt) {
        var b = principal;
        var totalInt = 0;
        var m = 0;
        while (b > 0 && m < 600) {
            m++;
            var intr = b * rate;
            totalInt += intr;
            b = (b + intr) - monthlyPmt;
        }
        return { months: m, interest: totalInt };
    }

    var standard = runSim(bal, pmt);
    var accelerated = runSim(bal, totalPmt);

    var y = Math.floor(accelerated.months / 12);
    var remM = accelerated.months % 12;
    var timeStr = y > 0 ? (y + " yr " + remM + " mo") : (remM + " Months");

    var savings = Math.max(0, standard.interest - accelerated.interest);

    document.getElementById('gp-res-months').innerText = timeStr;
    document.getElementById('gp-res-interest').innerText = "$" + Math.round(accelerated.interest).toLocaleString();
    document.getElementById('gp-res-savings').innerText = "$" + Math.round(savings).toLocaleString();
}
if (typeof calculateLoanPayoff === 'function') calculateLoanPayoff();
</script>
'''

    # 2. Conversion / Unit / Length / Weight / Currency Tool
    elif any(term in kw for term in ["converter", "convert", "conversion", "units", "currency", "mileage", "metric"]):
        return '''
<div class="gp-interactive-tool-box" id="gp-converter-tool">
    <div class="gp-tool-header">
        <h3 class="gp-tool-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 16V4M7 4L3 8M7 4L11 8M17 8V20M17 20L21 16M17 20L13 16"/></svg>
            Universal Measurement &amp; Unit Converter
        </h3>
        <span class="gp-tool-badge">Quick Tool</span>
    </div>
    <div class="gp-tool-grid">
        <div class="gp-tool-group">
            <label class="gp-tool-label">Input Value</label>
            <input type="number" id="gp-conv-input" class="gp-tool-input" value="100" oninput="runUnitConvert()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Conversion Category</label>
            <select id="gp-conv-cat" class="gp-tool-select" onchange="updateConvertUnits()">
                <option value="length">Distance / Length (Miles vs KM)</option>
                <option value="weight">Weight / Mass (Pounds vs KG)</option>
                <option value="fuel">Fuel Economy (MPG vs L/100km)</option>
                <option value="speed">Speed (MPH vs KM/H)</option>
            </select>
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Direction</label>
            <select id="gp-conv-dir" class="gp-tool-select" onchange="runUnitConvert()">
                <option value="forward">Imperial to Metric</option>
                <option value="reverse">Metric to Imperial</option>
            </select>
        </div>
    </div>
    <div class="gp-tool-results">
        <div class="gp-result-item">
            <span class="gp-result-label">Converted Output</span>
            <span class="gp-result-value" id="gp-conv-output">160.93 km</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">Formula / Multiplier</span>
            <span class="gp-result-value" style="font-size: 1.1rem; color: var(--text-main);" id="gp-conv-formula">1 Mile = 1.60934 Kilometers</span>
        </div>
    </div>
</div>
<script>
function runUnitConvert() {
    var val = parseFloat(document.getElementById('gp-conv-input').value) || 0;
    var cat = document.getElementById('gp-conv-cat').value;
    var dir = document.getElementById('gp-conv-dir').value;
    var outEl = document.getElementById('gp-conv-output');
    var formEl = document.getElementById('gp-conv-formula');

    if (cat === 'length') {
        if (dir === 'forward') {
            outEl.innerText = (val * 1.60934).toFixed(2) + " Kilometers";
            formEl.innerText = "Value × 1.60934";
        } else {
            outEl.innerText = (val / 1.60934).toFixed(2) + " Miles";
            formEl.innerText = "Value ÷ 1.60934";
        }
    } else if (cat === 'weight') {
        if (dir === 'forward') {
            outEl.innerText = (val * 0.453592).toFixed(2) + " Kilograms";
            formEl.innerText = "Pounds × 0.453592";
        } else {
            outEl.innerText = (val / 0.453592).toFixed(2) + " Pounds";
            formEl.innerText = "Kilograms ÷ 0.453592";
        }
    } else if (cat === 'fuel') {
        if (dir === 'forward') {
            var l = val > 0 ? (235.215 / val).toFixed(1) : 0;
            outEl.innerText = l + " L/100km";
            formEl.innerText = "235.215 ÷ MPG";
        } else {
            var mpg = val > 0 ? (235.215 / val).toFixed(1) : 0;
            outEl.innerText = mpg + " MPG";
            formEl.innerText = "235.215 ÷ (L/100km)";
        }
    } else if (cat === 'speed') {
        if (dir === 'forward') {
            outEl.innerText = (val * 1.60934).toFixed(1) + " km/h";
            formEl.innerText = "MPH × 1.60934";
        } else {
            outEl.innerText = (val / 1.60934).toFixed(1) + " mph";
            formEl.innerText = "km/h ÷ 1.60934";
        }
    }
}
function updateConvertUnits() { runUnitConvert(); }
runUnitConvert();
</script>
'''

    # 3. Health / BMI / Nutrition / Symptom Estimator
    elif any(term in kw for term in ["health", "bmi", "calorie", "symptom", "blood pressure", "heart rate", "weight loss"]):
        return '''
<div class="gp-interactive-tool-box" id="gp-health-calculator">
    <div class="gp-tool-header">
        <h3 class="gp-tool-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            Clinical BMI &amp; Metabolic Metric Estimator
        </h3>
        <span class="gp-tool-badge">Health Utility</span>
    </div>
    <div class="gp-tool-grid">
        <div class="gp-tool-group">
            <label class="gp-tool-label">Height (Inches or CM)</label>
            <input type="number" id="gp-bmi-height" class="gp-tool-input" value="68" placeholder="e.g. 68 inches (5\'8)" oninput="calcBMI()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Weight (Pounds)</label>
            <input type="number" id="gp-bmi-weight" class="gp-tool-input" value="160" placeholder="e.g. 160 lbs" oninput="calcBMI()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Unit Standard</label>
            <select id="gp-bmi-unit" class="gp-tool-select" onchange="calcBMI()">
                <option value="us">US Standard (Inches / Pounds)</option>
                <option value="metric">Metric (Centimeters / KG)</option>
            </select>
        </div>
    </div>
    <div class="gp-tool-results">
        <div class="gp-result-item">
            <span class="gp-result-label">Calculated BMI</span>
            <span class="gp-result-value" id="gp-res-bmi">24.3</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">WHO Weight Category</span>
            <span class="gp-result-value" style="color: #10b981; font-size: 1.25rem;" id="gp-res-category">Healthy Weight</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">Recommended Healthy Range</span>
            <span class="gp-result-value" style="font-size: 1.15rem; color: var(--text-main);" id="gp-res-range">122 - 164 lbs</span>
        </div>
    </div>
    <p class="gp-tool-note">Disclaimer: Body Mass Index (BMI) provides a screening benchmark. It does not measure body fat directly or replace personalized clinical evaluations.</p>
</div>
<script>
function calcBMI() {
    var h = parseFloat(document.getElementById('gp-bmi-height').value) || 0;
    var w = parseFloat(document.getElementById('gp-bmi-weight').value) || 0;
    var unit = document.getElementById('gp-bmi-unit').value;
    var bmi = 0;

    if (h <= 0 || w <= 0) return;

    if (unit === 'us') {
        bmi = (w / (h * h)) * 703;
    } else {
        var m = h / 100;
        bmi = w / (m * m);
    }

    var bmiRounded = Math.round(bmi * 10) / 10;
    document.getElementById('gp-res-bmi').innerText = bmiRounded;

    var catEl = document.getElementById('gp-res-category');
    if (bmi < 18.5) {
        catEl.innerText = "Underweight";
        catEl.style.color = "#3b82f6";
    } else if (bmi < 25) {
        catEl.innerText = "Normal / Healthy Weight";
        catEl.style.color = "#10b981";
    } else if (bmi < 30) {
        catEl.innerText = "Overweight";
        catEl.style.color = "#f59e0b";
    } else {
        catEl.innerText = "Obese Range";
        catEl.style.color = "#ef4444";
    }
}
calcBMI();
</script>
'''

    # 4. Percentage / Tax / Financial Growth Estimator fallback
    else:
        template = '''
<div class="gp-interactive-tool-box" id="gp-general-calculator">
    <div class="gp-tool-header">
        <h3 class="gp-tool-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            Interactive {kw_title} Decision Tool
        </h3>
        <span class="gp-tool-badge">Decision Tool</span>
    </div>
    <div class="gp-tool-grid">
        <div class="gp-tool-group">
            <label class="gp-tool-label">Baseline Amount ($)</label>
            <input type="number" id="gp-gen-base" class="gp-tool-input" value="5000" oninput="runGeneralCalc()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Adjustment Rate (%)</label>
            <input type="number" id="gp-gen-rate" class="gp-tool-input" value="7.5" step="0.5" oninput="runGeneralCalc()">
        </div>
        <div class="gp-tool-group">
            <label class="gp-tool-label">Timeline (Years / Terms)</label>
            <input type="number" id="gp-gen-years" class="gp-tool-input" value="3" min="1" max="50" oninput="runGeneralCalc()">
        </div>
    </div>
    <div class="gp-tool-results">
        <div class="gp-result-item">
            <span class="gp-result-label">Projected Outcome</span>
            <span class="gp-result-value" id="gp-gen-total">$6,211</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">Net Variance</span>
            <span class="gp-result-value" style="color: #10b981;" id="gp-gen-diff">+$1,211</span>
        </div>
        <div class="gp-result-item">
            <span class="gp-result-label">Annualized Return</span>
            <span class="gp-result-value" style="font-size: 1.15rem; color: var(--text-main);" id="gp-gen-annual">$2,070 / yr</span>
        </div>
    </div>
    <p class="gp-tool-note">Live interactive projection utility for <strong>{kw_title}</strong>.</p>
</div>
<script>
function runGeneralCalc() {
    var base = parseFloat(document.getElementById('gp-gen-base').value) || 0;
    var rate = (parseFloat(document.getElementById('gp-gen-rate').value) || 0) / 100;
    var yrs = parseFloat(document.getElementById('gp-gen-years').value) || 1;

    var total = base * Math.pow(1 + rate, yrs);
    var diff = total - base;
    var annual = yrs > 0 ? (total / yrs) : total;

    document.getElementById('gp-gen-total').innerText = "$" + Math.round(total).toLocaleString();
    document.getElementById('gp-gen-diff').innerText = (diff >= 0 ? "+$" : "-$") + Math.round(Math.abs(diff)).toLocaleString();
    document.getElementById('gp-gen-annual').innerText = "$" + Math.round(annual).toLocaleString() + " / yr";
}
runGeneralCalc();
</script>
'''
        return template.replace("{kw_title}", primary_kw)
