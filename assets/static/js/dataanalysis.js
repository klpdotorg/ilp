/* vi:si:et:sw=4:sts=4:ts=4 */
'use strict';

(function() {
    var premodalQueryParams = {};

    klp.init = function() {

        // Screen size adjustments
        if(screen.width >= 640) {
            $('.one-row-chart').height(400);
        } else {
            $('.one-row-chart').height(200);
        }

        // All GKA related data are stored in GKA
        klp.GKA = {};
        klp.GKA.routerParams = {};
        klp.GKA.GRAP_LABEL_MAX_CHAR = 4;

        // This function is used as a callback to accordion init function
        // to determine which section to load when a user clicks a
        // section
        klp.GKA.accordionClicked = function($el) {
            var isSectionVisible = $el.is(':visible'),
                elId = $el.attr('id'),
                functionMap = {
                    sms: loadSmsData,
                    // assessment: loadAssmtData, We don't need assessment section as of 30th Oct 2018
                    gpcontest: loadGPContestData,
                    surveys: loadSurveys,
                    comparison: loadComparison,
                    dummy: loadDummy
                };

            if(!isSectionVisible) { return; }

            if(typeof(functionMap[elId]) === 'function') {
                functionMap[elId](klp.GKA.routerParams);
            } else {
                console.log('Accordion event handler returned an unknow id');
            }
        }

        // Initialize accordion, filters and router
        klp.accordion.init();
        klp.router = new KLPRouter();
        klp.router.init();
        klp.router.events.on('hashchange', function(event, params) {
            hashChanged(params);
        });
        klp.router.start();
        premodalQueryParams = klp.router.getHash().queryParams;

        klp.boundary_filters.init();

        var $graphtype = $("#graphtype");
        $graphtype.on("click", function() {
	    var radioValue = $("input[name='graphtype']:checked").val();

	    if(radioValue == 'corelation')
	    {
		$('#endyear').hide()
		$('#start').addClass("chart-full-item").removeClass("chart-half-item")
	    }

        });


        $('#search_button').click(function(e){
            var district_id = $("#selectdistrict").val(),
                block_id = $("#selectblock").val(),
                cluster_id = $("#selectcluster").val(),
                institution_id = $("#selectschool").val(),
                start_year = $('#startyear').val(),
                end_year = $('#endyear').val(),
                graphtype = $("input[name='graphtype']:checked").val(),
                url = '/backoffice/analysis/';
		url += graphtype+"/";

                //if(start_year && end_year) {
                  //  url += '?startyear=' + start_year + '&endyear=' + end_year;
                //} else {
                    // url += 'default_date=true';
                //}
		if(start_year)
		{
			url += '?year='+start_year
		}

                if(institution_id) {
                    url += '&institution_id=' + institution_id;
                } else {
                    if(cluster_id) {
                        url += '&boundary_id=' + cluster_id;
                    } else if(block_id) {
                        url += '&boundary_id=' + block_id;
                    } else if(district_id) {
                        url += '&boundary_id=' + district_id;
                    }
                }

                e.originalEvent.currentTarget.href = url;

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
                window.location.href = '/dataanalysis/search';
            }
        }
        $('#ReportContainer').show();
    }

    function loadData(params, reloadOpenSection) {

        klp.GKA.routerParams = params;

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

    $(document).ready(function() {
        if (klp.hasOwnProperty('init')) {
            klp.init();
        }
    });


})();

