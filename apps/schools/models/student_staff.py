from django.db import models
from .institution import Institution

class StudentGroup(models.Model):
    """ StudentGroup information per school"""
    institution = models.ForeignKey(Institution)
    name = models.CharField(max_length=50)
    status = models.ForeignKey('common.Status')
    section = models.CharField(max_length=10, blank=True, null=True)
    group_type = models.ForeignKey('common.GroupType', default='class')
    students = models.ManyToManyField(
        'Student',
        related_name='studentgroups',
        through='StudentStudentGroupRelation'
    )
    class Meta:
        unique_together = (('institution', 'name', 'section'), )
        ordering = ['name', 'section']

    def __unicode__(self):
        return '%s' % self.name

class Student(models.Model):
    """ Student information """
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(max_length=20, null=True)
    gender = models.ForeignKey('common.Gender', default='m')
    mt = models.ForeignKey('common.Language', default='kan')
    religion = models.ForeignKey('common.Religion', null=True)
    category = models.ForeignKey('common.StudentCategory', null=True)
    enrollment_id = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    institution = models.ForeignKey(Institution)
    status = models.ForeignKey('common.Status')

    def __unicode__(self):
        return "%s" % self.first_name


class StudentStudentGroupRelation(models.Model):
    """Student and StudentGroup mapping per year"""
    student = models.ForeignKey(Student)
    student_group = models.ForeignKey(StudentGroup)
    academic_year = models.ForeignKey('common.AcademicYear')
    status = models.ForeignKey('common.Status')

    class Meta:
        unique_together = (('student', 'student_group', 'academic_year'), )

    def __unicode__(self):
        return "%s: %s in %s" % (self.student, self.student_group,
                                 self.academic_year,)


class StaffType(models.Model):
    """ Type of staff"""
    staff_type = models.CharField(max_length=100)
    institution_type = models.ForeignKey('common.InstitutionType')

    def __unicode__(self):
        return "%s" % self.staff_type


class Staff(models.Model):
    """ Staff information"""
    institution = models.ForeignKey(Institution)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)
    doj = models.DateField(max_length=20, null=True)
    gender = models.ForeignKey('common.Gender', default='f')
    mt = models.ForeignKey('common.Language', default='kan')
    staff_type = models.ForeignKey(StaffType)
    status = models.ForeignKey('common.Status')

    def __unicode__(self):
        return "%s" % self.first_name


class Qualification(models.Model):
    """Qualifications of Staff"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.name


class Training(models.Model):
    """Training imparted to Staff"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.name


class StaffStudentGroupRelation(models.Model):
    """Staff to StudentGroup mapping per year"""
    staff = models.ForeignKey(Staff)
    student_group = models.ForeignKey(StudentGroup)
    academic_year = models.ForeignKey('common.AcademicYear')
    status = models.ForeignKey('common.Status')

    class Meta:
        unique_together = (('staff', 'student_group', 'academic_year'), )

    def __unicode__(self):
        return "%s: %s in %s" % (self.staff, self.student_group,
                                 self.academic_year,)


class StaffQualification(models.Model):
    """Staff to Qualification mapping"""
    staff = models.ForeignKey(Staff)
    qualification = models.ForeignKey(Qualification)

    def __unicode__(self):
        return "%s: %s" % (self.staff, self.qualification)


class StaffTraining(models.Model):
    """Staff to Training mapping"""
    staff = models.ForeignKey(Staff)
    training = models.ForeignKey(Training)

    def __unicode__(self):
        return "%s: %s" % (self.staff, self.training)
