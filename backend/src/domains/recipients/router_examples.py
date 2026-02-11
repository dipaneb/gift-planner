CREATE_RECIPIENT_EXAMPLE = {
    "with_notes": {
        "summary": "With notes",
        "value": {
            "name": "Michel (Brother)",
            "notes": "Likes books, plays chess and started photography.",
        }
    },
    "without_notes": {
        "summary": "Without notes",
        "value": {
            "name": "Alice (Friend)",
        }
    },
    "with_gifts": {
        "summary": "With associated gifts",
        "value": {
            "name": "Bob (Colleague)",
            "notes": "Enjoys board games.",
            "gift_ids": [
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            ],
        }
    }
}

UPDATE_RECIPIENT_EXAMPLE = {
    "update_name": {
        "summary": "Update name only",
        "value": {
            "name": "Michel (Older Brother)",
        }
    },
    "update_notes": {
        "summary": "Update notes only",
        "value": {
            "notes": "Updated: Loves books, chess, photography and cooking.",
        }
    },
    "update_both": {
        "summary": "Update both fields",
        "value": {
            "name": "Michel",
            "notes": "Brother - interests: books, chess, photography, cooking.",
        }
    },
    "update_gifts": {
        "summary": "Replace associated gifts",
        "value": {
            "gift_ids": [
                "00000000-0000-0000-0000-000000000001",
            ],
        }
    }
}