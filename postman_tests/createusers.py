from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group  
admin_user = get_user_model().objects.create_superuser(
            '1111155559', 'admin')
regular_user = get_user_model().objects.create('2222234522', 'regular')
a3_user = get_user_model().objects.create('3333311111', 'a3')
a3 = Group.objects.get(name='a3_users')
ilpauth = Group.objects.get(name='ilp_auth_user')
ilpkonnect = Group.objects.get(name='ilp_konnect_user')
a3.user_set.add(a3_user) 
a3.save()
ilpkonnect.user_set.add(regular_user)
ilpkonnect.save()
ilpauth.user_set.add(regular_user) 
ilpauth.save()
a3_user.save()
regular_user.save()