intall requirements --- pip install -r requirements.txt
run project python manage.py runserver


# Expense Management API Documentation

## User Signup API

### Input
```json
{
    "email": "PatilNikhil@gmail.com",
    "name": "Patil Nikhil",
    "mobile_number": "0987654321",
    "password": "Nikhil@18"
}
```
### Output
```json
{
    "user_id": "5ac30e5c-d811-4ac1-a0af-88533ff5972d",
    "name": "Patil Nikhil",
    "email": "PatilNikhil@gmail.com",
    "message": "User created successfully"
}
```

## User Login API

### Input
```json
{
    "email": "Nikhilpatil18012004@gmail.com",
    "password":"Nikhil@18"
}
```
### Output
```json
{
    "user_id": "49b0b4d2-8753-4af8-b510-afcd885101d9",
    "name": "Nikhil Patil",
    "email": "nikhilpatil18012004@gmail.com",
    "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMDIxMDU1NCwiaWF0IjoxNzI5NjA1NzU0LCJqdGkiOiJkOTQ2NGUyMWE1NDg0MDY4YWIwYTg2MDU2ODMyMjQxNiIsInVzZXJfaWQiOiI0OWIwYjRkMi04NzUzLTRhZjgtYjUxMC1hZmNkODg1MTAxZDkifQ.eFLYeAuWg0NU7UKaXOgU5o8ixTKBBS1_pLIKhNiSWtU",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NjA5MzU0LCJpYXQiOjE3Mjk2MDU3NTQsImp0aSI6ImJiODE0ZWI1NDA5ZjQ1YThhODgzNTYxNGU0YTVlNDMzIiwidXNlcl9pZCI6IjQ5YjBiNGQyLTg3NTMtNGFmOC1iNTEwLWFmY2Q4ODUxMDFkOSJ9.DAl4VpAC5HCmXBNOF6wXvLCkPgquxsTGzb1O3VlEqbA"
    }
}
```

## Search User by Email API

### URL Path Parameter
- `email`: The email address of the user you want to search.

### Output
- **Success Response** (200 OK):
    ```json
    {
        "user_id": "5fe51365-fb31-4c10-ba34-bdbe5556fb68",
        "name": "Nikhil Patil",
        "email": "nikhilpatil18012004@gmail.com"
    }
    ```
- **Error Response** (404 Not Found):
    ```json
    {
        "error": "User not found."
    }
    ```

## Create Expense API

### Input
- Common Fields:
    - `description`: Description of the expense.
    - `amount`: The total amount of the expense.
    - `split_method`: Split method ('equal', 'exact', or 'percentage').
    - `participants_data`: Dictionary containing participant user IDs and their respective shares.
    - Additional fields based on split method:

        - **Equal Split**:
          - `self`: Whether the creator should be included in the split. Default is `true`.
          ```json
          {
              "description": "Trip Expense",
              "amount": 9000,
              "split_method": "equal",
              "participants_data": {
                  "user1": 1000,
                  "user2": 2000
              },
              "self": true
          }
          ```

        - **Exact Split**:
          ```json
          {
              "description": "Trip Expense",
              "amount": 9000,
              "split_method": "exact",
              "participants_data": {
                  "user1": 3000,
                  "user2": 2000
              },
              "self_amount": 1000
          }
          ```

        - **Percentage Split**:
          ```json
          {
              "description": "Trip Expense",
              "amount": 9000,
              "split_method": "percentage",
              "participants_data": {
                  "user1": 30,
                  "user2": 20
              },
              "self_percentage": 10
          }
          ```

### Output
```json
{
    "message": "Expense created successfully."
}
```

## User's All Expenses API

### Output
- **Success Response** (200 OK):
    ```json
    {
        "i_owe": [
            {
                "description": "Dinner at Restaurant",
                "amount": 1200.0,
                "split_method": "equal",
                "created_by": "john.doe@example.com",
                "status": "pending",
                "created_at": "2024-10-21T14:34:22Z"
            }
        ],
        "others_owe_me": [
            {
                "expense_id": "eb663885-6a16-48cb-84ba-d2ecd9c6269d",
                "description": "Birthday Party Expenses",
                "amount": 6000.0,
                "split_method": "percentage",
                "created_at": "2024-10-22T15:01:05.483699Z",
                "participants": [
                    {
                        "user_id": "eac58f88-5b89-42b7-aa23-c4a0200663ea",
                        "user_email": "infonikhil@gmail.com",
                        "amount": 2400.0,
                        "status": "settled"
                    }
                ]
            }
        ]
    }
    ```

## Owe List API

### Output
```json
{
    "people_i_owe": [
        {
            "name": "John Doe",
            "total_owe": 4500.0
        }
    ],
    "people_owe_me": [
        {
            "name": "Nit Sharma",
            "total_owed_to_me": 11250.0
        }
    ]
}
```

## Settle Expense API

### Input
- `user_ids`: (Optional) List of user IDs to mark as settled.
  If not provided, all pending participants will be settled.
  Example Input:
  ```json
  {
      "user_ids": ["eac58f88-5b89-42b7-aa23-c4a0200663ea", "04ed7b18-2c74-437e-90be-87820c74932d"]
  }
  ```

### Output
- If user IDs are provided:
    ```json
    {
        "message": "Expense settled for users: John Doe, Jane Doe."
    }
    ```
- If user IDs are not provided:
    ```json
    {
        "message": "All participants have been settled."
    }
    ```

## Balance Sheet API

### Output
```json
{
    "individual_expenses": [
        {
            "expense_id": "eb663885-6a16-48cb-84ba-d2ecd9c6269d",
            "description": "Birthday Party Expenses",
            "user_share": 2400.0,
            "total_amount": 6000.0,
            "split_method": "percentage",
            "created_by": "John Doe",
            "created_at": "2024-10-22T15:01:05.483699Z",
            "status": "settled"
        }
    ]
}
```

## Balance Sheet Download API

### Description
- This API allows the user to download a CSV file containing their balance sheet.
- The CSV contains headers like `Expense ID`, `Description`, `Amount`, `Split Method`, `Created By`, `Created At`, `Your Share`, `Status`.

### Example Output
The response will prompt a download of a CSV file named "balance_sheet.csv".
