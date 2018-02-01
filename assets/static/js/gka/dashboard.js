/* vi:si:et:sw=4:sts=4:ts=4 */
'use strict';
var districts = {"meta":[],'details':[]};
var entity = {"meta":[],'details':[]};
var entityDetails = {};
var topSummaryData = {};

(function() {
    var premodalQueryParams = {};

    klp.init = function() {
        klp.accordion.init();
        klp.gka_filters.init();
        klp.router = new KLPRouter();
        klp.router.init();
        klp.router.events.on('hashchange', function(event, params) {
            hashChanged(params);
        });
        klp.router.start();

        // All GKA related data are stored in GKA
        klp.GKA = {};

        $('#startDate').yearMonthSelect("init", {validYears: ['2015', '2016', '2018']});
        $('#endDate').yearMonthSelect("init", {validYears: ['2015', '2016', '2018']});

        //this is a bit of a hack to save query state when
        //triggering a modal, since modals over-ride the url
        //Works only on date modal.
        premodalQueryParams = klp.router.getHash().queryParams;
        if (premodalQueryParams.hasOwnProperty("from")) {
            var mDate = moment(premodalQueryParams.from);
            $('#startDate').yearMonthSelect("setDate", mDate);
        }
        if (premodalQueryParams.hasOwnProperty("to")) {
            var mDate = moment(premodalQueryParams.to);
            $('#endDate').yearMonthSelect("setDate", mDate);
        } else {
            $('#endDate').yearMonthSelect("setDate", moment());
        }

        $('#dateSummary').click(function(e) {
            e.preventDefault();
            var currentQueryParams = premodalQueryParams;
            var startDate = $('#startDate').yearMonthSelect("getFirstDay");
            var endDate = $('#endDate').yearMonthSelect("getLastDay");
            if (moment(startDate) > moment(endDate)) {
                klp.utils.alertMessage("End date must be after start date", "error");
                return false;
            }
            currentQueryParams['from'] = $('#startDate').yearMonthSelect("getFirstDay");
            currentQueryParams['to'] = $('#endDate').yearMonthSelect("getLastDay");
            klp.router.setHash(null, currentQueryParams);
        });

        $('a[href=#datemodal]').click(function(e) {
            premodalQueryParams = klp.router.getHash().queryParams;
        });

        $('a[href=#close]').click(function(e) {
            klp.router.setHash(null, premodalQueryParams, {'trigger': false});
        });

        $('a[href=#searchmodal]').click(function(e) {
            premodalQueryParams = klp.router.getHash().queryParams;
        });
        loadData(premodalQueryParams);
    }

    function hashChanged(params) {
        var queryParams = params.queryParams;
        //This is for the default URL localhost:8001/gka
        //No Query Params
        if(window.location.hash)
        {
            //This is a reload of localhost:8001/gka
            //No Query Params
            if(window.location.hash == '#resetButton') {
                window.location.href = '/gka';
            }
            //This is to prevent server calls when just the modal actions are called
            //This condition is triggered for eg: for localhost:8001/gka#datemodal?from=12/03/2016&to12/06/2016
            //and not for just localhost:8001/gka#datemodal
            else if(window.location.hash != '#datemodal' && window.location.hash !='#close' && window.location.hash != '#searchmodal')
            {
                loadData(queryParams)
            }
            //This is the do nothing case switch for localhost:8001/gka#datemodal
            else {//do nothing;
            }
        }
        $('#ReportContainer').show();
    }

    function loadData(params) {
        // As of August 1st, 2017, data from June 2017 is shown as default
        if(!params.from && !params.to) {
            params.from = '2017-06-01';
            params.to = '2018-12-31';
        }

        // Parameters common across all calls
        params.survey_tag = 'gka';

        loadTopSummary(params);
        // All other sections are loaded after loadTopSummary is loaded
        // as they use data fetched by loadTopSummary
    }

    function loadComparison(params) {
        var $metaXHR = klp.api.do("survey/info/class/gender", params);
        startDetailLoading();
        $metaXHR.done(function(data)
        {
            var neighbours = _.map(data.summary_comparison, function(summary){
                return {
                    name: summary.boundary_name,
                    schools: summary.schools,
                    sms: summary.sms,
                    sms_govt: summary.sms_govt,
                    sms_govt_percent: getPercent(summary.sms_govt, summary.sms),
                    assmt: summary.assessments,
                    contests: summary.contests,
                    surveys: summary.surveys
                }
            });
            var tplComparison= swig.compile($('#tpl-compareTable').html());
            var compareHTML = tplComparison({"neighbours":neighbours});
            $('#compareTable').html(compareHTML);
            renderComparisonCharts(params, data);
            stopDetailLoading();
        });
    }

    function renderComparisonCharts(params, data){

        function getSkillValue(skills, skillType, dataType) {
            var value;

            if (dataType === 'ekstep') {
                if(skills.competencies[skillType]) {
                    var total = skills.competencies[skillType].total,
                        score = skills.competencies[skillType].score;
                    value = score / total * 100;
                } else {
                    value = 0;
                }
            } else {
                for(var s in skills.competencies) {
                    var yes = 0, no = 0;
                    for(var i = 1; i <= 5; i++) {
                        if(skills.competencies[skillType + ' ' + i]) {
                            if(skills.competencies[skillType + ' ' + i].Yes && skills.competencies[skillType + ' ' + i].No) {
                                    yes += skills.competencies[skillType + ' ' + i].Yes;
                                    no += skills.competencies[skillType + ' ' + i].No;
                            }
                        }
                    }
                }
                value = yes / (yes + no) * 100;
            }

            if(value) { return value.toFixed(2); } else { return 0; }
        }

        function getNValues(section, dataType) {
            var addition = getSkillValue(section, 'Addition'),
                subtraction = getSkillValue(section, 'Subtraction'),
                multiplication = getSkillValue(section, 'Multiplication'),
                division = getSkillValue(section, 'Division');
            return [{
                meta: section.boundary_name,
                skill: 'Addition',
                value: getSkillValue(section, 'Addition', dataType)
            },{
                meta: section.boundary_name,
                skill: 'Subtraction',
                value: getSkillValue(section, 'Subtraction', dataType)
            },{
                meta: section.boundary_name,
                skill: 'Multiplication',
                value: getSkillValue(section, 'Multiplication', dataType)
            },{
                meta: section.boundary_name,
                skill: 'Division',
                value: getSkillValue(section, 'Division', dataType)
            }];
        };

        function getMetaValues(dataType) {
            var metaValues = {};
            for(var i = 1; i <= 4; i++) {
                if(!data.competency_comparison[i-1]) {
                    metaValues['n' + i] = [];
                } else {
                    var ekstepData = data.competency_comparison[i-1][0].type === dataType ? data.competency_comparison[i-1][0] : data.competency_comparison[i-1][1];
                    metaValues['n' + i] = getNValues(ekstepData, dataType);
                }
            }
            return metaValues;
        }

        var ekstepValues = getMetaValues('ekstep'),
            gpContestValues = getMetaValues('gp_contest');

        var ekstepCompetencies = {
            labels: ["Addition","Subtraction","Multiplication","Division"],
            series: [
                {
                    className: 'ct-series-f',
                    data: ekstepValues["n1"]
                },
                {
                    className: 'ct-series-a',
                    data: ekstepValues["n2"]
                },
                {
                    className: 'ct-series-g',
                    data: ekstepValues["n3"]
                },
                {
                    className: 'ct-series-o',
                    data: ekstepValues["n4"]
                }
            ],
        }

        var gpContestCompetencies = {
            labels: ["Addition","Subtraction","Multiplication","Division"],
            series: [
                {
                    className: 'ct-series-f',
                    data: gpContestValues["n1"]
                },
                {
                    className: 'ct-series-a',
                    data: gpContestValues["n2"]
                },
                {
                    className: 'ct-series-g',
                    data: gpContestValues["n3"]
                },
                {
                    className: 'ct-series-o',
                    data: gpContestValues["n4"]
                }
            ],
        }

        renderBarChart('#compareAssmtGraph', ekstepCompetencies, "Percentage of Children");
        renderBarChart('#compareGpcGraph', gpContestCompetencies, "Percentage of Children");
    }

    function loadSmsData(params) {
        startDetailLoading();

        // Fetch SMS Summary
        var $smsSummaryXHR = klp.api.do("survey/info/source/", params);
        $smsSummaryXHR.done(function(data) {
            stopDetailLoading();
            klp.GKA.smsSummary = data;
            renderSmsSummary(data);
        });

        // Fetch SMS Volume
        // Fetch users first
        var $usersXHR = klp.api.do("survey/info/users", params);
        $usersXHR.done(function(userGroups) {

            // Fetch volumes next
            var $volumesXHR = klp.api.do("survey/volume/", params);
            $volumesXHR.done(function(volumes) {
                var data = {
                    volumes: volumes,
                    user_groups: userGroups.users
                };
                stopDetailLoading();
                renderSMSUserVolumeCharts(data, params);
            });
        });

        // Fetch SMS Details
        var $detailXHR = klp.api.do("survey/detail/source/", params);
        $detailXHR.done(function(data) {
            stopDetailLoading();
            renderSMSDetails(data);
        });
    }

    function loadSurveys(params) {
        startDetailLoading();

        delete params.survey_tag;
        params.survey_id = 7;

        // Load the source for csv summary
        var $sourceXHR = klp.api.do("survey/info/source/", params);
        $sourceXHR.done(function(sourceData) {
            klp.GKA.surveySummaryData = sourceData;
            renderSurveySummary(sourceData);

            // Load the respondent summary
            var $respondentXHR = klp.api.do("survey/info/respondent/", params);
            $respondentXHR.done(function(respondentData) {
                renderRespondentChart(respondentData);
                stopDetailLoading();
            });
        });

        // Load the volumes
        var $volumeXHR = klp.api.do("survey/volume/", params);
        $volumeXHR.done(function(data) {
            renderVolumeChart(data, params);
            stopDetailLoading();
        });

        // Load the detail section
        var $detailXHR = klp.api.do("survey/detail/source/", params);
        $detailXHR.done(function(data) {
            renderSurveyQuestions(data.source);
            stopDetailLoading();
        });
    }

    function renderVolumeChart(data, params) {
        var volumes = data;

        var expectedValue = 13680;
        if(typeof(params.admin1) !== 'undefined') {
            expectedValue = 2280;
        } else if(typeof(params.school_id) !== 'undefined' || typeof(params.admin2) !== 'undefined' || typeof(params.admin3) !== 'undefined') {
            expectedValue = 0;
        }

        var $noDataAlert = $('#survey-volume-chart-no-render-alert');
        var $mobVolume = $('#mobVolume');

        $noDataAlert.hide();
        $mobVolume.show()

        if(_.isEmpty(volumes)) {
            $noDataAlert.show();
            $mobVolume.hide();
            return;
        }

        var months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var fromDate = '2017-01-01';
        if(params.from) {
            fromDate = params.from;
        }

        var monthIndex = parseInt(fromDate.split('-')[1], 10),
            yearIndex = parseInt(fromDate.split('-')[0], 10),
            volumeValues = [];

        for(var i=1; i<=12; i+=1) {
            volumeValues.push(months[monthIndex] + ' ' + yearIndex);
            monthIndex += 1;
            if(monthIndex > 12) {
                monthIndex = 1;
                yearIndex += 1;
            }
        }

        var volume_values = _.map(volumeValues, function(v){
            var month = v.split(' ')[0],
                year = v.split(' ')[1];
            return {
                'meta': v,
                'value': volumes[year] ? volumes[year][month] : 0
            };
        });

        var data = {
            labels: _.map(volume_values, function(v){ return v.meta }),
            series: [
                {
                    className: 'ct-series-b',
                    data: volume_values,
                },
                {
                    className: 'ct-series-h',
                    data: _.map(volume_values, function(v){ return expectedValue; })
                }
            ]
        }

        renderLineChart('#mobVolume', data);
    }

    function renderRespondentChart(data) {
        var labelMap = {
            'SDMC Member': 'SDMC',
            'CBO Member': 'CBO',
            'Parents': 'Parent',
            'Teachers': 'Teacher',
            'Volunteer': 'Volunteer',
            'Educated Youth': 'Youth',
            'Local Leader': 'Leader',
            'Akshara Staff': 'Akshara',
            'Elected Representative': 'Elected' ,
            'Parents': 'Parents',
            'Children': 'Children'
        };

        var labels = _.values(labelMap);

        var respondents = data.respondents;
        var meta_values = [];
        for ( var label in labelMap) {
            meta_values.push({'meta': labelMap[label], 'value': respondents[label] || 0})
        }

        var data_respondent = {
            labels: labels,
            series: [
                {
                    className: 'ct-series-a',
                    data: meta_values,
                }
            ]
        };

        renderBarChart('#mobRespondent', data_respondent);
    }

    function renderSurveyQuestions(data) {
        var questionKeys = [];
        questionKeys = [
            "mob-sdmc-meet",
            "mob-subtraction",
            "mob-addition",
            "mob-read-english",
            "mob-read-kannada",
            "mob-teacher-shortage",
            "mob-mdm-satisfactory",
            "ivrss-functional-toilets-girls"
        ];

        var questionObjects = _.map(questionKeys, function(key) {
            return getQuestion(data, 'csv', key);
        });
        var questions = getQuestionsArray(questionObjects);
        //var regroup = {}
        var tplResponses = swig.compile($('#tpl-mobResponses').html());
        // for (var each in questions)
        //     regroup[questions[each]["key"]] = questions[each];
        var html = tplResponses({"questions":questions})
        $('#surveyQuestions').html(html);
    }

    function renderSurveySummary(data) {
        data = data.source.csv;
        var tplCsvSummary = swig.compile($('#tpl-csvSummary').html());
        data["format_lastcsv"] = formatLastStory(data.last_assessment);
        data['schoolPerc'] = getPercent(data.schools_impacted, klp.GKA.topSummaryData.schools_impacted);
        var csvSummaryHTML = tplCsvSummary(data);
        $('#surveySummary').html(csvSummaryHTML);
    }


    // Renders top summary of GKA dashboard
    function loadTopSummary(params) {

        var passedFrom = params.from;
        var passedTo = params.to;

        // Top summary needs a year
        if(params.from && params.to) {
            params.year = params.from.slice(2, 4) + params.to.slice(2, 4);
        }

        // Top summary doesnt need a from and to
        delete params.from;
        delete params.to;

        // Load the summary first
        var $summaryXHR = klp.api.do("surveys/tagmappingsummary/", params);
        startSummaryLoading();
        $summaryXHR.done(function(data) {
            var topSummary = {
                education_volunteers: 0,
                total_school: data.total_schools,
                children_impacted: data.num_students,
                schools_impacted: data.num_schools
            };

            // Bring back the from and to
            params.from = passedFrom;
            params.to = passedTo;
            // And delete the year params which is not needed in subsequent calls
            delete params.year;

            // Load the users Education volunteers count
            params.survey_tag = 'gka';
            var $usersXHR = klp.api.do("survey/summary/", params);
            $usersXHR.done(function(data) {
                topSummary.active_users = (data.summary && data.summary.num_users) ? data.summary.num_users : 0; 

                klp.GKA.topSummaryData = topSummary;
                renderTopSummary(topSummary);

                // Load the rest of sections
                // loadSmsData(params);
                // loadAssmtData(params);
                // loadGPContestData(params);
                // loadSurveys(params);
                // loadComparison(params);
            });
        });
    }

    function renderTopSummary(topSummary) {
        var tplTopSummary = swig.compile($('#tpl-topSummary').html());
        var topSummaryHTML = tplTopSummary({"data": topSummary});
        stopSummaryLoading();
        $('#topSummary').html(topSummaryHTML);
    }

    function renderSmsSummary(data) {
        var summaryData = {},
            lastAssessment = null,
            tplSmsSummary = swig.compile($('#tpl-smsSummary').html());

        // Build the summary data by adding sms and konnectsms source

        data = data.source;

        // Assessment count
        summaryData.assessment_count = data.sms.assessment_count + data.konnectsms.assessment_count;

        // Schools impacted
        summaryData.schools_impacted = data.sms.schools_impacted + data.konnectsms.schools_impacted;

        // Last assessment date
        if(new Date(data.sms.last_assessment) > new Date(data.konnectsms.last_assessment)) {
            lastAssessment = data.sms.last_assessment;
        } else {
            lastAssessment = data.konnectsms.last_assessment;
        }        
        summaryData.last_assessment = lastAssessment;
        summaryData.format_lastsms = lastAssessment;

        summaryData.smsPercentage = summaryData.schools_impacted / summaryData.assessment_count * 100;
        summaryData.smsPercentage = Math.floor(summaryData.smsPercentage);

        var smsSummaryHTML = tplSmsSummary(summaryData);
        $('#smsSummary').html(smsSummaryHTML);
    }


    function renderSMSDetails(data) {
        data = data.source;
        
        var SMSQuestionKeys = [
                "ivrss-gka-trained",
                "ivrss-math-class-happening",
                "ivrss-gka-tlm-in-use",
                "ivrss-gka-rep-stage",
                "ivrss-group-work"
            ],
            questionObjects = _.map(SMSQuestionKeys, function(key) {
                return getQuestion(data, 'sms', key);
            }),
            questions = getQuestionsArray(questionObjects),
            regroup = {},
            tplResponses = swig.compile($('#tpl-smsResponses').html());
        
        for (var each in questions) {
            regroup[questions[each]["key"]] = questions[each];
        }

        $('#smsQuestions').html(tplResponses({"questions":regroup}));
    }

    function renderSMSUserVolumeCharts(data, params)  {

        var meta_values = [];
        var volumes = data;

        // Set the expected values of line chart
        var expectedValue = 13680;
        if(typeof(params.admin1) !== 'undefined') {
            expectedValue = 2280;
        } else if(typeof(params.school_id) !== 'undefined' || typeof(params.admin2) !== 'undefined' || typeof(params.admin3) !== 'undefined') {
            expectedValue = 0;
        }

        // Utility function for preparing volumes
        function prepareVolumes(year) {
            var values = [];

            for(var v in data.volumes[year]) {
                values.push({
                    meta: v + ' ' + year,
                    value: data.volumes[year][v]
                });
            }
            return values;
        }

        for (var m in data.user_groups) {
            if(m) {
                meta_values.push({
                    meta: m,
                    value: data.user_groups[m]
                });
            }
        }

        // Build data for bar chart and render it
        var sms_sender = {
            labels: _.map(meta_values, function(m){ return m.meta; }),
            series: [
                {
                    className: 'ct-series-b',
                    data: meta_values,
                }
            ],
        }
        renderBarChart('#smsSender', sms_sender);

        // Build the data for line chart and render it
        var months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var fromDate = '2017-06-01';
        if(params.from) {
            fromDate = params.from;
        }

        var monthIndex = parseInt(fromDate.split('-')[1], 10),
            yearIndex = parseInt(fromDate.split('-')[0], 10),
            volumeValues = [];

        for(var i=1; i<=12; i+=1) {
            volumeValues.push(months[monthIndex] + ' ' + yearIndex);
            monthIndex += 1;
            if(monthIndex > 12) {
                monthIndex = 1;
                yearIndex += 1;
            }
        }

        var volume_values = _.map(volumeValues, function(v){
            var month = v.split(' ')[0],
                year = v.split(' ')[1];

            return {
                'meta': v,
                'value': volumes[year] ? volumes[year][month] : 0
            };
        });

        var sms_volume = {
            labels: _.map(volume_values, function(v){ return v.meta }),
            series: [
                {
                    className: 'ct-series-b',
                    data: volume_values,
                },
                {
                    className: 'ct-series-h',
                    data: _.map(volume_values, function(v){ return expectedValue; })
                }
            ]
        }

        var chartLabel = '';

        if(!expectedValue) {
            sms_volume.series = [sms_volume.series[0]];
            chartLabel = "<div class='center-text font-small uppercase'>" +
                        "<span class='fa fa-circle brand-green'></span> Actual Volumes</div>"
        } else {
            chartLabel = "<div class='center-text font-small uppercase'><span class='fa fa-circle brand-turquoise'></span>"+
                        " Expected Volumes <span class='fa fa-circle brand-green'></span> Actual Volumes</div>"
        }

        renderLineChart('#smsVolume', sms_volume);
        $('#smsLegend').html(chartLabel);
    }

    function loadAssmtData(params) {

        delete params.survey_tag;
        params.survey_id = 3;
        
        // Load summary first
        // TODO: Check if we need to pass the survey_tag=ekstep
        // params.survey_tag = 'ekstep';
        var $summaryXHR = klp.api.do("survey/summary/", params);
        $summaryXHR.done(function(summaryData) {
            summaryData = summaryData.summary;

            // Load details next
            var $keyXHR = klp.api.do("survey/detail/key/", params);
            $keyXHR.done(function(detailKeydata) {

                var topSummary = klp.GKA.topSummaryData;
                var tot_gka_schools = topSummary.total_school;
                var schools_assessed = summaryData.schools_impacted;
                var schools_perc = getPercent(
                    schools_assessed, tot_gka_schools
                );
                var children = summaryData.children_impacted;
                var children_impacted = topSummary.children_impacted;
                var children_perc = getPercent(children, children_impacted);
                var last_assmt = summaryData.last_assessment;
                var dataSummary = {
                    "count": summaryData.total_assessments,
                    "schools": schools_assessed,
                    "schools_perc": schools_perc,
                    "children": children,
                    "children_perc": children_perc,
                    "last_assmt": formatLastStory(last_assmt)
                }
                renderAssmtSummary(dataSummary);
                renderAssmtCharts(detailKeydata);

                var $volumeXHR = klp.api.do("survey/volume/", params);
                $volumeXHR.done(function(data) {
                    stopDetailLoading();
                    renderAssmtVolumeChart(data, params);
                });

            });
        });
    }

    function renderAssmtSummary(data) {
        var tplAssmtSummary = swig.compile($('#tpl-assmtSummary').html());
        var assmtSummaryHTML = tplAssmtSummary({'assmt':data});
        $('#assmtSummary').html(assmtSummaryHTML);
        var tplAssmtCoverage = swig.compile($('#tpl-assmtCoverage').html());
        var assmtCoverageHTML = tplAssmtCoverage({'assmt':data});
        $('#assmtCoverage').html(assmtCoverageHTML);

    }

    function renderAssmtCharts(data) {
        function getAssmtPerc(scores, topic) {
            if (scores[topic]) {
              return getPercent(scores[topic].score, scores[topic].total)
            } else {
              return getPercent(0, 0)
            }
        }

        var scores = data.scores

        const labels = ['Number Sense', 'Addition', 'Subtraction', 'Multiplication', 'Division', 'Fractions', 'Decimals', 'Shapes', 'Area', 'Money', 'Word Problem'];
        var meta_values = _.map(labels, (label) => {
          return {
            meta: label,
            value: getAssmtPerc(scores, label)
          }
        })

        var competencies = {
            labels: labels,
            series: [
                {
                    className: 'ct-series-i',
                    data: meta_values,
                    //distributed_series:true
                }
            ],
        }
        renderBarChart('#assmtCompetancy', competencies, "Percentage of Children");
    }

    function renderAssmtVolumeChart(volumes, params) {

       var expectedValue = 68000;
        if(typeof(params.admin1) !== 'undefined') {
            expectedValue = 11000;
        } else if(typeof(params.school_id) !== 'undefined' || typeof(params.admin2) !== 'undefined' || typeof(params.admin3) !== 'undefined') {
            expectedValue = 0;
        }

        var months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var fromDate = '2017-01-01';
        if(params.from) {
            fromDate = params.from;
        }
        var monthIndex = parseInt(fromDate.split('-')[1], 10),
            yearIndex = parseInt(fromDate.split('-')[0], 10),
            volumeValues = [];

        for(var i=1; i<=12; i+=1) {
            volumeValues.push(months[monthIndex] + ' ' + yearIndex);
            monthIndex += 1;
            if(monthIndex > 12) {
                monthIndex = 1;
                yearIndex += 1;
            }
        }

        var volume_values = _.map(volumeValues, function(v){
            var month = v.split(' ')[0],
                year = v.split(' ')[1];
            return {
                'meta': v,
                'value': volumes[year] ? volumes[year][month] : 0
            };
        });

        var assmt_volume = {
            labels: _.map(volume_values, function(v){return v.meta}),
            series: [
                {
                    className: 'ct-series-g',
                    data: volume_values,
                },
                {
                    className: 'ct-series-d',
                    data: [expectedValue,expectedValue,expectedValue,expectedValue,expectedValue,expectedValue,expectedValue,expectedValue,expectedValue,expectedValue,expectedValue, expectedValue]
                }
            ]
        }

        var chartLabel = '';
        if(!expectedValue) {
            assmt_volume.series = [assmt_volume.series[0]];
            chartLabel = "<div class='center-text font-small uppercase'>"+
                        "<span class='fa fa-circle pink-salmon'></span> Actual Volumes</div>"
        } else {
            chartLabel = "<div class='center-text font-small uppercase'><span class='fa fa-circle brand-orange'></span>"+
                        " Expected Volumes <span class='fa fa-circle pink-salmon'></span> Actual Volumes</div>"
        }

        renderLineChart('#assmtVolume', assmt_volume);
        $('#avLegend').html(chartLabel);

    }

    function loadGPContestData(params){
        delete params.survey_tag;
        params.survey_id = 2;

        var metaURL = "survey/info/class/gender/";
        var $metaXHR = klp.api.do(metaURL, params);
        $metaXHR.done(function(data) {

            var dataSummary = {
                "summary": {
                    "schools":data.summary.schools,
                    "gps": data.summary.gps,
                    "contests":data.summary.contests,
                    "children": data.summary.students
                },
                "Class 4": {
                    "boy_perc": getPercent(data['4'].males_score, data['4'].males),
                    "girl_perc": getPercent(data['4'].females_score, data['4'].females),
                    "total_studs": getPercent(
                        data['4'].males_score + data['4'].females_score,
                        data['4'].males+data['4'].females
                    )
                },
                "Class 5": {
                    "boy_perc": getPercent(data['5'].males_score, data['5'].males),
                    "girl_perc": getPercent(data['5'].females_score, data['5'].females),
                    "total_studs": getPercent(
                        data['5'].males_score + data['5'].females_score,
                        data['5'].males + data['5'].females
                    )
                },
                "Class 6": {
                    "boy_perc": getPercent(data['6'].males_score, data['6'].males),
                    "girl_perc": getPercent(data['6'].females_score, data['6'].females),
                    "total_studs": getPercent(
                        data['6'].males_score + data['6'].females_score,
                        data['6'].males + data['6'].females
                    )
                }
            }

            var tplSummary = swig.compile($('#tpl-gpcSummary').html());
            var summaryHTML = tplSummary({"data": dataSummary["summary"]});
            $('#gpcSummary').html(summaryHTML);

            tplSummary = swig.compile($('#tpl-genderGpcSummary').html());
            summaryHTML = tplSummary({"data":dataSummary["Class 4"]});
            $('#gpcGender_class4').html(summaryHTML);

            tplSummary = swig.compile($('#tpl-genderGpcSummary').html());
            summaryHTML = tplSummary({"data":dataSummary["Class 5"]});
            $('#gpcGender_class5').html(summaryHTML);

            tplSummary = swig.compile($('#tpl-genderGpcSummary').html());
            summaryHTML = tplSummary({"data":dataSummary["Class 6"]});
            $('#gpcGender_class6').html(summaryHTML);

            renderGPContestCharts(data);
        })
    }


    function renderGPContestCharts(data) {
        function aggCompetancies(competancies) {
            var topics = ["Number concept","Addition","Subtraction","Multiplication","Division","Patterns","Shapes","Fractions","Decimal","Measurement"]
            var competanciesKeys = Object.keys(competancies)
            var result = {}
            for (var topic of topics) {
                result[topic] = {'Yes': 0, 'No': 0}

                for (var key of competanciesKeys) {
                    if (key.indexOf(topic) !== -1) {
                        result[topic]['Yes'] += competancies[key]['Yes']
                        result[topic]['No'] += competancies[key]['No']
                    }
                }
            }
            return result
        }

        var class4competancies = genCompetancyChartObj(aggCompetancies(data['4'].competancies));
        var class5competancies = genCompetancyChartObj(aggCompetancies(data['5'].competancies));
        var class6competancies = genCompetancyChartObj(aggCompetancies(data['6'].competancies));
        renderBarChart('#gpcGraph_class4', class4competancies, "Percentage of Children");
        renderBarChart('#gpcGraph_class5', class5competancies, "Percentage of Children");
        renderBarChart('#gpcGraph_class6', class6competancies, "Percentage of Children");
    }

    function genCompetancyChartObj(aggCompetancies) {
        function getTopicPerc(competancy){
            var yesVal = competancy['Yes'], noVal = competancy['No']
            return getPercent(yesVal, yesVal+noVal)
        }
        var meta_values = [
            {"meta":"Number Concepts", "value": getTopicPerc(aggCompetancies['Number concept'])},
            {"meta":"Addition","value": getTopicPerc(aggCompetancies['Addition'])},
            {"meta":"Subtraction","value": getTopicPerc(aggCompetancies['Subtraction'])},
            {"meta":"Multiplication","value": getTopicPerc(aggCompetancies['Multiplication'])},
            {"meta":"Division","value": getTopicPerc(aggCompetancies['Division'])},
            {"meta":"Patterns","value": getTopicPerc(aggCompetancies['Patterns'])},
            {"meta":"Shapes and Spatial Understanding","value":getTopicPerc(aggCompetancies['Shapes'])},
            {"meta":"Fractions","value": getTopicPerc(aggCompetancies['Fractions'])},
            {"meta":"Decimal","value": getTopicPerc(aggCompetancies['Decimal'])},
            {"meta":"Measurement - weight and time","value":getTopicPerc(aggCompetancies['Measurement'])}
        ];
        var competencies = {
            labels: ["Number Concepts","Addition","Subtraction","Multiplication","Division","Patterns","Shapes","Fractions","Decimal","Measurement"],
            series: [
                {
                    className: 'ct-series-n',
                    data: meta_values,
                    //distributed_series:true
                }
            ]
        }
        return competencies
    }

    function renderBarChart(elementId, data, yTitle=' ') {

        var options = {
            //seriesBarDistance: 10,
            axisX: {
                showGrid: true,
            },
            axisY: {
                showGrid: true,
            },
            plugins: [
                Chartist.plugins.tooltip(),
                Chartist.plugins.ctAxisTitle({
                  axisX: {
                    //No label
                  },
                  axisY: {
                    axisTitle: yTitle,
                    axisClass: 'ct-axis-title',
                    offset: {
                      x: 0,
                      y: 0
                    },
                    textAnchor: 'middle',
                    flipTitle: false
                  }
                })
            ]
        };

        var responsiveOptions = [
            ['screen and (max-width: 749px)', {
                seriesBarDistance: 5,
                height: '200px',
                axisX: {
                  labelInterpolationFnc: function (value) {
                    if (value.length > 9) {
                      return value.slice(0, 9) + '...'
                    }

                    return value;
                  },
                  offset: 80
                }
            }]
        ];

        var $chart_element = Chartist.Bar(elementId, data, options, responsiveOptions).on('draw', function(chartData) {
            if (chartData.type === 'bar') {
                chartData.element.attr({
                    style: 'stroke-width: 15px;'
                });
            }
            if (chartData.type === 'label' && chartData.axis === 'x') {
                chartData.element.attr({
                    width: 200
                })
            }
        });
    }

    function renderLineChart(elementId, data) {

        var options = {
            seriesBarDistance: 10,
            axisX: {
                showGrid: true,
            },
            axisY: {
                showGrid: true,
            },
            plugins: [
                Chartist.plugins.tooltip()
            ]
        };

        var responsiveOptions = [
            ['screen and (max-width: 749px)', {
                seriesBarDistance: 5,
                height: '200px',
                axisX: {
                  labelInterpolationFnc: function (value) {
                    if (value.length > 9) {
                      return value.slice(0, 9) + '...'
                    }

                    return value;
                  },
                  offset: 80,
                }
            }]
        ];

        var $chart_element = Chartist.Line(elementId, data, options, responsiveOptions).on('draw', function(data) {
            // if (data.type === 'bar') {
            //     data.element.attr({
            //         style: 'stroke-width: 15px;'
            //     });
            // }
            if (data.type === 'label' && data.axis === 'x') {
                data.element.attr({
                    width: 200
                })
            }
        });
    }



    /*
        Helper functions
            TODO: move to separate file and document.
     */
    function startSummaryLoading() {
        var $container = $('#ReportContainer');
        $container.find('.js-summary-container').startLoading();
    }

    function startDetailLoading() {
        var $container = $('#ReportContainer');
        $container.find('.js-detail-container').startLoading();
    }

    function stopSummaryLoading(schoolType) {
        var $container = $('#ReportContainer');
        $container.find('.js-summary-container').stopLoading();
    }

    function stopDetailLoading(schoolType) {
        var $container = $('#ReportContainer');
        $container.find('.js-detail-container').stopLoading();
    }

    function getYear(dateString) {
        return dateString.split("-")[0];
    }

    $.fn.startLoading = function() {
        var $this = $(this);
        var $loading = $('<div />').addClass('fa fa-cog fa-spin loading-icon-base js-loading');
        $this.empty().append($loading);
    }

    $.fn.stopLoading = function() {
        var $this = $(this);
        $this.find('.js-loading').remove();
    }

    function formatLastStory(last_story) {
        var date =' ';
        var time = ' ';
        if(last_story != null) {
            if(last_story.indexOf('T') != -1) {
                var arr = last_story.split('T');
                date = moment(arr[0], "YYYY-MM-DD").format("DD MMM YYYY");
                time += moment(arr[1], "HH:mm:ss").format("h:mm:ss a");
            } else {
                date = moment(last_story, "YYYY-MM-DD").format("DD MMM YYYY");
            }
        }
        return date + time;
    }

    function getScore(answers, option) {
        if (!answers) { return 0; }
        option = option ? option: 'Yes';
        var score = answers[option] ? answers[option]: 0;
        return score;
    }

    function getTotal(answers) {
        if (!answers) { return 0; }
        var yes = answers['Yes'] ? answers['Yes'] : 0;
        var no = answers['No'] ? answers['No'] : 0;
        return yes + no;
    }

    function getPercent(score, total) {
        if (total == 0 || score == 0) {
            return 0;
        }
        return parseFloat((score / total) * 100).toFixed(2);
    }

    function getQuestion(data, source, key) {
        for (var i=0, len=data[source].length; i<len; i++) {
            var question = data[source][i];
            if (question.question.key === key) {
                return question;
            }
        }
        return false;
    }

    function getQuestionsArray(questions) {
        return _.map(questions, function(question, seq) {
            var score = getScore(question.answers, 'Yes');
            var total = getTotal(question.answers);
            var percent = getPercent(score, total);
            var questionObj = question.question;
            return {
                'question': questionObj? questionObj.display_text: '',
                'key': questionObj? questionObj.key: '',
                'score': score,
                'total': total,
                'percent': percent
            };
        });
    }

})();
