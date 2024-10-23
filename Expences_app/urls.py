from django.urls import path
from .views import SearchUserByEmailView, CreateExpenseView , UsersAllExpensesView, OweView, SettleExpenseView, BalanceSheetView, BalanceSheetDownloadView



urlpatterns = [
    path('get_user/<str:email>/', SearchUserByEmailView.as_view(), name='get_user_name'),
    path('create_expense/', CreateExpenseView.as_view(), name="create_expence"),
    path('users_expense/', UsersAllExpensesView.as_view(), name="users_expence_view"),
    path('owe_list/', OweView.as_view(), name="users_owe_list"),
    path('settle_expense/<str:expense_id>/', SettleExpenseView.as_view(), name="settle_expense"),
    
    path('balance_sheet/', BalanceSheetView.as_view(), name='balance_sheet'),
    path('balance-sheet/download/', BalanceSheetDownloadView.as_view(), name='balance-sheet-download')
    
]   
