from users.models import User
superuser1 = User.objects.create(mobile_no='3333322222',email='superuser1@klp.org.in', password='changeme', is_active='t', is_superuser='t')
superuser1 = User.objects.create(mobile_no='4444422222',email='superuser2@klp.org.in', password='changeme', is_active='t', is_superuser='t')
