'use strict';

(function() {
  klp.init = function() {
    let searchByGPs = false;
    let selectedConverageTab = '2016';
    let selectedPerformanceTab = 'basic';
    let selectedComparisonTab = 'year';
    const years = ["2016", "2017", "2018"];
    const performanceTabs = [
      {
        text: 'Basic',
        value: 'basic',
      },
      {
        text: 'Details',
        value: 'details',
      }
    ];
    const comparisonTabs = [
      {
        text: 'Year',
        value: 'year'
      },
      {
        text: 'Neighbour',
        value: 'neighbour',
      }
    ];
    const tabs = years.map((tab) => {
      return {
        value: tab,
        start_date: `${tab}-01-01`,
        end_date: `${Number(tab) + 1}-01-01`
      }
    })
    const $educational_hierarchy_checkbox = $("#select-educational-hrc");
    const $gp_checkbox = $("#select-gp-checkbox");
    const $select_school_cont = $("#select-school-cont");
    const $select_cluster_cont = $("#select-cluster-cont");
    const $select_gp_cont = $("#select-gp-cont");

    // Initialize accordion, filters and router
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
      if(window.location.hash) {
        if(window.location.hash == '#resetButton') {
          window.location.href = '/gp-contest';
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
      var yearTabHTML = tplYearTab({ tabs: tabs.map((tab) => ({ text: tab.value, value: tab.value })) });
       
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
      const $currentTab = $(`#${tab.value}`);
      if (tab.value === goingToSelectTab) {
        $currentTab.addClass("selected-gp-tab");
      } else {
        $currentTab.removeClass("selected-gp-tab");
      }
    }

    // This function select the tab
    function selectYearTab(goingToSelectTab) {
      tabs.forEach((tab) => {
        selectTab(tab, goingToSelectTab);
      })
    }

    // This function select the performance tab
    function selectPerformanceTab(goingToSelectTab) {
      performanceTabs.forEach((tab) => {
        selectTab(tab, goingToSelectTab);
      })
    }

    // This function select the Comparison Tab
    function selectComparisonTab(goingToSelectTab) {
      comparisonTabs.forEach((tab) => {
        selectTab(tab, goingToSelectTab);
      })
    }

    // Fetch coverage information
    function loadCoverage() {
      const selectedYearInfo = tabs.find((tab) => {
        return tab.value === selectedConverageTab;
      });

      var $coverageXHR = klp.api.do(
         `survey/summary/?survey_id=2&from=${selectedYearInfo.start_date}&${selectedYearInfo.end_date}&state=ka`
      )

      $coverageXHR.done(function(result) {
        var tplCoverage = swig.compile($('#tpl-coverage').html());
        var coverageHTML = tplCoverage({ data: result.summary });
        
        $('#gp-coverage').html(coverageHTML);
      });
    }

    // Fetch performance info
    function loadPerformance() {
      const selectedYearInfo = tabs.find((tab) => {
        return tab.value === selectedConverageTab;
      });

      var $performanceXHR = klp.api.do(
         `survey/detail/questiongroup/key/?survey_id=2&from=${selectedYearInfo.start_date}&${selectedYearInfo.end_date}`
      );
      $performanceXHR.done(function(result) {
        var chartData = {};
        for(var i = 4; i <= 6; i++) {
          chartData['class' + i] = {
            labels: _.keys(result['Class ' + i +' Assessment']),
            series: [_.map(result['Class ' + i +' Assessment'], function(r){
              return Math.round((r.score / r.total) * 100);
            })]
          };
        }

        console.log(chartData);
        renderBarChart('#gp-performance-class-4', chartData.class4);
        renderBarChart('#gp-performance-class-5', chartData.class5);
        renderBarChart('#gp-performance-class-6', chartData.class6);
      });
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
    loadPerformance();

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
    tabs.forEach((tab) => {
      const $tabId = $(`#${tab.value}`);
      $tabId.on("click", function(e) {
        selectedConverageTab = e.target.dataset.value;
        selectYearTab(selectedConverageTab);
        loadCoverage();
      });
    })

    // Performance tabs listener
    performanceTabs.forEach((tab) => {
      const $tabId = $(`#${tab.value}`);
      $tabId.on("click", function(e) {
        selectedPerformanceTab = e.target.dataset.value;
        selectPerformanceTab(selectedPerformanceTab);
        loadPerformance();
      })
    })

    // Comparison tab listener
    comparisonTabs.forEach((tab) => {
      const $tabId = $(`#${tab.value}`);
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
})()


