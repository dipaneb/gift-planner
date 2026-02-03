REGISTER_EXAMPLES={
    "with_name": {
        "summary": "With name",
        "value": {
            "email": "michel@yahoo.com",
            "password": "mySecurePass1234$",
            "confirmed_password": "mySecurePass1234$",
            "name": "Michel"
        }
    },
    "without_name": {
        "summary": "Without name",
        "description": "Including the 'name' key but using an empty string acts as if the 'name' key weren't included.",
        "value": {
            "email": "michel@yahoo.com",
            "password": "mySecurePass1234$",
            "confirmed_password": "mySecurePass1234$",
        }
    },
}

RESET_PASSWORD_EXAMPLE={
    "Example": {
        "summary": "Example",
        "value": {
            "password": "mySecurePass1234$",
            "confirmed_password": "mySecurePass1234$",
        }
    }
}