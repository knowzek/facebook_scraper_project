# constants.py

TITLE_KEYWORD_TO_CATEGORY_RAW = {
    "storytime": "List - Storytimes",
    "Story Time": "List - Storytimes",
    "Storytime": "List - Storytimes",
    "babies in bloom": "List - Storytimes",
    "Kids": "Audience - School Age",
    "math": "List - STEM/STEAM",
    "science": "List - STEM/STEAM",
    "nature": "List - STEM/STEAM",
    "STEM": "List - STEM/STEAM",
    "lego": "List - STEM/STEAM",
    "chess": "List - STEM/STEAM",
    "baby": "Audience - Parent & Me",
    "babies": "Audience - Parent & Me",
    "toddler": "Audience - Toddler/Infant, Audience - Parent & Me, List - Toddler Time Events",
    "preschool": "Audience - Preschool Age",
    "tiny tot": "Audience - Toddler/Infant, Audience - Parent & Me",
    "steam": "List - STEM/STEAM",
    "pride": "List - PRIDE Events",
    "computers": "List - STEM/STEAM",
    "yoga": "Category - Fitness Events",
    "food distribution": "List - Food Distribution",
    "homeschool": "List - Homeschool",
    "KINDERSTEM": "List - STEM/STEAM, Audience - Preschool Age",
    "SPR": "Audience - Special Events, List - STEM/STEAM",
    "Build Bash": "List - STEM/STEAM",
    "Active": "List - Fitness Events",
    "Dance": "List - Fitness Events",
    "Dancing": "List - Fitness Events",
    "neurodiverse": "Audience - Special Needs, List - Special Needs Events",
    "neurodiversity": "Audience - Special Needs, List - Special Needs Events",
    "asd": "Audience - Special Needs, List - Special Needs Events",
    "sensory": "Audience - Special Needs, List - Special Needs Events",
    "sensory-friendly": "Audience - Special Needs, List - Special Needs Events",
    "LGBTQ+": "List - PRIDE Events",
    "Trans": "List - PRIDE Events",
    "Rainbow Family": "List - PRIDE Events",
    "Rainbow Families": "List - PRIDE Events",
    "theater": "Audience - Special Events",
    "Magician": "Audience - Special Events",
    "juggler": "Audience - Special Events",
    "Mom": "Audience - Parent & Me",
    "Mother": "Audience - Parent & Me",
    "Father": "Audience - Parent & Me",
    "caregiver": "Audience - Parent & Me",
    "dad": "Audience - Parent & Me",
    "weather": "Audience – Outdoor Event",
    "train": "List – Events with Trains",
    "Volunteer": "List – Youth Volunteer Opportunities",
    "free": "Audience – Free Event",
    "all ages": "Audience – Family Event",
    "fireworks": "List – Fireworks",
    "parade": "List – Parades",
    "infant": "Audience - Toddler/Infant",
    "tween": "Audience – School Age",
    "PNO": "List – Parents Night Out",
    "Era": "List – Swiftie Events",
    "Potter": "List – Wizard Events",
    "Harry Potter": "List – Wizard Events",
    "high school": "Audience – Teens"
}

TITLE_KEYWORD_TO_CATEGORY = {k.lower(): v for k, v in TITLE_KEYWORD_TO_CATEGORY_RAW.items()}

COMBINED_KEYWORD_TO_CATEGORY_RAW = {
    ("storytime", "toddler"): "List - Toddler Time Events, Audience - Family Event, Audience - Toddler/Infant, List - Storytimes",
    ("storytime", "baby"): "Audience - Toddler/Infant, List - Storytimes, Audience - Family Event",
    ("storytime", "infant"): "Audience - Toddler/Infant, List - Storytimes, Audience - Family Event",
    ("story time", "toddler"): "List - Toddler Time Events, Audience - Family Event, Audience - Toddler/Infant, List - Storytimes",
    ("story time", "baby"): "Audience - Toddler/Infant, List - Storytimes, Audience - Family Event",
    ("story time", "infant"): "Audience - Toddler/Infant, List - Storytimes, Audience - Family Event"
}

COMBINED_KEYWORD_TO_CATEGORY = {
    (kw1.lower(), kw2.lower()): cat
    for (kw1, kw2), cat in COMBINED_KEYWORD_TO_CATEGORY_RAW.items()
}

UNWANTED_TITLE_KEYWORDS = [
    "summer meals",
    "Summer Meals",
    "adult"
]

FACEBOOK_LOCATION_MAP = {
    "Rosemont Elementary": "Rosemont Elementary School",
    "College Park Elementary": "College Park Elementary School",
    "Williams Farm": "Williams Farm Park",
}

