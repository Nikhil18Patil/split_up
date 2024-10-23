import csv
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponse
from .models import  Expense, Participant


User = get_user_model()

class SearchUserByEmailView(APIView):
    """
    SearchUserByEmailView: API to search for a user by email.

    This view allows you to search for a user by providing their email address in the URL path.
    It returns the user's ID, name, and email if the user exists in the database.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    URL Path Parameter:
    - `email` (str): The email address of the user you're looking for.

    Response:
    - 200 OK: Returns the user information if the user is found.
        Example:
        {
            "user_id": "5fe51365-fb31-4c10-ba34-bdbe5556fb68",
            "name": "Nikhil Patil",
            "email": "nikhilpatil18012004@gmail.com"
        }
    - 404 Not Found: If the email is missing or if the user with the given email does not exist.
        Example:
        {
            "error": "email not found in input"
        }
        or
        {
            "error": "User not found."
        }

    Endpoint:
    - GET /expense/get_user/nikhilpatil18012004@gmail.com/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, email=None):
        try:
            if not email:
                return Response({"error": "email not found in input"}, status=status.HTTP_404_NOT_FOUND)
            
            user = User.objects.get(email=email)
            return Response({
                "user_id": str(user.id),
                "name": user.name,
                "email": user.email
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class CreateExpenseView(APIView):
    """
    CreateExpenseView: API to create an expense and split it among participants using different methods.

    The view supports three types of split methods:
    1. Equal Split: The total amount is divided equally among all participants.
    2. Exact Split: Each participant contributes a specified amount.
    3. Percentage Split: Each participant contributes a percentage of the total amount.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    Input (Common Fields):
    - `description` (str): A brief description of the expense.
    - `amount` (float): The total expense amount.
    - `split_method` (str): The split method, which can be one of 'equal', 'exact', or 'percentage'.
    - `participants_data` (dict): A dictionary containing participant user IDs as keys and their share (amount/percentage) as values.

    Split Method Specific Fields:
    1. **Equal Split**:
       - `self` (bool): Indicates if the creator should be included in the split. Default is `true`.
       
       Example Input:
       ```json
       {
           "description": "KedarNath",
           "amount": 9000,
           "split_method": "equal",
           "participants_data": {
               "eac58f88-5b89-42b7-aa23-c4a0200663ea": 1000,
               "04ed7b18-2c74-437e-90be-87820c74932d": 2000,
               "a060c415-4870-4d7e-a580-3b34afab8c22": 4000
           },
           "self": true
       }
       ```

    2. **Exact Split**:
       - `self_amount` (float): The exact amount the creator is contributing.
       
       Example Input:
       ```json
       {
           "description": "KedarNath",
           "amount": 9000,
           "split_method": "exact",
           "participants_data": {
               "eac58f88-5b89-42b7-aa23-c4a0200663ea": 2000,
               "04ed7b18-2c74-437e-90be-87820c74932d": 2000,
               "a060c415-4870-4d7e-a580-3b34afab8c22": 4000
           },
           "self_amount": 1000
       }
       ```

    3. **Percentage Split**:
       - `self_percentage` (float): The percentage of the total amount the creator is contributing.
       
       Example Input:
       ```json
       {
           "description": "KedarNath",
           "amount": 9000,
           "split_method": "percentage",
           "participants_data": {
               "eac58f88-5b89-42b7-aa23-c4a0200663ea": 20,
               "04ed7b18-2c74-437e-90be-87820c74932d": 20,
               "a060c415-4870-4d7e-a580-3b34afab8c22": 40
           },
           "self_percentage": 10
       }
       ```

    Response:
    - 201 Created: Returns a success message if the expense is created.
      Example Output:
      ```json
      {
          "message": "Expense created successfully."
      }
      ```

    - 400 Bad Request: Returns an error message if any required fields are missing or validation fails.
      Example Output:
      ```json
      {
          "error": "The total of exact amounts does not match the expense amount."
      }
      ```

    - 404 Not Found: Returns an error message if any participant is not found.
      Example Output:
      ```json
      {
          "error": "One or more participants not found."
      }
      ```

    Validation:
    - For equal split, the amount is divided equally among all participants, including the creator if `self` is `true`.
    - For exact split, the total of the exact amounts provided for all participants (including `self_amount`) must equal the total `amount`.
    - For percentage split, the total percentages provided for all participants (including `self_percentage`) must equal 100%.

    Endpoint:
    - POST /expense/create_expense/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Extract input data
            description = request.data.get('description')
            amount = request.data.get('amount')
            split_method = request.data.get('split_method')
            participants_data = request.data.get('participants_data')  # Dictionary {user_id: value}

            # Validate required fields
            if not description or not amount or not split_method or not participants_data:
                return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                amount = float(amount)
                
                # Create the expense
                expense = Expense.objects.create(
                    description=description,
                    amount=amount,
                    split_method=split_method,
                    created_by=request.user
                )

                # Equal Split Method
                if split_method == 'equal':
                    self_exist = request.data.get('self', False)
                    total_participants = len(participants_data) + (1 if self_exist else 0)
                    equal_share = round(amount / total_participants, 2)
                    equal_percentage = round((equal_share / amount) * 100, 2)

                    # Add the creator as a participant
                    if self_exist:
                        Participant.objects.create(
                            user=request.user,
                            expense=expense,
                            amount=equal_share,
                            percentage=equal_percentage,
                            status="settled"
                        )

                    # Add other participants
                    for user_id in participants_data.keys():
                        user = User.objects.get(id=user_id)
                        Participant.objects.create(
                            user=user,
                            expense=expense,
                            amount=equal_share,
                            percentage=equal_percentage
                        )

                # Exact Split Method
                elif split_method == 'exact':
                    total_exact_amount = 0
                    self_amount = request.data.get('self_amount')
                    total_exact_amount += float(self_amount)
                    self_exact_percentage = round((float(self_amount) / amount) * 100, 2)

                    # Add the creator as a participant
                    Participant.objects.create(
                        user=request.user,
                        expense=expense,
                        amount=self_amount,
                        percentage=self_exact_percentage,
                        status="settled"
                    )

                    # Add other participants
                    for user_id, exact_amount in participants_data.items():
                        user = User.objects.get(id=user_id)
                        exact_amount = float(exact_amount)
                        total_exact_amount += exact_amount
                        exact_percentage = round((exact_amount / amount) * 100, 2)

                        Participant.objects.create(
                            user=user,
                            expense=expense,
                            amount=exact_amount,
                            percentage=exact_percentage
                        )

                    # Ensure total amounts match the expense
                    if round(total_exact_amount, 2) != round(amount, 2):
                        return Response({"error": "The total of exact amounts does not match the expense amount."}, status=status.HTTP_400_BAD_REQUEST)

                # Percentage Split Method
                elif split_method == 'percentage':
                    total_percentage = 0
                    self_percentage = float(request.data.get('self_percentage'))
                    total_percentage += self_percentage
                    self_participant_amount = round((self_percentage / 100) * amount, 2)

                    # Add the creator as a participant
                    Participant.objects.create(
                        user=request.user,
                        expense=expense,
                        amount=self_participant_amount,
                        percentage=self_percentage,
                        status="settled"
                    )

                    # Add other participants
                    for user_id, percentage in participants_data.items():
                        user = User.objects.get(id=user_id)
                        percentage = float(percentage)
                        total_percentage += percentage
                        participant_amount = round((percentage / 100) * amount, 2)

                        Participant.objects.create(
                            user=user,
                            expense=expense,
                            amount=participant_amount,
                            percentage=percentage
                        )

                   
                    if round(total_percentage, 2) != 100:
                        return Response({"error": "The total percentages must add up to 100%."}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"message": "Expense created successfully."}, status=status.HTTP_201_CREATED)

            except User.DoesNotExist:
                return Response({"error": "One or more participants not found."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_user(self, user_id):
        """Utility method to get user by user_id."""
        return User.objects.get(id=user_id)
  
        
        
class UsersAllExpensesView(APIView):
    """
    UsersAllExpensesView: API to fetch all expenses for the authenticated user. 

    This view returns two types of data:
    1. **i_owe**: Expenses where the user is a participant and owes money to others.
    2. **others_owe_me**: Expenses where the user is the creator, and other participants owe them money.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    Input:
    - No input payload required (GET request).

    Output:
    - **i_owe** (list): A list of expenses where the user owes others.
        - `description` (str): A description of the expense.
        - `amount` (float): The amount the user owes.
        - `split_method` (str): The method used to split the expense ('equal', 'exact', or 'percentage').
        - `created_by` (str): The email of the user who created the expense.
        - `status` (str): The payment status of the user's share ('pending' or 'settled').
        - `created_at` (str): The timestamp when the expense was created.

    - **others_owe_me** (list): A list of expenses where others owe the user.
        - `expense_id` (UUID): The unique ID of the expense.
        - `description` (str): A description of the expense.
        - `amount` (float): The total expense amount.
        - `split_method` (str): The method used to split the expense.
        - `created_at` (str): The timestamp when the expense was created.
        - `participants` (list): A list of participants who owe the user.
            - `user_id` (UUID): The unique ID of the participant.
            - `user_email` (str): The email of the participant.
            - `amount` (float): The amount the participant owes.
            - `status` (str): The payment status of the participant's share ('pending' or 'settled').

    Example Output:
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
                    },
                    {
                        "user_id": "a060c415-4870-4d7e-a580-3b34afab8c22",
                        "user_email": "NitSharma@gmail.com",
                        "amount": 1800.0,
                        "status": "pending"
                    }
                ]
            }
        ]
    }
    ```

    Response Status Codes:
    - **200 OK**: Successfully returns the list of expenses.
    - **500 Internal Server Error**: Returns an error message in case of an internal server issue.

    Endpoint:
    - GET /expense/users_expense/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch expenses where the user is the creator (others owe them)
            created_expenses = Expense.objects.filter(created_by=request.user)
            others_owe_me = [{
                'expense_id': exp.expense_id,
                'description': exp.description,
                'amount': exp.amount,
                'split_method': exp.split_method,
                'created_at': exp.created_at,
                'participants': [
                    {   
                        'user_id': part.user.id,
                        'user_email': part.user.email,
                        'amount': part.amount,
                        'status': part.status
                    } for part in exp.participants.exclude(user=request.user)
                ]
            } for exp in created_expenses]

            # Fetch expenses where the user is a participant (they owe others)
            participant_expenses = Participant.objects.filter(user=request.user, status='pending')
            i_owe = [{
                'description': part.expense.description,
                'amount': part.amount,
                'split_method': part.expense.split_method,
                'created_by': part.expense.created_by.email,
                'status': part.status,
                'created_at': part.expense.created_at
            } for part in participant_expenses]

            # Return the response with the i_owe and others_owe_me data
            return Response({
                'i_owe': i_owe,
                'others_owe_me': others_owe_me
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class OweView(APIView):
    """
    OweView: API to fetch total amounts the user owes to others and others owe to the user.
    
    This view returns two types of data:
    1. **people_i_owe**: A list of people to whom the user owes money.
    2. **people_owe_me**: A list of people who owe money to the user.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    Input:
    - No input payload required (GET request).

    Output:
    - **people_i_owe** (list): A list of people the user owes.
        - `name` (str): The name of the person to whom the user owes money.
        - `total_owe` (float): The total amount the user owes this person.
        
    - **people_owe_me** (list): A list of people who owe the user.
        - `name` (str): The name of the person who owes the user money.
        - `total_owed_to_me` (float): The total amount this person owes the user.

    Example Output:
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
            },
            {
                "name": "Patil Nikhil",
                "total_owed_to_me": 10650.0
            },
            {
                "name": "info Nikhil",
                "total_owed_to_me": 6450.0
            }
        ]
    }
    ```

    Response Status Codes:
    - **200 OK**: Successfully returns the list of people the user owes and those who owe the user.
    - **500 Internal Server Error**: Returns an error message in case of an internal server issue.

   Endpoint:
    - GET /expense/owe_list/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            # Get list of all people the user owes money to
            people_i_owe = Participant.objects.filter(
                user=user, status="pending"
            ).values('expense__created_by__name').annotate(total_owe=Sum('amount'))

            # Get list of all people who owe money to the user
            people_owe_me = Participant.objects.filter(
                expense__created_by=user, status="pending"
            ).values('user__name').annotate(total_owed_to_me=Sum('amount'))

            # Format the results to include names
            data = {
                "people_i_owe": [
                    {
                        "name": person['expense__created_by__name'],
                        "total_owe": person['total_owe']
                    }
                    for person in people_i_owe
                ],
                "people_owe_me": [
                    {
                        "name": person['user__name'],
                        "total_owed_to_me": person['total_owed_to_me']
                    }
                    for person in people_owe_me
                ],
            }

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SettleExpenseView(APIView):
    """
    SettleExpenseView: API to settle payments for an expense. The user who created the expense can mark participants as "settled".

    Task:
    - Allows settling payments for participants of an expense.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    Input:
    - **user_ids** (optional): List of user IDs to mark as settled for the expense.
    ```json
    {
        "user_ids": ["eac58f88-5b89-42b7-aa23-c4a0200663ea", "04ed7b18-2c74-437e-90be-87820c74932d"]
    }
    ```
    - If `user_ids` is not provided, all pending participants will be settled.

    URL Path:
    - The API expects the `expense_id` to be passed in the URL path, representing the specific expense to settle participants for.

    Example Request:
    - POST /expenses/settle_expense/{expense_id}/
    
    Output:
    - If `user_ids` are provided:
    ```json
    {
        "message": "Expense settled for users: John Doe, Jane Doe.",
        "not_settled": "Some users could not be settled: ['user_id1', 'user_id2']"
    }
    ```
    - If `user_ids` is not provided, the response will settle all pending participants:
    ```json
    {
        "message": "All participants have been settled."
    }
    ```

    Response Status Codes:
    - **200 OK**: Successfully settled participants.
    - **400 Bad Request**: Invalid input (e.g., `user_ids` is not a list or no pending participants).
    - **404 Not Found**: Expense not found or the user is not the creator of the expense.
    - **500 Internal Server Error**: Internal server error with an error message.

    Example Output:
    - When no users are settled:
    ```json
    {
        "message": "No participants were settled.",
        "not_settled": "Some users could not be settled: ['eac58f88-5b89-42b7-aa23-c4a0200663ea', '04ed7b18-2c74-437e-90be-87820c74932d']"
    }
    ```

    Example Usage:
    - POST /expenses/settle_expense/{expense_id}/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, expense_id):
        try:
            user_ids = request.data.get("user_ids", None)  # List of user_ids to settle

            try:
                # Fetch the expense by ID and ensure it's created by the current user
                expense = Expense.objects.get(expense_id=expense_id, created_by=request.user)

                if user_ids:
                    # Validate that user_ids is a list
                    if not isinstance(user_ids, list):
                        return Response({"error": "user_ids must be a list."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    settled_users = []
                    not_found_users = []

                    # Settle specific participants
                    for user_id in user_ids:
                        try:
                            participant = Participant.objects.get(expense=expense, user__id=user_id, status="pending")
                            participant.status = "settled"
                            participant.save()
                            settled_users.append(participant.user.name)  # Store settled user names
                        except Participant.DoesNotExist:
                            not_found_users.append(user_id)  # Store user IDs that were not found or already settled

                    if settled_users:
                        message = f"Expense settled for users: {', '.join(settled_users)}."
                    else:
                        message = "No participants were settled."

                    # Include users that were not found or already settled
                    if not_found_users:
                        return Response({
                            "message": message,
                            "not_settled": f"Some users could not be settled: {not_found_users}"
                        }, status=status.HTTP_200_OK)

                    return Response({"message": message}, status=status.HTTP_200_OK)

                else:
                    # Settle all participants if no user_ids are provided
                    participants = Participant.objects.filter(expense=expense, status="pending")
                    
                    if not participants.exists():
                        return Response({"message": "No pending payments to settle for this expense."}, status=status.HTTP_400_BAD_REQUEST)

                    participants.update(status="settled")
                    
                    return Response({"message": "All participants have been settled."}, status=status.HTTP_200_OK)

            except Expense.DoesNotExist:
                return Response({"error": "Expense not found or you are not the creator."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BalanceSheetView(APIView):
    """
    BalanceSheetView: API to retrieve the balance sheet of expenses for the authenticated user.

    Task:
    - Retrieves all expenses the user has participated in, including their share and the total expense amount.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    Output:
    - Returns a JSON response with the user's individual expenses.
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
            },
            ...
        ]
    }
    ```

    Response Status Codes:
    - **200 OK**: Successfully retrieved individual expenses.

    Example Usage:
    - GET /expense/balance_sheet/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        participated_expenses = Participant.objects.filter(user=request.user)
        
        individual_expenses_data = []

        # Process participated expenses (user as participant)
        for participation in participated_expenses:
            expense = participation.expense
            total_amount = expense.amount
            
            individual_expenses_data.append({
                'expense_id': expense.expense_id,
                'description': expense.description,
                'user_share': participation.amount,  
                'total_amount': total_amount,  # Total expense amount
                'split_method': expense.split_method,
                'created_by': expense.created_by.name,
                'created_at': expense.created_at,
                'status': participation.status,  # User's status (pending/settled)
            })

        return JsonResponse({
            'individual_expenses': individual_expenses_data,
        })


