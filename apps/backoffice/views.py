import uuid
import os
import threading

from django.shortcuts import render
from django.views import View
from django.conf import settings

from boundary.models import BoundaryStateCode

from backoffice.forms import ExportForm
from backoffice.utils import (
    get_assessment_field_names, create_csv_and_move
)
from users.views import UserLoginView
from users.serializers import UserLoginSerializer, UserSerializer
from users.utils import (
    login_user,
    check_source_and_add_user_to_group,
    activate_user_and_login
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin


def is_staff(user):
    print("inside check")
    return user.is_staff


class BackOfficeLoginView(UserLoginView):
    template_name = 'backoffice/login.html'

    def get(self, request, *args, **kwargs):
        print("login view invoked")
        next = request.GET.get('next', '')
        return render(request, self.template_name, {"next": next})
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = UserSerializer(serializer.user).data
        user = authenticate(request, username=request.data["username"], password=request.data["password"])
        if user is not None:
            login(self.request, user)
            # See if the user belongs to PreUserGroup and add him
            # check_source_and_add_user_to_group(request, serializer.user)
            if user.is_staff:
                print("user is a staff")
                print(request.GET.get('next', '/backoffice/'))
                return HttpResponseRedirect(request.GET.get('next', '/backoffice/'))
            else:
                return Response("User forbidden access to this area", status=status.HTTP_403_FORBIDDEN)
        else:
                return Response("Invalid Login", status=status.HTTP_401_UNAUTHORIZED)



class BackOfficeLogoutView(LoginRequiredMixin, View):
    def get(self,request):
        logout(request)
        print("user logged out")
        return HttpResponse("Logged out", status=status.HTTP_200_OK)


class BackOfficeView(LoginRequiredMixin, View):
    template_name = 'backoffice/export.html'
    login_url = '/backoffice/login/'
    
    def get(self, request):
        if request.user.is_authenticated:
            print("User is authenticated")
        if request.user.is_staff:
            print("user is a staff user")
        states = BoundaryStateCode.objects.all()
        year = list(range(2016, 2020))
        month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        return render(request, self.template_name,
                      {'states': states, 'year': year, 'month': month})

    def post(self, request):
        form = ExportForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            field_names = get_assessment_field_names(
                data['survey']
            )
            file_id = str(uuid.uuid1())

            file_path = settings.MEDIA_ROOT + '/backoffice-data/'
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            try:
                # threading.Thread(target=create_csv_and_move, args=(
                #     data['survey'], data['district'], data['block'],
                #     data['cluster'], data['school'], data['from_year'],
                #     data['from_month'], data['to_year'], data['to_month'],
                #     file_id + '.csv', field_names
                # )).start()
                threading.Thread(target=create_csv_and_move, args=(
                    data['survey'], data['district'], data['block'],
                    data['cluster'], data['school'], data['from_date'],
                    data['to_date'],
                    file_id + '.csv', field_names
                )).start()
            except Exception as e:
                return render(
                    request, self.template_name,
                    {'file_error': (
                        "There is an error in generating the file:", e)}
                )
            file_url = (
                settings.MEDIA_URL + 'backoffice-data/' + file_id + '.csv'
            )
            return render(request, self.template_name, {'file_url': file_url})
        return render(
            request, self.template_name, {'form_errors': form.errors}
        )


class GPContestValidatorView(View):
    """
    View that validates GP contest raw data excel file
    """
    template_name = 'backoffice/gpcontest_validator.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        return render(
            request,
            self.template_name,
            {
                'errors': ['Unknown error occured. Please contact KLP team at dev@klp.org.in'],
                'success': ['All rows passed']
            }
        )
