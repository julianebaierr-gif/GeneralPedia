import os

SITE_NAME = "GeneralPedia"
DOMAIN = "https://generalpedia.com"
TAGLINE = "The Complete Encyclopedia & Everyday Knowledge Hub"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_DIR = os.path.join(BASE_DIR, "data")
SITE_DIR = os.path.join(BASE_DIR, "site")

SPREADSHEET_ID = "1IDS7DUc4PrlYbxhKwlqsoeQK70JH10-M_Qq80zm_-b0"
SHEET_GID = "758476499"
APPS_SCRIPT_WEBHOOK_URL = os.environ.get("GENERALPEDIA_SHEET_WEBHOOK", "https://script.google.com/macros/s/AKfycbzP5tXwq7ESaDVZawatxxeUhl641F0LmJzeokAd_vTjgvPfLbAMBVsPpR9cP_2W9Psk5w/exec")

CATEGORIES = {
    "how-to": {
        "name": "How-To & Guides",
        "slug": "how-to",
        "color": "emerald",
        "description": "Step-by-step tutorials, actionable guides, and everyday solutions."
    },
    "finance": {
        "name": "Finance & Money",
        "slug": "finance",
        "color": "amber",
        "description": "Tax brackets, retirement accounts (Roth IRA, 401k), insurance, and loans."
    },
    "health": {
        "name": "Health & Wellness",
        "slug": "health",
        "color": "rose",
        "description": "Medical insights, symptoms breakdown, natural wellness, and body care."
    },
    "tools": {
        "name": "Calculators & Tools",
        "slug": "tools",
        "color": "indigo",
        "description": "Interactive financial calculators, measurement converters, and calendars."
    },
    "automotive": {
        "name": "Automotive",
        "slug": "automotive",
        "color": "cyan",
        "description": "Vehicle buying advice, repair guides, maintenance, and car comparisons."
    },
    "tech": {
        "name": "Tech & Digital",
        "slug": "tech",
        "color": "blue",
        "description": "Digital tools, cyber security explanations, software, and tech tips."
    },
    "lifestyle": {
        "name": "Home & Lifestyle",
        "slug": "lifestyle",
        "color": "teal",
        "description": "Home care, pet nutrition guides, recipes, and everyday living advice."
    },
    "culture": {
        "name": "Entertainment & Culture",
        "slug": "culture",
        "color": "purple",
        "description": "Major global events, movies, pop culture, and sports reviews."
    }
}
