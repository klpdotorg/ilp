'use strict';

(function() {
  klp.init = function() {
    let searchByGPs = false;
    let selectedTab = '2016';
    const years = ["2016", "2017", "2018"];
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

    $('#startDate').yearMonthSelect("init", {validYears: ['2016', '2017', '2018', '2019']});
    $('#endDate').yearMonthSelect("init", {validYears: ['2016', '2017', '2018', '2019']});
    $('#startDate').yearMonthSelect("setDate", moment("20180601", "YYYYMMDD"));
    $('#endDate').yearMonthSelect("setDate", moment("20190331", "YYYYMMDD"));

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

    // This function renders tabs
    function renderYearsTabs() {
      var tplYearTab = swig.compile($('#tpl-year-tabs').html());
      var yearTabHTML = tplYearTab({ tabs: tabs });
       
      $('#year-tabs').html(yearTabHTML);
    }

    // This function select the tab
    function selectYearTab(year) {
      tabs.forEach((tab) => {
        const $currentTab = $(`#${tab.value}-year`);
        if (tab.value === year) {
          $currentTab.addClass("selected-gp-tab");
        } else {
          $currentTab.removeClass("selected-gp-tab");
        }
      })
    }

    // Fetch coverage information
    function loadCoverage() {
      const selectedYearInfo = tabs.find((tab) => {
        return tab.value === selectedTab;
      });
      console.log(selectedYearInfo, 'Printing the selectedYearInfo');

      var $coverageXHR = klp.api.do(
         `survey/summary/?survey_id=2&from=${selectedYearInfo.start_date}&${selectedYearInfo.end_date}&state=ka`
      )

      $coverageXHR.done(function(result) {
        console.log(result);
        var tplCoverage = swig.compile($('#tpl-coverage').html());
        var coverageHTML = tplCoverage({ data: result.summary });
        
        $('#gp-coverage').html(coverageHTML);
      });
    }
    // Calling all functions
    hideSearchFields();
    showDefaultFilters();
    renderYearsTabs();
    selectYearTab(selectedTab);
    loadCoverage();

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

    // Button year listener
    tabs.forEach((tab) => {
      const $tabYearId = $(`#${tab.value}-year`);
      $tabYearId.on("click", function(e) {
        const selectedYear = e.target.dataset.value;
        selectedTab = selectedYear;
        selectYearTab(tab.value);
        loadCoverage();
      });
    })

  }
})()


