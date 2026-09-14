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

# Each category has a dedicated expert author with a real name, photo, and short bio.
AUTHORS = {
    "how-to": {
        "name": "Marcus Reid",
        "initials": "MR",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Senior technical writer specializing in step-by-step troubleshooting guides and practical DIY solutions."
    },
    "finance": {
        "name": "Sarah Mitchell",
        "initials": "SM",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Certified financial analyst covering tax strategy, retirement planning, and personal budgeting insights."
    },
    "health": {
        "name": "Elena Torres",
        "initials": "ET",
        "avatar": "https://images.unsplash.com/photo-1594824476967-48c8b964ac31?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Health science researcher and medical journalist writing evidence-based wellness and symptom guides."
    },
    "tools": {
        "name": "James Carter",
        "initials": "JC",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Data engineer and calculator developer building interactive financial and measurement reference tools."
    },
    "automotive": {
        "name": "David Chen",
        "initials": "DC",
        "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Automotive journalist with ten years of experience in vehicle diagnostics, specs, and market reviews."
    },
    "tech": {
        "name": "Ryan Kowalski",
        "initials": "RK",
        "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Software engineer and cybersecurity specialist explaining digital tools and emerging tech trends."
    },
    "lifestyle": {
        "name": "Nora Jacobs",
        "initials": "NJ",
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Home living editor covering pet nutrition, cleaning hacks, recipes, and everyday household advice."
    },
    "culture": {
        "name": "Amir Hassan",
        "initials": "AH",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&h=120&q=80",
        "bio": "Culture and entertainment critic reviewing global events, sports milestones, and film analysis."
    }
}
