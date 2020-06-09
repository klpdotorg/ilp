from django.db import models
from .institution import Institution


class StudentGroup(models.Model):
    """ StudentGroup information per school"""
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)
    section = models.CharField(max_length=10, blank=True, null=True)
    group_type = models.ForeignKey('common.GroupType', default='class', on_delete=models.DO_NOTHING)
    students = models.ManyToManyField(
        'Student',
        related_name='studentgroups',
        through='StudentStudentGroupRelation'
    )
    staff = models.ManyToManyField("Staff", through="StaffStudentGroupRelation")
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
    gender = models.ForeignKey('common.Gender', default='male', on_delete=models.DO_NOTHING)
    mt = models.ForeignKey('common.Language', default='kan', on_delete=models.DO_NOTHING)
    religion = models.ForeignKey('common.Religion', null=True, on_delete=models.DO_NOTHING)
    category = models.ForeignKey('common.StudentCategory', null=True, on_delete=models.DO_NOTHING)
    enrollment_id = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return "%s" % self.first_name


class StudentStudentGroupRelation(models.Model):
    """Student and StudentGroup mapping per year"""
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.DO_NOTHING)
    academic_year = models.ForeignKey('common.AcademicYear', on_delete=models.DO_NOTHING)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('student', 'student_group', 'academic_year'), )

    def __unicode__(self):
        return "%s: %s in %s" % (self.student, self.student_group,
                                 self.academic_year,)


class StaffType(models.Model):
    """ Type of staff"""
    staff_type = models.CharField(max_length=100)
    institution_type = models.ForeignKey('common.InstitutionType', on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return "%s" % self.staff_type


class Staff(models.Model):
    """ Staff information"""
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True)
    doj = models.DateField(max_length=20, null=True)
    gender = models.ForeignKey('common.Gender', default='f', on_delete=models.DO_NOTHING)
    mt = models.ForeignKey('common.Language', default='kan', on_delete=models.DO_NOTHING)
    staff_type = models.ForeignKey(StaffType, on_delete=models.DO_NOTHING)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)

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
    staff = models.ForeignKey(Staff, on_delete=models.DO_NOTHING)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.DO_NOTHING)
    academic_year = models.ForeignKey('common.AcademicYear', on_delete=models.DO_NOTHING)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('staff', 'student_group', 'academic_year'), )

    def __unicode__(self):
        return "%s: %s in %s" % (self.staff, self.student_group,
                                 self.academic_year,)


class StaffQualification(models.Model):
    """Staff to Qualification mapping"""
    staff = models.ForeignKey(Staff, on_delete=models.DO_NOTHING)
    qualification = models.ForeignKey(Qualification, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return "%s: %s" % (self.staff, self.qualification)


class StaffTraining(models.Model):
    """Staff to Training mapping"""
    staff = models.ForeignKey(Staff, on_delete=models.DO_NOTHING)
    training = models.ForeignKey(Training, on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return "%s: %s" % (self.staff, self.training)