LIBRARY_CONSTANTS = {
    "vbpl": {
        "program_type_to_categories": {
            "Storytimes & Early Learning": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event, List - Storytimes",
            "STEAM": "Event Location - Virginia Beach, List - STEM/STEAM, Audience - Free Event, Audience - Family Event",
            "Computers & Technology": "Event Location - Virginia Beach, Audience - Free Event, Audience - Teens, Audience - Family Event",
            "Workshops & Lectures": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event",
            "Discussion Groups": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event",
            "Arts & Crafts": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event",
            "Hobbies": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event",
            "Books & Authors": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event",
            "Culture": "Event Location - Virginia Beach, Audience - Free Event, Audience - Family Event",
            "History & Genealogy": "Event Location - Virginia Beach, Audience - Teens, Audience - Free Event"
        },
        "name_suffix_map": {
            "Oceanfront Area Library": "Oceanfront Area Library",
            "Meyera E. Oberndorf Central Library": "MEO Central Library",
            "TCC/City Joint-Use Library": "TCC Joint-Use Library",
            "Princess Anne Area Library": "Princess Anne Area Library",
            "Bayside Area Library": "Bayside Area Library",
            "Pungo-Blackwater Library": "Pungo Blackwater Library",
            "Windsor Woods Area Library": "Windsor Woods Area Library",
            "Great Neck Area Library": "Great Neck Area Library",
            "Kempsville Area Library": "Kempsville Area Library"
        },
        "venue_names": {
        "Meyera E. Oberndorf Central Library": "MEO Central Library",
        "TCC/City Joint-Use Library": "TCC Joint-Use Library",
        "Princess Anne Area Library": "Princess Anne Area Library",
        "Oceanfront Area Library": "Oceanfront Area Library",
        "Bayside Area Library": "Bayside Area Library",
        "Pungo-Blackwater Library": "Pungo Blackwater Library",
        "Windsor Woods Area Library": "Windsor Woods Area Library",
        "Great Neck Area Library": "Great Neck Area Library",
        "Kempsville Area Library": "Kempsville Area Library"
    },
        "event_name_suffix": " (Virginia Beach)"
    },
    
    "npl": {
        "age_to_categories": {
            "Family": "Audience - Free Event, Event Location - Norfolk, Audience - Family Event",
            "All Ages": "Audience - Free Event, Event Location - Norfolk",
            "Babies (0-2)": "Audience - Free Event, Event Location - Norfolk, Audience - Parent & Me, Audience - Toddler/Infant, List - Toddler Time Events",
            "Toddlers (2-3)": "Audience - Free Event, Event Location - Norfolk, Audience - Parent & Me, Audience - Toddler/Infant, List - Toddler Time Events",
            "Preschool (3-5)": "Audience - Free Event, Event Location - Norfolk, Audience - Parent & Me, Audience - Preschool Age",
            "Elementary School Age (5-9)": "Audience - Free Event, Event Location - Norfolk, Audience - School Age",
            "Tweens (9-13)": "Event Location - Norfolk, Audience - School Age, Audience - Free Event",
            "Teens (12-17)": "Audience - Teens, Event Location - Norfolk, Audience - Free Event"
        },
        "name_suffix_map": {
            "Mary D. Pretlow Anchor Branch Library": "Pretlow Library",
            "Barron F. Black Branch Library": "Barron F. Black Library",
            "Richard A. Tucker Memorial Library": "Tucker Library",
            "Larchmont Branch Library": "Larchmont Library",
            "Jordan-Newby Anchor Branch Library at Broad Creek": "Jordan-Newby Anchor Branch Library",
            "Blyden Branch Library": "Blyden Branch Library",
            "Lafayette Branch Library": "Lafayette Branch Library",
            "Van Wyck Branch Library": "Van Wyck Branch Library",
            "Downtown Branch at Slover": "Downtown Branch at Slover",
            "Park Place Branch Library": "Park Place Branch Library",
            "Little Creek Branch Library": "Little Creek Branch Library",
            "Janaf Branch Library": "Janaf Branch Library",
            "2nd Floor Program Room": "Downtown Branch at Slover",
            "2nd Floor Flex Room": "Downtown Branch at Slover",
            "5th Floor Main": "Downtown Branch at Slover",
            "2nd Floor Fish Bowl": "Downtown Branch at Slover",
            "Collaboration Room": "Tucker Library"
        },
        "venue_names": {
            "Richard A. Tucker Memorial Library": "Richard A. Tucker Memorial Library",
            "Barron F. Black Branch Library": "Barron F. Black Branch, Norfolk Public Library",
            "Mary D. Pretlow Anchor Branch Library": "Pretlow Branch Library",
            "Jordan-Newby Anchor Branch Library at Broad Creek": "Jordan-Newby Anchor Branch Library at Broad Creek",
            "Blyden Branch Library": "Blyden Branch Library",
            "Lafayette Branch Library": "Lafayette Branch, Norfolk Public Library",
            "Larchmont Branch Library": "Larchmont Branch Library, Norfolk Public Library",
            "Van Wyck Branch Library": "Van Wyck Branch, Norfolk Public Library",
            "Downtown Branch at Slover": "The Slover / Downtown Branch Library",
            "Park Place Branch Library": "Park Place Branch Library",
            "Little Creek Branch Library": "Little Creek Branch, Norfolk Public Library",
            "Janaf Branch Library": "Janaf Branch, Norfolk Public Library",
            "2nd Floor Program Room": "The Slover / Downtown Branch Library",
            "2nd Floor Flex Room": "The Slover / Downtown Branch Library",
            "5th Floor Main": "The Slover / Downtown Branch Library",
            "2nd Floor Fish Bowl": "The Slover / Downtown Branch Library",
            "Collaboration Room": "Richard A. Tucker Memorial Library",
            "Larchmont@Lambert": "Lambert’s Point Recreation Center"
        },
        "event_name_suffix": " (Norfolk)",
    },
    "chpl": {
        "age_to_categories": {
            "Preschool": "Audience - Preschool Age, Audience - Free Event, Event Location - Chesapeake, Audience - Parent & Me",
            "Elementary School": "Audience - School Age, Audience - Free Event, Event Location - Chesapeake",
            "Middle School": "Audience - Teens, Audience - Free Event, Audience - School Age, Event Location - Chesapeake",
            "High School": "Audience - Teens, Audience - Free Event, Audience - School Age, Event Location - Chesapeake",
            "Families": "Audience - Family Event, Audience - Free Event, Event Location - Chesapeake",
            "All Ages": "Audience - Free Event, Event Location - Chesapeake",
            "Adult": "Audience - Free Event, Event Location - Chesapeake"
        },
        "name_suffix_map": {
            "Dr. Clarence V. Cuffee Outreach and Innovation Library": "Cuffee Library",
            "Greenbrier Library": "Greenbrier Library",
            "Russell Memorial Library": "Russell Memorial Library",
            "Central Library": "Chesapeake Central Library",
            "Indian River Library": "Indian River Library",
            "South Norfolk Memorial Library": "South Norfolk Memorial Library",
            "Major Hillard Library": "Major Hillard Library"
        },
        "venue_names": {
            "Dr. Clarence V. Cuffee Outreach and Innovation Library": "Dr. Clarence V. Cuffee Outreach & Innovation Library",
            "Greenbrier Library": "Greenbrier Library",
            "Russell Memorial Library": "Russell Memorial Library",
            "Central Library": "Chesapeake Central Library",
            "Indian River Library": "Indian River Library",
            "South Norfolk Memorial Library": "South Norfolk Memorial Library",
            "Major Hillard Library": "Major Hillard Library"
        },
        "event_name_suffix": " (Chesapeake)",
    },
    "hpl": {
    "program_type_to_categories": {
        "storytime": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Storytimes, List - Toddler Time Events, Audience - Toddler/Infant",
        "lego": "Event Location - Hampton, Audience - Free Event, Audience - School Age, List - STEM/STEAM",
        "steam": "Event Location - Hampton, Audience - Free Event, Audience - School Age, List - STEM/STEAM",
        "slime": "Event Location - Hampton, Audience - Free Event, Audience - School Age, List - STEM/STEAM",
        "craft": "Event Location - Hampton, Audience - Free Event, Audience - Family Event",
        "painting": "Event Location - Hampton, Audience - Free Event, Audience - Family Event",
        "art": "Event Location - Hampton, Audience - Free Event, Audience - Family Event",
        "baking": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Cooking",
        "cookie": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Cooking",
        "cupcake": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Cooking",
        "sensory": "Event Location - Hampton, Audience - Free Event, Audience - Toddler/Infant, List - Toddler Time Events",
        "chalk": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Outdoor Activities",
        "bubble": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Outdoor Activities",
        "photography": "Event Location - Hampton, Audience - Free Event, Audience - Teens, List - STEM/STEAM",
        "writing": "Event Location - Hampton, Audience - Free Event, Audience - Teens, List - Creative Writing",
        "book club": "Event Location - Hampton, Audience - Free Event, Audience - Teens, List - Reading",
        "movie": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Movies",
        "game": "Event Location - Hampton, Audience - Free Event, Audience - School Age, List - Games & Activities",
        "trivia": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Games & Activities",
        "scavenger": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Games & Activities",
        "hunt": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Games & Activities",
        "music": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Music & Performance",
        "dance": "Event Location - Hampton, Audience - Free Event, Audience - Family Event, List - Music & Performance",
        "teen": "Event Location - Hampton, Audience - Free Event, Audience - Teens",
        "tween": "Event Location - Hampton, Audience - Free Event, Audience - School Age"
    },

    "location_map": {
        "Main Library": "Hampton Main Library",
        "Main Library First Floor": "Hampton Main Library",
        "Main Library Second Floor": "Hampton Main Library",
        "Main Library > Children’s Programming Room": "Hampton Main Library",
        "Willow Oaks Branch Library": "Willow Oaks Branch Library",
        "Willow Oaks Branch Library Children's Area": "Willow Oaks Branch Library",
        "Willow Oaks Branch Library > Children's Area": "Willow Oaks Branch Library",
        "Northampton Branch Library": "Northampton Branch Library",
        "Phoebus Branch Library": "Phoebus Branch Library",
        "Makerspace": "Hampton Main Library",
        "Children's Department": "Hampton Main Library",
        "Willow Oaks Village Square 227 Fox Hill Rd. Hampton VA 23669": "Willow Oaks Branch Library",
        "Outside at Main Entrance": "Hampton Main Library"
    },
    "name_suffix_map": {
        "Hampton Main Library": "Hamption Main Library",
        "Willow Oaks Branch Library": "Willow Oaks Branch Library",
        "Northampton Branch Library": "Northampton Branch Library",
        "Phoebus Branch Library": "Phoebus Branch Library"
    },
    "venue_names": {
        "Hampton Main Library": "Hamption Main Library",
        "Willow Oaks Branch Library": "Willow Oaks Branch Library",
        "Northampton Branch Library": "Northampton Branch Library",
        "Phoebus Branch Library": "Phoebus Branch Library"
    },
},
    "spl": {
        "name_suffix_map": {
            "Morgan Memorial Library": "Morgan Memorial Library",
            "North Suffolk Library": "North Suffolk Library",
            "Chuckatuck Library": "Chuckatuck Library"
        },
        "location_map": {
            "Adult Room (North Suffolk), Children's Area (North Suffolk), North Suffolk Library": "North Suffolk Library",
            "Meeting Room (Morgan Memorial), Morgan Memorial Library": "Morgan Memorial Library",
            "Morgan Memorial Library": "Morgan Memorial Library",
            "North Suffolk Library": "North Suffolk Library",
            "Chuckatuck Library": "Chuckatuck Library",
            "King's Landing Apartments: 1000 Linton Ln, Outreach": "Library2Go",
            "Online (See Description for Details)": "Online"
        },
        "venue_names": {
            "Morgan Memorial Library": "Morgan Memorial Library",
            "North Suffolk Library": "North Suffolk Library",
            "Chuckatuck Library": "Chuckatuck Library"
        },
        "program_type_to_categories": {
            "Early Childhood": "Audience - Family Event, Event Location - Suffolk, Audience - Preschool Age, Audience - Free Event, Audience - Parent & Me, Audience - Toddler/Infant",
            "Elementary": "Audience - School Age, Audience - Free Event, Event Location - Suffolk",
            "Family": "Audience - Family Event, Audience - Free Event, Event Location - Suffolk",
            "High School": "Audience - Teens, Audience - Free Event, Event Location - Suffolk",
            "Middle School": "Audience - Teens, Audience - Free Event, Event Location - Suffolk",
            "All Ages": "Audience - Family Event, Audience - Free Event, Event Location - Suffolk"
        },
        "event_name_suffix": " (Suffolk)",
        "age_to_categories": {}
    },
    "ppl": {
        "name_suffix_map": {
            "Main": "Portsmouth Main Library",
            "Main Library": "Portsmouth Main Library",
            "Churchland Branch": "Churchland Branch Library",
            "Cradock Branch": "Cradock Branch Library",
            "Manor Branch": "Manor Branch Library",
            "Coleman Meeting Room - Churchland Branch": "Churchland Branch Library",
            "Coleman Meeting Room": "Churchland Branch Library"
        },
        "venue_names": {
            "Main Library": "Portsmouth Main Library",
            "Churchland Branch": "Churchland Library",
            "Churchland Branch Library": "Churchland Library",
            "Cradock Branch": "Cradock Branch, Portsmouth Library",
            "Churchland Branch Library > Rotunda": "Churchland Library",
            "Churchland Branch Library > Children's Programming Room": "Churchland Library",
            "Children's Event Room - Main": "Portsmouth Main Library",
            "Children's Event Room": "Portsmouth Main Library",
            "Manor Branch": "Manor Branch Library"
        },
        "age_to_categories": {
            "Infant": "Audience - Toddler/Infant, Audience - Free Event, Event Location - Portsmouth",
            "Preschool": "Audience - Preschool Age, Audience - Free Event, Audience - Parent & Me, Event Location - Portsmouth",
            "School Age": "Audience - School Age, Audience - Free Event, Event Location - Portsmouth",
            "Tweens": "Audience - School Age, Audience - Free Event, Event Location - Portsmouth",
            "Teens": "Audience - Teens, Audience - Free Event, Event Location - Portsmouth",
            "All Ages": "Audience - Free Event, Event Location - Portsmouth"
        },
        "program_type_to_categories": {
            # leave blank for now unless you want to map specific phrases like "STEAM", "craft", etc.
        },
        "event_name_suffix": " (Portsmouth)"
    },

    "nnpl": {
        "name_suffix_map": {
            "Main Street Library": "Main Street Library",
            "Grissom Library": "Grissom Library",
            "Pearl Bailey Library": "Pearl Bailey Library",
            "Avenue Branch": "Avenue Branch",
            "Library Branch": "Library Branch"
        },
        "venue_names": {
            "Virgil I. Grissom Library": "Grissom Library",
            "Main Street Library": "Main Street Library",
            "Pearl Bailey Library": "Pearl Bailey Library",
            "Avenue Branch": "Avenue Branch",
            "Meeting Room": "Pearl Bailey Library"  
        },
        "program_type_to_categories": {
            "Storytime": "Audience - Family Event, List - Storytimes, Event Location - Newport News, Audience - Free Event",
            "ArtsandCrafts": "Audience - Family Event, Event Location - Newport News, Audience - Free Event",
            "SummerReading": "Audience - Family Event, Event Location - Newport News, Audience - Free Event",
            "Community": "Audience - Family Event, Event Location - Newport News, Audience - Free Event",
            "Teens": "Audience - Teens, Event Location - Newport News, Audience - Free Event",
            "Tweens": "Event Location - Newport News, Audience - Free Event",
            "Children": "Audience - Family Event, Event Location - Newport News, Audience - Free Event",
            "Adults": "Event Location - Newport News, Audience - Free Event",
            "Book": "List - Books & Authors, Event Location - Newport News, Audience - Free Event",
            "Reading": "List - Books & Authors, Event Location - Newport News, Audience - Free Event",
            "STEAM": "List - STEM/STEAM, Event Location - Newport News, Audience - Free Event",
            "Science": "List - STEM/STEAM, Event Location - Newport News, Audience - Free Event"
        },
        "age_to_categories": {
            "Babies": "Audience - Toddler/Infant, Audience - Free Event, Event Location - Newport News",
            "Toddlers": "Audience - Toddler/Infant, List - Toddler Time Events, Audience - Free Event, Event Location - Newport News",
            "Preschool": "Audience - Preschool Age, Audience - Free Event, Event Location - Newport News",
            "Children": "Audience - Family Event, Audience - Free Event, Event Location - Newport News, Audience - School Age",
            "Kids": "Audience - Family Event, Audience - Free Event, Event Location - Newport News",
            "Tweens": "Audience - Free Event, Event Location - Newport News",
            "Teens": "Audience - Teens, Audience - Free Event, Event Location - Newport News",
            "Young Adults": "Audience - Teens, Audience - Free Event, Event Location - Newport News",
            "Adults": "Audience - Free Event, Event Location - Newport News",
            "18+": "Audience - Free Event, Event Location - Newport News",
            "21+": "Audience - Free Event, Event Location - Newport News",
            "Seniors": "Audience - Seniors, Audience - Free Event, Event Location - Newport News",
            "School Age": "Audience - Family Event, Audience - Free Event, Event Location - Newport News, Audience - School Age",
            "All Ages": "Audience - Family Event, Audience - Free Event, Event Location - Newport News",
            "Infant": "Audience - Toddler/Infant, Audience - Free Event, Event Location - Newport News",
            "Family": "Audience - Family Event, Audience - Free Event, Event Location - Newport News"
        }
    }
}