class BalanceSheetDownloadView(APIView):
    """
    BalanceSheetDownloadView: API to download the balance sheet of expenses for the authenticated user in CSV format.

    Task:
    - Allows users to download a CSV file containing their expenses along with their shares and statuses.

    Authentication:
    - Requires Bearer JWT Token (Authorization header).

    Output:
    - Returns a CSV file containing the following headers:
    - `Expense ID`, `Description`, `Amount`, `Split Method`, `Created By`, `Created At`, `Your Share`, `Status`.

    Example Response:
    - The response will prompt a download of a CSV file named "balance_sheet.csv".

    Example Usage:
    - GET /expense/balance_sheet/download/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Create the HttpResponse object with the appropriate CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

        # Create a CSV writer object and write the header row
        writer = csv.writer(response)
        writer.writerow(['Expense ID', 'Description', 'Amount', 'Split Method', 'Created By', 'Created At', 'Your Share', 'Status'])

        # Fetch the expenses where the user is either the creator or a participant
        overall_expenses = Expense.objects.filter(Q(created_by=request.user) | Q(participants__user=request.user)).distinct()

        # Loop through each expense and write its data along with user-specific share and status
        for exp in overall_expenses:
            # Get the participants of the expense
            participants = exp.participants.all()

            # Get data for the current user
            participant_data = participants.filter(user=request.user).first()

            if participant_data:
                user_share = participant_data.amount  # Fetch the user's share amount
                status = participant_data.status      # Fetch the status of the expense for the user
            else:
                user_share = 'N/A'
                status = 'N/A'

            # Write a row for this expense
            writer.writerow([
                exp.expense_id,
                exp.description,
                exp.amount,
                exp.split_method,
                exp.created_by.name,  # Assuming `created_by` is a User model with a `name` attribute
                exp.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format the date for CSV
                user_share,
                status
            ])

        # Return the CSV response for download
        return response
