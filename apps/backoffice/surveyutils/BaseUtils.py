import abc


class BaseUtils(metaclass=abc.ABCMeta):
    
    def getAllQuestionGroupData(self, surveyid):
        questiondata = {}
        try:
            question_qs = QuestionGroup_Questions.objects.filter(questiongroup__survey_id=surveyid).values('questiongroup_id', 'questiongroup__name', 'question__id', 'question__question_text','question__display_text', 'sequence')
        except QuestionGroup_Questions.DoesNotExist:
            print("Did not find relevant question data for surveyid: "+str(surveyid))
            return None

        for qs in question_qs:
            if qs['questiongroup_id'] in questiondata:
                questiondata[qs['questiongroup_id']]['questions'][qs['sequence']] = {'question_text':qs['question_question_text'], 'qid': qs['question_id'], 'display_text': qs['question__display_text']}
            else:
                questiondata[qs['questiongroup_id']] = {'name':qs['questiongroup__name'], 'questions':[]}
                questiondata[qs['questiongroup_id']]['questions'][qs['sequence']] = {'question_text':qs['question_question_text'], 'qid': qs['question_id'], 'display_text': qs['question__display_text']}
        return questiondata

    def getQuestionData(self, surveyid, questiongroup_id):
        numquestions = 0
        questiondata = {}
        try:
            question_qs = QuestionGroup_Questions.objects.filter(questiongroup=questiongroup_id).values('questiongroup_id', 'questiongroup__name', 'question__id', 'question__microconcept__char_id','question__question_text', 'question__display_text','questiongroup__source__name', 'sequence').order_by('sequence')
        except QuestionGroup_Questions.DoesNotExist:
            print("Did not find relevant question data for surveyid: "+str(surveyid))
            return None

        for qs in question_qs:
            if numquestions < qs['sequence']:
                numquestions = numquestions+1
            if qs['questiongroup_id'] in questiondata:
                questiondata[qs['questiongroup_id']]['questions'].append({'question_text':qs['question__question_text'], 'qid': qs['question__id'], 'display_text': qs['question__microconcept__char_id'], 'sequence': qs['sequence']})
            else:
                questiondata[qs['questiongroup_id']] = {'name':qs['questiongroup__name'],'source':qs['questiongroup__source__name'], 'questions':[]}
                questiondata[qs['questiongroup_id']]['questions'].append({'question_text':qs['question__question_text'], 'qid': qs['question__id'], 'display_text': qs['question__microconcept__char_id'], 'sequence': qs['sequence']})
        return questiondata, numquestions
       
    @abc.abstractmethod
    def getQuestionGroups(self, surveyid, from_yearmonth, to_yearmonth):
        pass
    
    @abc.abstractmethod
    def getAssessmentData(self, surveyinfo, districts, questiongroup, from_yearmonth, to_yearmonth):
        pass
      
    def validateSurvey(self, surveyid):
        if surveyid == None:
            print("Mandatory parameter surveyid not passed")
            return None
        try:
            survey = Survey.objects.get(id=surveyid)
        except Survey.DoesNotExist:
            print("Invalid Survey id passed: "+str(surveyid)+", please enter a valid one")
            return None
        return survey

    def create_file_name(self, filename, from_yearmonth, to_yearmonth, qgroup_id, qgroup_name):
        ''' Construct a filename with a questiongroup ID, from, to dates and timestamp '''
        now = date.today()
        filename = filename + "_" + str(qgroup_id) + "_" + qgroup_name \
            + "_" + str(from_yearmonth) + "_" + str(to_yearmonth) + "_" + str(now)
        return filename 
    
    
    @abc.abstractmethod
    def createXLS(self, surveyinfo, questioninfo, numquestions, questiongroup_id, assessmentdata, filename, skipxls, dest_folder):
        pass
    
    def deleteTempFiles(self, tempFiles):
            for f in tempFiles:
            os.remove(f)

    def getAcademicYear(self, inputdate):
        year = inputdate[:4]
        month = inputdate[5:7]
        if int(month) >=6:
            academicyear = year+"-"+str(int(year)+1)
        else:
            academicyear = str(int(year)-1)+"-"+year
        return academicyear

    def convertToDate(self, from_yearmonth_string, to_yearmonth_string):
        from_date = None
        to_date = None
        if from_yearmonth_string is not None:
            year = int(from_yearmonth_string[0:4])
            month = int(from_yearmonth_string[4:])
            from_date = date(year=year, month=month, day=1)
        if to_yearmonth_string is not None:
            to_year = int(to_yearmonth_string[0:4])
            to_month = int(to_yearmonth_string[4:])
            to_date = date(year=to_year, month=to_month, day=calendar.monthrange(to_year, to_month)[1])
        return from_date, to_date

    def dumpData(self, surveyinfo, from_yearmonth, to_yearmonth, filename, skipxls):
        questiongroups_list = self.getQuestionGroups(surveyinfo.id, from_yearmonth, to_yearmonth)
        dest_folder = self.createOutputFolder(surveyinfo, from_yearmonth, to_yearmonth)
        if from_yearmonth and to_yearmonth is not None:
            districts = SurveyBoundaryAgg.objects.filter(
                survey_id=surveyinfo.id, boundary_id__boundary_type_id='SD').filter(
                    yearmonth__range=[from_yearmonth, to_yearmonth]
                ).values_list('boundary_id', flat=True).distinct()
        else:
            districts = SurveyBoundaryAgg.objects.filter(
                survey_id=surveyinfo.id, boundary_id__boundary_type_id='SD').values_list('boundary_id', flat=True).distinct()
        for questiongroup in questiongroups_list:
            q_group = QuestionGroup.objects.get(id=questiongroup)
            #strip out spaces
            q_group_name = q_group.name.replace(" ", "")
            # We are getting assessment data per questiongroup and creating XLS files per questiongroup
            assessment_data, numquestions, questioninfo = self.getAssessmentData(surveyinfo, districts, questiongroup, from_yearmonth, to_yearmonth)
            # Create the CSV/XLS file name so it is descriptive/neat
            output_file_name = self.create_file_name(filename, from_yearmonth, to_yearmonth, questiongroup, q_group_name)
            
            # Create the CSV/XLS files
            self.createXLS(surveyinfo, questioninfo, numquestions, questiongroup, assessment_data, output_file_name, skipxls, dest_folder)


    def createOutputFolder(self,surveyinfo, from_yearmonth, to_yearmonth):
        # Create the folder structure where the data will sit
        foldername = surveyinfo.name.replace(" ", "")
        parent_dir = "generated_files"
        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)
        parent_dir = os.path.join(parent_dir, "survey_data")
        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)
        folderpath = os.path.join(parent_dir,foldername)
        if not os.path.exists(folderpath):
            os.mkdir(folderpath)

        dest_folder = folderpath
        # Create the destination folder
        if from_yearmonth is not None:
            from_short_year = from_yearmonth[:-2]
            to_short_year = int(to_yearmonth[:-2])
            if int(to_short_year) == int(from_short_year):
                to_short_year = int(to_short_year) + 1
            academic_year_id = from_short_year + "-" + str(to_short_year)
            year_folder = os.path.join(folderpath, academic_year_id)
            if not os.path.exists(year_folder):
                os.mkdir(year_folder)
            dest_folder = year_folder
        return dest_folder
