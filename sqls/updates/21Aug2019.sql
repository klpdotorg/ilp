update assessments_competencyquestionmap set lang_key= (select distinct lang_key from assessments_competencyquestionmap where key='Number Recognition' and questiongroup_id=47) where questiongroup_id in (62,63) and key='Number Recognition';