from django.contrib.auth import get_user_model
from users.models import User
print("Deleting users")
try:
    get_user_model().objects.get(mobile_no='1111155559')
except User.DoesNotExist:
    pass
else:
    get_user_model().objects.get(mobile_no='1111155559').delete()
try:
    get_user_model().objects.get(mobile_no='2222234522')
except User.DoesNotExist:
    pass
else:
    get_user_model().objects.get(mobile_no='2222234522').delete()
try:
    get_user_model().objects.get(mobile_no='3333311111')
except User.DoesNotExist:
    pass
else:
    get_user_model().objects.get(mobile_no='3333311111').delete()
print("Finished deleting users")