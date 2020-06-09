import datetime
from django.db import models


class StatusManager(models.Manager):
    def all_active(self):
        return self.filter(status=Status.ACTIVE)

    def all_inactive(self):
        return self.filter(status=Status.INACTIVE)

    def all_deleted(self):
        return self.filter(status=Status.DELETED)


class AcademicYear(models.Model):
    """ Academic years in Schools """
    char_id = models.CharField(max_length=300, primary_key=True)
    year = models.CharField(max_length=10)
    active = models.ForeignKey('Status', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('year'), )


class Status(models.Model):
    """ Status of the data"""
    ACTIVE = 'AC'
    INACTIVE = 'IA'
    DELETED = 'DL'
    PROMOTION_SUCCESS = 'PS'
    PROMOTION_FAILED = 'PF'
    PASSED_OUT = 'PO'
    DETAINED = 'D'

    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class Language(models.Model):
    """ Languages used in School """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


def current_academic():
    ''' To select current academic year'''
    try:
        academicObj = AcademicYear.objects.get(active='AC')
        return academicObj
    except AcademicYear.DoesNotExist:
        return 1


def default_end_date():
    ''' To select academic year end date'''

    now = datetime.date.today()
    currentYear = int(now.strftime('%Y'))
    currentMont = int(now.strftime('%m'))
    academicYear = current_academic().name
    academicYear = academicYear.split('-')
    if currentMont > 5 and int(academicYear[0]) == currentYear:
        academic_end_date = datetime.date(currentYear+1, 5, 30)
    else:
        academic_end_date = datetime.date(currentYear, 5, 30)
    return academic_end_date


class InstitutionGender(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class InstitutionType(models.Model):
    '''
    Aligned to constants defined in the DB models. When those change,
    these will also have to
    change
    '''
    PRIMARY_SCHOOL = 'primary'
    PRE_SCHOOL = 'pre'

    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class Gender(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class GroupType(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class Religion(models.Model):
    """Religion"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.name


class StudentCategory(models.Model):
    """ Category of students"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.name


class RespondentType(models.Model):
    char_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    state_code = models.ForeignKey('boundary.BoundaryStateCode', null=True, on_delete=models.DO_NOTHING)
    active = models.ForeignKey('Status', default='AC', on_delete=models.DO_NOTHING)
