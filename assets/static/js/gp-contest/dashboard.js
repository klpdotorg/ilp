'use strict';
console.log('Coming here');

(function() {
  klp.init = function() {
    let searchByGPs = false;
    const $educational_hierarchy_checkbox = $("#select-educational-hrc");
    const $gp_checkbox = $("#select-gp-checkbox");
    const $select_school_cont = $("#select-school-cont");
    const $select_cluster_cont = $("#select-cluster-cont");
    const $select_gp_cont = $("#select-gp-cont");

    // Initialize accordion, filters and router
    console.log(klp);
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

    hideSearchFields();
    showDefaultFilters();
  }
})()


