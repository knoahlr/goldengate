from django.urls import path
from goldengate.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    applicant_user,
    account_holding_user,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("profile/<int:id>/", view=user_detail_view, name="detail"),
    path("signup", view=applicant_user, name="applicant_signup"),
    path("login", view=account_holding_user, name="account_holder_login"),

]
