# -*- coding: utf-8 -*-
"""
Dynamic Interactive Tool & Calculator Engine for GeneralPedia.
1. Strictly detects whether a keyword genuinely warrants an interactive tool.
2. Uses Gemini AI to dynamically generate a 100% bespoke, custom-built HTML & JavaScript widget
   specifically tailored for THAT exact keyword with real-time calculations.
3. No hardcoded templates or generic fallbacks. If it's not a real tool topic, returns None.
"""
import re
import json
import urllib.request
from env_loader import get_secret

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

STRICT_TOOL_PATTERNS = [
    r'\bcalculator\b',
    r'\bconverter\b',
    r'\bconversion\b',
    r'\bto\s+(inches|gallon|gallons|ml|liters|lbs|kg|cm|feet|meters|celsius|fahrenheit|cups|grams|ounces|oz)\b',
    r'\bestimator\b',
    r'\bamortization\b',
    r'\bdepth chart\b'
]

def is_tool_or_calculator_topic(primary_kw, semantic_kws=None):
    """
    STRICT check: Only returns True if the keyword explicitly requests an interactive tool,
    calculator, conversion, or lookup widget.
    Regular informational, culture, automotive reviews, or how-to guides return False.
    """
    text = (primary_kw or "").strip().lower()
    for pat in STRICT_TOOL_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def generate_interactive_tool_html(primary_kw, semantic_kws=None):
    """
    Generates a 100% customized, self-contained interactive widget (HTML + CSS + JavaScript)
    dynamically using Gemini AI for the specific keyword.
    Does NOT use any static templates.
    """
    if not is_tool_or_calculator_topic(primary_kw, semantic_kws):
        return None

    if not GEMINI_API_KEY:
        print("[Tool Generator] GEMINI_API_KEY missing, skipping widget generation.")
        return None

    prompt = f"""You are a senior UI/UX developer and mathematician creating an interactive, self-contained web tool for GeneralPedia.
Create a modern, fully functional, 100% client-side interactive tool for the exact topic:
"{primary_kw}"

REQUIREMENTS:
1. Wrap everything inside: <div class="gp-interactive-tool-box" id="gp-custom-tool"> ... </div>
2. Include:
   - Header with clear title and <span class="gp-tool-badge">Interactive Tool</span>
   - Input fields specifically for "{primary_kw}" (with correct labels, default values, min/max, steps)
   - Real-time or on-click calculation button: <button type="button" class="gp-tool-btn" onclick="runToolCalc()">Calculate</button>
   - Results dashboard showing specific output values (e.g. converted amounts, calculated formulas, summary breakdowns)
   - A brief informative note explaining the formula or data source
3. Include an embedded <script> block with JavaScript that:
   - Reads the input values
   - Performs accurate real-life mathematical calculations specifically for "{primary_kw}"
   - Updates the result DOM elements instantly with proper formatting
   - Calls the calculation function immediately on page load so results are visible right away
4. Use standard classes:
   - Container: .gp-interactive-tool-box
   - Header: .gp-tool-header, .gp-tool-title, .gp-tool-badge
   - Form grid: .gp-tool-grid
   - Form groups: .gp-tool-group, .gp-tool-label, .gp-tool-input, .gp-tool-select
   - Button: .gp-tool-btn
   - Results: .gp-tool-results, .gp-result-item, .gp-result-label, .gp-result-value
   - Note: .gp-tool-note
5. Return ONLY clean HTML and JS. Do not wrap in markdown quotes. Do not include <html>, <head>, or <body> tags.
"""

    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-flash-latest"
    ]

    for model_name in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 4096
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get('candidates', [])
                if not candidates:
                    continue
                parts = candidates[0].get('content', {}).get('parts', [])
                if not parts:
                    continue
                raw_html = parts[0].get('text', '').strip()
                clean_html = re.sub(r'^```html\s*', '', raw_html, flags=re.IGNORECASE)
                clean_html = re.sub(r'^```\s*', '', clean_html)
                clean_html = re.sub(r'```$', '', clean_html).strip()

                if '<div class="gp-interactive-tool-box"' in clean_html and '<script>' in clean_html and '</script>' in clean_html and '</div>' in clean_html:
                    print(f"[Tool Generator] Successfully generated 100% custom AI interactive tool for '{primary_kw}' using {model_name}")
                    return clean_html
                else:
                    print(f"[Tool Generator] Model {model_name} generated incomplete tool HTML (missing closing tags), trying next fallback...")
        except Exception as e:
            print(f"[Tool Generator Warning] {model_name} failed: {e}. Trying fallback...")
            continue

    return None
