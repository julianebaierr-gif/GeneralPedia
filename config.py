import os

SITE_NAME = "GeneralPedia"
DOMAIN = "https://www.generalpedia.com"
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

# Each category has a dedicated expert author with a real name, photo, role, and comprehensive E-E-A-T profile.
AUTHORS = {
    "how-to": {
        "name": "Marcus Reid",
        "initials": "MR",
        "role": "Senior Technical Writer & DIY Systems Editor",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "Marcus Reid leads the How-To & Tutorials desk at GeneralPedia, focusing on actionable DIY repairs, appliance diagnostics, technical troubleshooting protocols, and step-by-step consumer workflows. With over a decade of hands-on experience evaluating mechanical systems and home maintenance workflows, Marcus specializes in deconstructing complex repair procedures into accessible, safety-first tutorials. Every instructional guide published under his supervision undergoes rigorous bench testing and step-by-step verification to ensure reliability, tool clarity, and safety for readers of all technical skill levels.",
        "experience": "12+ years experience in technical troubleshooting, appliance diagnosis, and DIY guide creation.",
        "expertise": ["Home Appliance Diagnostics", "Step-by-Step DIY Tutorials", "Hardware Troubleshooting", "Preventive Maintenance", "Safety Protocols"],
        "editorial_standards": "All repair manuals require hands-on verification, required tool checklists, clear hazard warnings, and diagnostic logic trees before publication."
    },
    "finance": {
        "name": "Sarah Mitchell",
        "initials": "SM",
        "role": "Certified Financial Analyst & Tax Strategy Editor",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "Sarah Mitchell directs financial analysis and tax research at GeneralPedia. She specializes in clarifying complex IRS tax codes, statutory retirement vehicles (401(k), Roth IRA, SEP-IRA), capital gains management, and household budgeting frameworks. Prior to joining GeneralPedia, Sarah managed private wealth portfolios and contributed quantitative economic research to financial advisory journals. Her writing empowers readers to make informed, data-driven decisions that safeguard their financial independence and optimize their long-term tax efficiency.",
        "experience": "14+ years in personal wealth management, statutory tax compliance, and retirement investment analysis.",
        "expertise": ["IRS Tax Brackets & Deadlines", "Retirement Planning (401k & Roth IRA)", "Capital Gains & Investment Strategy", "Debt Management", "Personal Budgeting"],
        "editorial_standards": "Strict adherence to official IRS statutory publications, empirical economic data, and transparent financial scenario modeling."
    },
    "health": {
        "name": "Elena Torres",
        "initials": "ET",
        "role": "Health Science Researcher & Clinical Wellness Editor",
        "avatar": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "Elena Torres oversees health, clinical wellness, and symptom analysis content at GeneralPedia. Drawing on extensive experience in biomedical research and public health communication, Elena translates complex clinical studies into clear, actionable health guides. Her work emphasizes preventative care, evidence-based lifestyle interventions, and objective symptom timelines. She collaborates closely with medical advisory standards to ensure all health documentation adheres strictly to recognized peer-reviewed medical literature and official health agency guidance.",
        "experience": "9+ years in clinical journalism, biomedical research analysis, and public health communication.",
        "expertise": ["Clinical Wellness Summaries", "Symptom Progression Timelines", "Preventative Healthcare", "Evidence-Based Nutrition", "Public Health Guidelines"],
        "editorial_standards": "Grounded entirely in peer-reviewed clinical literature (PubMed, CDC, WHO) with verified medical disclaimers and multi-stage fact checking."
    },
    "tools": {
        "name": "James Carter",
        "initials": "JC",
        "role": "Senior Data Systems Engineer & Calculator Developer",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "James Carter is the lead systems architect and calculation developer for GeneralPedia's interactive tools directory. With a strong background in software engineering and applied mathematics, James designs and audits the algorithms powering our financial calculators, telecommunication directory lookups, conversion tools, and date calculators. He ensures that every computational engine on the platform executes with mathematical precision, instant latency, and complete transparency regarding underlying formulas.",
        "experience": "11+ years in computational algorithms, telecommunication routing systems, and interactive calculation engines.",
        "expertise": ["Interactive Financial Engines", "Telecommunication Routing & Area Codes", "Conversion Algorithms", "Measurement Standards", "Computational Modeling"],
        "editorial_standards": "Rigorous formula validation, edge-case testing, and real-time execution accuracy across all modern web browsers."
    },
    "automotive": {
        "name": "David Chen",
        "initials": "DC",
        "role": "Automotive Specialist & Vehicle Diagnostics Journalist",
        "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "David Chen is the automotive editor at GeneralPedia, providing comprehensive vehicle reviews, trim level comparisons, mechanical diagnostic procedures, and long-term ownership cost analyses. Having road-tested hundreds of vehicles and investigated automotive engineering advancements from hybrid powertrains to electric architectures, David delivers unvarnished, data-rich assessments to help buyers and vehicle owners make informed maintenance and purchasing choices.",
        "experience": "10+ years in automotive road testing, powertrain engineering review, and OBD-II diagnostics.",
        "expertise": ["Powertrain & Hybrid Technology", "Vehicle Trim Comparisons", "OBD-II Fault Diagnostics", "Fuel Economy Benchmarks", "Pre-Purchase Inspection Checklists"],
        "editorial_standards": "Objective manufacturer specification benchmarking, real-world road test verification, and certified diagnostic protocols."
    },
    "lifestyle": {
        "name": "Nora Jacobs",
        "initials": "NJ",
        "role": "Home Living & Pet Care Editorial Specialist",
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "Nora Jacobs is the lifestyle and home care editor at GeneralPedia. She focuses on practical home management, veterinarian-approved pet nutrition guides, sustainable cleaning methodologies, and indoor environmental quality. Nora works directly with reference materials and animal safety guidelines to ensure every household tip and pet food safety analysis is vetted for safety, practical efficacy, and environmental consciousness.",
        "experience": "9+ years in lifestyle journalism, household management, veterinary nutrition research, and sustainable home care.",
        "expertise": ["Pet Nutrition & Toxic Foods Reference", "Sustainable Household Cleaning", "Indoor Air Quality", "Seasonal Home Maintenance", "Family Living Strategies"],
        "editorial_standards": "Veterinary dietary safety cross-referencing, non-toxic household formulations, and practical implementation guidelines."
    },
    "culture": {
        "name": "Amir Hassan",
        "initials": "AH",
        "role": "Cultural Historian & Sports Milestone Analyst",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=240&h=240&q=85",
        "bio": "Amir Hassan heads the culture, sports, and entertainment desk at GeneralPedia. He chronicles major global sports events, cultural traditions, holiday histories, and milestones in modern entertainment. With a background in cultural historiography, Amir contextualizes current sporting tournaments and societal events within their broader historical frameworks, delivering engaging, well-researched retrospective analyses and event guides.",
        "experience": "10+ years in cultural archiving, international sporting retrospectives, and entertainment journalism.",
        "expertise": ["International Sporting Tournaments", "Historical Cultural Traditions", "Holiday Origins & Statutory Recognitions", "Media & Entertainment Retrospectives"],
        "editorial_standards": "Primary source verification, chronological timeline mapping, and balanced cultural commentary."
    }
}
