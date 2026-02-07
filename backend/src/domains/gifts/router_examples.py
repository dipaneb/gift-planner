CREATE_GIFT_EXAMPLE = {
    "minimal": {
        "summary": "Minimal gift (name only)",
        "value": {
            "name": "Chess set",
        }
    },
    "with_details": {
        "summary": "Gift with all details",
        "value": {
            "name": "Canon EOS R50",
            "url": "https://www.amazon.fr/dp/B0BVNQ3Q3W",
            "price": 799.99,
            "status": "idee",
            "quantity": 1,
            "recipient_ids": [],
        }
    },
    "with_recipients": {
        "summary": "Gift assigned to recipients",
        "value": {
            "name": "Board game collection",
            "price": 45.00,
            "recipient_ids": [
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            ],
        }
    }
}

UPDATE_GIFT_EXAMPLE = {
    "update_name": {
        "summary": "Update name only",
        "value": {
            "name": "Canon EOS R50 (Black)",
        }
    },
    "update_status": {
        "summary": "Update status only",
        "value": {
            "status": "achete",
        }
    },
    "update_multiple": {
        "summary": "Update multiple fields",
        "value": {
            "name": "Canon EOS R50 (Black)",
            "price": 749.99,
            "status": "commande",
            "quantity": 1,
        }
    },
    "update_recipients": {
        "summary": "Replace associated recipients",
        "value": {
            "recipient_ids": [
                "00000000-0000-0000-0000-000000000001",
            ],
        }
    }
}
