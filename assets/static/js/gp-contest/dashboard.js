'use strict';

(function() {
    klp.init = function() {
        // All GKA related data are stored in GKA
        klp.GP = {};
        klp.GP.routerParams = {};

        var searchByGPs = false;
        var selectedConverageTab = '2016';
        var selectedPerformanceTab = 'basic';
        var selectedComparisonTab = 'year';
        var years = ["2016", "2017", "2018"];
        var performanceTabs = [
            {
                text: 'Basic',
                value: 'basic',
            },
            {
                text: 'Details',
                value: 'details',
            }
        ];
        var comparisonTabs = [
            {
                text: 'Year',
                value: 'year'
            }
        ];
        var tabs = _.map(years, function(tab) {
            return {
                value: tab,
                start_date: `${tab}-06-01`,
                end_date: `${Number(tab) + 1}-04-30`
            }
        })
        var $educational_hierarchy_checkbox = $("#select-educational-hrc");
        var $gp_checkbox = $("#select-gp-checkbox");
        var $select_school_cont = $("#select-school-cont");
        var $select_cluster_cont = $("#select-cluster-cont");
        var $select_gp_cont = $("#select-gp-cont");
            
        // This function is used as a callback to accordion init function
        // to determine which section to load when a user clicks a
        // section
        klp.GP.accordionClicked = function($el) {
            var isSectionVisible = $el.is(':visible'),
            elId = $el.attr('id'),
            functionMap = {
                "class-4-performance": loadPerformance,
                "class-5-performance": loadPerformance,
                "class-6-performance": loadPerformance,
            };
            if (!isSectionVisible) { return; }
    
            if (typeof(functionMap[elId]) === 'function') {
                functionMap[elId](klp.GP.routerParams);
            } else {
                console.log('Accordion event handler returned an unknow id');
            }
        }

        // Initialize accordion, filters and router
        klp.accordion.init();
        klp.gp_filters.init();
        klp.router = new KLPRouter();
        klp.router.init();
        klp.router.events.on('hashchange', function(event, params) {
            hashChanged(params);
        });
        klp.router.start();

        $('#startDate').yearMonthSelect("init", {validYears: ['2016', '2017', '2018', '2019']});
        $('#endDate').yearMonthSelect("init", {validYears: ['2016', '2017', '2018', '2019']});
        $('#startDate').yearMonthSelect("setDate", moment("20180601", "YYYYMMDD"));
        $('#endDate').yearMonthSelect("setDate", moment("20190331", "YYYYMMDD"));

        // Triggers hash changes into appropriate function calls
        function hashChanged(params) {
            var queryParams = params.queryParams;

            klp.GP.routerParams = queryParams;

            loadPerformance();
            loadCoverage();
                
            if (window.location.hash) {
                if (window.location.hash == '#resetButton') {
                    window.location.href = '/gp-contest';
                }
                else if(window.location.hash != '#datemodal' && window.location.hash !='#close' && window.location.hash != '#searchmodal') {
                }
            }
        }

        function showDefaultFilters() {
            // Setting educational_hierarchy by default true
            $educational_hierarchy_checkbox.prop("checked", true)
        }

        // hideSearchFields to hide search fields based on searchByGPs filter
        function hideSearchFields() {
            if (searchByGPs) {
                $select_school_cont.css("display", "none");
                $select_cluster_cont.css("display", "none");
                $select_gp_cont.css("display", "block");
            } else {
                $select_school_cont.css("display", "block");
                $select_cluster_cont.css("display", "block");
                $select_gp_cont.css("display", "none");
            }
        }

        // This function renders coverage tabs
        function renderYearsTabs() {
            var tplYearTab = swig.compile($('#tpl-tabs').html());
            var yearTabHTML = tplYearTab({ tabs: _.map(tabs, function(tab) {
                return { text: tab.value, value: tab.value };
            })});
            
            $('#year-tabs').html(yearTabHTML);
        }

        // This function renders performance tabs
        function renderPerformanceTabs() {
            var tplPerformanceTab = swig.compile($('#tpl-tabs').html());
            var performanceTabHTML = tplPerformanceTab({ tabs: performanceTabs });

            $('#performance-tabs').html(performanceTabHTML);
        }

        // this function renders comparison tabs
        function renderComaprisonTabs() {
            var tplComparisonTab = swig.compile($('#tpl-tabs').html());
            var comparisonTabHTML = tplComparisonTab({ tabs: comparisonTabs });

            $('#comparison-tabs').html(comparisonTabHTML);
        }

        function selectTab(tab, goingToSelectTab) {
            var $currentTab = $(`#${tab.value}`);
            if (tab.value === goingToSelectTab) {
                $currentTab.addClass("selected-gp-tab");
            } else {
                $currentTab.removeClass("selected-gp-tab");
            }
        }

        // This function select the tab
        function selectYearTab(goingToSelectTab) {
            _.forEach(tabs, function(tab) {
                selectTab(tab, goingToSelectTab);
            });
        }

        // This function select the performance tab
        function selectPerformanceTab(goingToSelectTab) {
            _.forEach(performanceTabs, function(tab) {
                selectTab(tab, goingToSelectTab);
            });
        }

        // This function select the Comparison Tab
        function selectComparisonTab(goingToSelectTab) {
            _.forEach(comparisonTabs, function(tab) {
                selectTab(tab, goingToSelectTab);
            });
        }

        $('#search_button').click(function(e){
            var district_id = $("#select-district").val(),
                block_id = $("#select-block").val(),
                cluster_id = $("#select-cluster").val(),
                institution_id = $("#select-school").val(),
                gp_id = $("#select-gp").val(),
                start_date = $('#startDate').yearMonthSelect("getFirstDay"),
                end_date = $('#endDate').yearMonthSelect("getLastDay"),
                url = '/gp-contest/#searchmodal';

            if (start_date && end_date) {
                url += '?from=' + start_date + '&to=' + end_date;
            } else {
                // url += 'default_date=true';
            }
            
            if (searchByGPs) {
                if (gp_id) {
                    url += '&electionboundary_id=' + gp_id;
                } else {
                    if (block_id) {
                        url += '&boundary_id' + block_id;
                    } else if (district_id) {
                        url += '&boundary_id' + district_id;
                    }
                }
            } else {
                if (institution_id) {
                    url += '&institution_id=' + institution_id;
                } else {
                    if (cluster_id) {
                        url += '&boundary_id=' + cluster_id;
                    } else if(block_id) {
                        url += '&boundary_id=' + block_id;
                    } else if(district_id) {
                        url += '&boundary_id=' + district_id;
                    }
                }
            }
            e.originalEvent.currentTarget.href = url;
        });
        
        // This returns search entity type and entity Id
        function getSearchedEntityInfo() {
            var routerParams = klp.GP.routerParams;

            if (routerParams.electionboundary_id) {
                return {
                    type: 'electionboundary_id',
                    value: routerParams.electionboundary_id,
                }
            }

            if (routerParams.institution_id) {
                return {
                    type: 'institution_id',
                    value: routerParams.institution_id,
                }
            }

            if (routerParams.boundary_id) {
                return {
                    type: 'boundary_id',
                    value: routerParams.boundary_id,
                }
            }

            return null;
        }

        // This function check for selected boundary and update that in the post url
        function checkForUrlParams(url) {
            var entityInfo = getSearchedEntityInfo();
            if (!entityInfo) {
                return url;
            }

            return `${url}&${entityInfo.type}=${entityInfo.value}`;
        };

        // Fetch coverage information
        function loadCoverage() {
            $("#gp-coverage").startLoading();
        
            var selectedYearInfo = tabs.find(function(tab) {
                return tab.value === selectedConverageTab;
            });
            var coverageUrl = checkForUrlParams(`survey/summary/?survey_id=2&from=${selectedYearInfo.start_date}&to=${selectedYearInfo.end_date}`);
            var fetchGPUrl = checkForUrlParams(`survey/detail/electionboundary/?survey_id=2&from=${selectedYearInfo.start_date}&to=${selectedYearInfo.end_date}`);
            var $coverageXHR = klp.api.do(
                coverageUrl
            );

            $coverageXHR.done(function(result) {
                var $gpXHR = klp.api.do(
                    fetchGPUrl
                );

                $gpXHR.done(function(gpData) {
                    var tplCoverage = swig.compile($('#tpl-coverage').html());
                    var coverageHTML = tplCoverage({ data: result.summary, gp: gpData.GP });
                    
                    $('#gp-coverage').html(coverageHTML);
                    $("#gp-coverage").stopLoading();
                });
            });
        }

        function getConcepts(conceptsData, classNumber) {
            var assessments = conceptsData[`Class ${classNumber} Assessment`];
            return Object.keys(assessments).map(function(key) {
                return assessments[key];
            })
        }

        function getConceptGroupChartData(conceptData) {
            var chartData = _.reduce(conceptData, function(soFar, value, key) {
                if (typeof value === 'object') {
                    soFar.labels.push(key);
                    soFar.series.push(Math.round((value.score / value.total ) * 100));
                }

                return soFar;
            }, { labels: [], series: []});

            return {
                labels: chartData.labels,
                series: [chartData.series]
            };
        }

        function getConceptGroups(concepts, selectedConceptGroupIndex) {
            return _.reduce(concepts[selectedConceptGroupIndex], function(soFar, value, index) {
                if (typeof value === 'object') {
                    soFar.push(value);
                }
                return soFar;
            }, []);
        }

        // This function creates graph element
        function createGraphElement(id, appendToId) {
            $('<div/>', {
                id: id,
                class: 'ct-chart ct-minor-seventh js-detail-container chartist-container bar-chart one-row-chart',
            }).appendTo(`#${appendToId}`);
        }

        // This function shows concepts groups and micro concepts
        function handleConcepts(clickedConceptValue, chartData, performanceResult, classNumber) {
            var seriesValues = chartData[`class${classNumber}`].series[0];
            var selectedConceptIndex = seriesValues.indexOf(Number(clickedConceptValue));

            var concepts = getConcepts(performanceResult, classNumber);
            var conceptGroupChartData = getConceptGroupChartData(concepts[selectedConceptIndex]); 

            if ($(`#gp-performance-class-${classNumber}-concept-group`).length !== 0) {
                $(`#gp-performance-class-${classNumber}-concept-group`).remove();
            }
            createGraphElement(`gp-performance-class-${classNumber}-concept-group`, `concept-groups-class-${classNumber}`);

            renderBarChart(`#gp-performance-class-${classNumber}-concept-group`, conceptGroupChartData);

            $(`#close-concept-group-class-${classNumber}`).css('display', 'inline-block');
            $(`#concept-group-header-class-${classNumber}`).css('display', 'block');

            $(`#close-concept-group-class-${classNumber}`).click(() => {
                $(`#gp-performance-class-${classNumber}-concept-group`).remove();
                $(`#close-concept-group-class-${classNumber}`).css('display', 'none');
                $(`#concept-group-header-class-${classNumber}`).css('display', 'none');
            })
            
            $(`#gp-performance-class-${classNumber}-concept-group`).click(function(conceptGroupEvent) {
                var clickedConceptGroupValue = conceptGroupEvent.target.getAttribute('ct:value');
                var conceptGroups = getConceptGroups(concepts, selectedConceptIndex);
                var selectedConceptGroupIndex = conceptGroupChartData.series[0].indexOf(Number(clickedConceptGroupValue))
                var selectedConceptGroup = conceptGroups[selectedConceptGroupIndex]
                var microConceptChartData = getConceptGroupChartData(selectedConceptGroup);

                if ($(`#gp-performance-class-${classNumber}-micro-concept`).length !== 0) {
                    $(`#gp-performance-class-${classNumber}-micro-concept`).remove(); 
                }
                createGraphElement(`gp-performance-class-${classNumber}-micro-concept`, `micro-concepts-class-${classNumber}`);

                renderBarChart(`#gp-performance-class-${classNumber}-micro-concept`, microConceptChartData);

                // showing close button and header
                $(`#close-micro-concept-class-${classNumber}`).css('display', 'inline-block');
                $(`#micro-concept-header-class-${classNumber}`).css('display', 'block');

                $(`#close-micro-concept-class-${classNumber}`).click(() => {
                    $(`#gp-performance-class-${classNumber}-micro-concept`).remove();
                    $(`#close-micro-concept-class-${classNumber}`).css('display', 'none');
                    $(`#micro-concept-header-class-${classNumber}`).css('display', 'none');
                })
            })
        }

        // For resetting the details graph
        function resetDetailsGraph(value) {
            if (value !== 'details') {
                for (var i = 4; i <= 6; i++) {
                    $(`#gp-performance-class-${i}-micro-concept`).remove();
                    $(`#close-micro-concept-class-${i}`).css('display', 'none');
                    $(`#gp-performance-class-${i}-concept-group`).remove();
                    $(`#close-concept-group-class-${i}`).css('display', 'none');
                    $(`#concepts-header-class-${i}`).css('display', 'none');
                    $(`#concept-group-header-class-${i}`).css('display', 'none');
                    $(`#micro-concept-header-class-${i}`).css('display', 'none');
                }
            }

            if (value === "details") {
                for (var i = 4; i <= 6; i++) {
                    $(`#concepts-header-class-${i}`).css('display', 'block');
                }
            }
        }

        // Fetch performance info
        function loadPerformance() {
            // Starting all spinners
            $("#gp-performance-class-4").startLoading();
            $("#gp-performance-class-5").startLoading();
            $("#gp-performance-class-6").startLoading();

            var routerParams = klp.GP.routerParams;	
            var dateParams = {};

            var LABELS_REQUIRED = [
                'Number Concept',
                'Addition',
                'Subtraction',
                'Multiplication',
                'Division',
            ];

            var selectedYearInfo = tabs.find(function(tab) {
                return tab.value === selectedConverageTab;
            });

            if (routerParams.from && routerParams.to) {
                dateParams.from = routerParams.from;
                dateParams.to = routerParams.to;
            } else {
                var defaultDateParams = getDefaultAcademicYear();
                dateParams.from = defaultDateParams.from;
                dateParams.to = defaultDateParams.to; 
            }

            if (selectedPerformanceTab === 'basic') {
                var basicPerformanceUrl = checkForUrlParams(`survey/detail/questiongroup/key/?survey_id=2&from=${dateParams.from}&to=${dateParams.to}`);
                var $performanceXHR = klp.api.do(basicPerformanceUrl);

                $performanceXHR.done(function(result) {
                    var chartData = {},
                        labels = [],
                        series = [];

                    for (var i = 4; i <= 6; i++) {
                        labels = LABELS_REQUIRED;
                        series = _.map(LABELS_REQUIRED, function(label) {
                            var graphVals = result['Class ' + i +' Assessment'];
                            if (!graphVals[label]) {
                                return 0;
                            }

                            return Math.round((graphVals[label].score / graphVals[label].total) * 100);
                        });

                        chartData['class' + i] = {labels: [], series: [[]]};
                        _.forEach(labels, function(l, index) {
                            if(!_.includes(LABELS_REQUIRED, l)) { return; }

                            chartData['class' + i].labels.push(l);
                            chartData['class' + i].series[0].push(series[index]);
                        });


                    // chartData['class' + i] = {
                    //   labels: _.keys(result['Class ' + i +' Assessment']),
                    //   series: [_.map(result['Class ' + i +' Assessment'], function(r){
                    //     return Math.round((r.score / r.total) * 100);
                    //   })]
                // };
                    }

                    renderBarChart('#gp-performance-class-4', chartData.class4);
                    renderBarChart('#gp-performance-class-5', chartData.class5);
                    renderBarChart('#gp-performance-class-6', chartData.class6);

                    // Stoping all spinners
                    $("#gp-performance-class-4").stopLoading();
                    $("#gp-performance-class-5").stopLoading();
                    $("#gp-performance-class-6").stopLoading();
                });
            } else {
                // var detailsPerformanceUrl = checkForUrlParams(`survey/detail/questiongroup/qdetails/?survey_id=2&from=${selectedYearInfo.start_date}&to=${selectedYearInfo.end_date}`);
                // var $performanceXHR = klp.api.do(detailsPerformanceUrl);
                
                // $performanceXHR.done(function(performanceResult) {
                    var performanceResult = {"Class 6 Assessment":{"Shapes":{"score":10174,"total":31700,"Mensuration":{"Mesuration (Area, perimeter, circumference, radius, diameter etc)":{"score":2236,"total":15850},"total":15850,"score":2236},"Flat shapes":{"2D shapes attributes":{"score":7938,"total":15850},"score":7938,"total":15850}},"Number Operations":{"Multiplication":{"score":6201,"total":15850,"Long Multiplication (Abstract)":{"score":6201,"total":15850}},"Subtraction":{"score":10349,"total":15850,"Subtraction with Borrow (Abstratct)":{"score":10349,"total":15850}},"score":40777,"total":79250,"Addition":{"score":14135,"Addition with Carry (Abstract)":{"score":14135,"total":15850},"total":15850},"Money":{"score":2995,"total":15850,"Word Problem - Measurements - Money":{"score":2995,"total":15850}},"Division":{"score":7097,"Long Division without Reminder":{"score":7097,"total":15850},"total":15850}},"Number Sense":{"Multiplication":{"score":6025,"total":15850,"Long Multiplication (Abstract)":{"score":6025,"total":15850}},"score":43515,"Decimals":{"total":15850,"Relate Fractions to Decimal numbers and vice versa":{"score":4972,"total":15850},"score":4972},"total":95100,"Division":{"score":7155,"Division - word problem":{"score":7155,"total":15850},"total":15850},"Numbers":{"score":12564,"Oral number name association":{"score":12564,"total":15850},"total":15850},"Fractions":{"score":12799,"Part of a whole object (2D shapes) - Fractions":{"score":4533,"total":15850},"total":31700,"Fractions using pictures":{"score":8266,"total":15850}}},"Measurements":{"Time":{"Word Problem - Measurements - Time":{"score":4852,"total":15850},"total":15850,"score":4852},"score":21239,"Division":{"score":7757,"total":15850,"Word Problem - Measurements - Money":{"score":7757,"total":15850}},"total":47550,"Weight":{"total":15850,"Convert larger units to smaller units and vice versa - Weight":{"score":8630,"total":15850},"score":8630}}},"Class 5 Assessment":{"Shapes":{"score":11495,"total":35115,"Patterns in shapes":{"score":5479,"total":17558,"Observes and extends patterns in sequence of shapes":{"score":5479,"total":17558}},"Flat shapes":{"2D shapes attributes":{"score":6016,"total":17557},"score":6016,"total":17557}},"Number Operations":{"Multiplication":{"score":6235,"total":17558,"Long Multiplication (Abstract)":{"score":6235,"total":17558}},"Subtraction":{"score":10235,"total":17558,"Subtraction with Borrow (Abstratct)":{"score":10235,"total":17558}},"score":56291,"total":105348,"Addition":{"score":15414,"Addition with Carry (Abstract)":{"score":15414,"total":17558},"total":17558},"Money":{"score":10103,"total":17558,"Word Problem - Measurements - Money":{"score":10103,"total":17558}},"Division":{"score":14304,"Division - word problem":{"score":6197,"total":17558},"total":35116,"Long Division without Reminder":{"score":8107,"total":17558}}},"Number Sense":{"Numbers":{"score":14567,"Oral number name association":{"score":14567,"total":17558},"total":17558},"score":55020,"Sequence":{"total":17558,"Arranging in Ascending or Descending order":{"score":6800,"total":17558},"score":6800},"Decimals":{"total":17558,"Relate Fractions to Decimal numbers and vice versa":{"score":9800,"total":17558},"score":9800},"Multiplication":{"score":6908,"total":17558,"Long Multiplication (Abstract)":{"score":6908,"total":17558}},"Number patterns":{"score":8029,"total":17558,"Number patterns with logic":{"score":8029,"total":17558}},"total":105348,"Fractions":{"score":8916,"Part of a whole object (2D shapes) - Fractions":{"score":8916,"total":17558},"total":17558}},"Measurements":{"score":3776,"Division":{"score":3776,"total":17558,"Word Problem - Measurements - Money":{"score":3776,"total":17558}},"total":17558}},"Class 4 Assessment":{"Shapes":{"score":24600,"total":51782,"Patterns in shapes":{"score":3488,"total":17261,"Observes and extends patterns in sequence of shapes":{"score":3488,"total":17261}},"Mensuration":{"Mesuration (Area, perimeter, circumference, radius, diameter etc)":{"score":8744,"total":17260},"total":17260,"score":8744},"Flat shapes":{"2D shapes attributes":{"score":12368,"total":17261},"score":12368,"total":17261}},"Number Operations":{"Multiplication":{"score":5285,"total":17262,"Long Multiplication (Abstract)":{"score":5285,"total":17262}},"Subtraction":{"score":9018,"total":17263,"Subtraction with Borrow (Abstratct)":{"score":9018,"total":17263}},"score":46701,"total":86310,"Addition":{"score":14594,"Addition with Carry (Abstract)":{"score":14594,"total":17263},"total":17263},"Money":{"score":8949,"total":17261,"Word Problem - Measurements - Money":{"score":8949,"total":17261}},"Division":{"score":8855,"Long Division without Reminder":{"score":8855,"total":17261},"total":17261}},"Number Sense":{"total":51789,"Numbers":{"score":14345,"Oral number name association":{"score":14345,"total":17263},"total":17263},"Multiplication":{"score":6693,"total":17263,"Long Multiplication (Abstract)":{"score":6693,"total":17263}},"score":31110,"Sequence":{"total":17263,"Arranging in Ascending or Descending order":{"score":10072,"total":17263},"score":10072}},"Measurements":{"score":9424,"Division":{"score":4752,"total":17261,"Word Problem - Measurements - Money":{"score":4752,"total":17261}},"total":34522,"Length":{"Word Problem - Measurements - Four Arithmetic operations on Length":{"score":4672,"total":17261},"total":17261,"score":4672}}}}
                    var chartData = {};
                    for(var i = 4; i <= 6; i++) {
                        chartData['class' + i] = {
                            labels: _.keys(performanceResult['Class ' + i +' Assessment']),
                            series: [_.map(performanceResult['Class ' + i +' Assessment'], function(r, index){
                                return Math.round((r.score / r.total) * 100);
                            })]
                        };
                    }

                    // Rendering the all the graphs
                    renderBarChart('#gp-performance-class-4', chartData.class4);
                    renderBarChart('#gp-performance-class-5', chartData.class5);
                    renderBarChart('#gp-performance-class-6', chartData.class6);

                    // Stoping all spinners
                    $("#gp-performance-class-4").stopLoading();
                    $("#gp-performance-class-5").stopLoading();
                    $("#gp-performance-class-6").stopLoading();

                    // concepts graph listeners
                    $('#gp-performance-class-4').click(function(conceptEvent) {
                        var clickedConceptValue = conceptEvent.target.getAttribute('ct:value');
                        handleConcepts(clickedConceptValue, chartData, performanceResult, '4');
                    });
                    $('#gp-performance-class-5').click(function(value) {
                        var clickedConceptValue = value.target.getAttribute('ct:value');
                        handleConcepts(clickedConceptValue, chartData, performanceResult, '5');
                    });
                    $('#gp-performance-class-6').click(function(value) {
                        var clickedConceptValue = value.target.getAttribute('ct:value');
                        handleConcepts(clickedConceptValue, chartData, performanceResult, '6');
                    });
               // });
            } /* if else ends */
        }

        // Calling all functions
        hideSearchFields();
        showDefaultFilters();
        renderYearsTabs();
        selectYearTab(selectedConverageTab);
        renderPerformanceTabs();
        selectPerformanceTab(selectedPerformanceTab);
        renderComaprisonTabs();
        selectComparisonTab(selectedComparisonTab);

        // Start filling the default views/tabs
        loadCoverage();
        // loadPerformance();

        // listeners for checkboxes
        $educational_hierarchy_checkbox.on("change", function(value) {
            searchByGPs = false;
            $gp_checkbox.prop("checked", false);

            hideSearchFields();
        })

        $gp_checkbox.on("change", function(value) {
            searchByGPs = true;
            $educational_hierarchy_checkbox.prop("checked", false)

            hideSearchFields();
        })

        // Coverage tabs listener
        _.forEach(tabs, function(tab) {
            var $tabId = $(`#${tab.value}`);
            $tabId.on("click", function(e) {
                selectedConverageTab = e.target.dataset.value;
                selectYearTab(selectedConverageTab);
                loadCoverage();
            });
        })

        // Performance tabs listener
        _.forEach(performanceTabs, function(tab) {
            var $tabId = $(`#${tab.value}`);
            $tabId.on("click", function(e) {
                selectedPerformanceTab = e.target.dataset.value;
                selectPerformanceTab(selectedPerformanceTab);

                // removing if user has opened the details graph
                resetDetailsGraph(tab.value);

                // Loading performance
                loadPerformance();
            })
        })

        // Comparison tab listener
        _.forEach(comparisonTabs, function(tab) {
            var $tabId = $(`#${tab.value}`);
            $tabId.on("click", function(e) {
                selectedComparisonTab = e.target.dataset.value;
                selectComparisonTab(selectedComparisonTab);
            })
        })

        // Charts renderers
        function renderBarChart(elementId, data, yTitle=' ') {
            var options = {
                seriesBarDistance: 10,
                axisX: {
                    showGrid: true,
                    offset: 80
                },
                axisY: {
                    showGrid: true,
                    // offset: 80
                },
                position: 'start',
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
                        if (value.length > klp.GKA.GRAP_LABEL_MAX_CHAR) {
                        return value.slice(0, klp.GKA.GRAP_LABEL_MAX_CHAR) + '..'
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

    }

    /* Helper function */
    $.fn.startLoading = function() {
        var $this = $(this);
        var $loading = $('<div />').addClass('fa fa-cog fa-spin loading-icon-base js-loading');
        $this.empty().append($loading);
    }

    $.fn.stopLoading = function() {
        var $this = $(this);
        $this.find('.js-loading').remove();
    }

    function getDefaultAcademicYear() {
        var currentDate = new Date();
        var currentYear = currentDate.getFullYear();
        return {
            from: currentYear + '-06-01',
            to: (currentYear + 1) + '-04-30',
        }
    }
})()


