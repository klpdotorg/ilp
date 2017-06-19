from django.db import models

# Choices

INSTITUTION_GENDER = (
    ('boys', 'Boys'),
    ('girls', 'Girls'),
    ('co-ed', 'Co-Ed'),
)

INSTITUTION_TYPE = (
    ('pre', 'Pre'),
    ('primary', 'Primary'),
)

GENDER = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)

GROUP_TYPE = (
    ('Class', 'Class'),
    ('Center', 'Center')
)
