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

	$('#divyear').hide()

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
		$('#divyear').show()
		//$('#start').addClass("chart-full-item").removeClass("chart-half-item")
		//document.getElementById("startlabel").innerHTML = "Select Year";
	    }
	    if(radioValue == 'summarycounts')
	    {
		$('#divyear').hide()
	    }

        });


        $('#search_button').click(function(e){
            $('#chartArea').empty();
            $('#chartLabel').empty();

            var district_id = $("#selectdistrict").val(),
                block_id = $("#selectblock").val(),
                cluster_id = $("#selectcluster").val(),
                institution_id = $("#selectschool").val(),
                year = $('#year').val(),
                graphtype = $("input[name='graphtype']:checked").val(),
                url = 'backoffice/analysis/';

                //if(start_year && end_year) {
                  //  url += '?startyear=' + start_year + '&endyear=' + end_year;
                //} else {
                    // url += 'default_date=true';
                //}
		if(graphtype)
		{
			url += '?graph_type='+graphtype
		}
		if(year)
		{
			url += '&year='+year
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

            var $search = klp.api.do(url);
            $search.done(function(data) {
                if(data.status == '')
		{
		    loadCharts(data)
                }
		else
		{
                    showError(data.status)
		}
            })
        });
        loadData(premodalQueryParams);
    }

    function createtab(tab, tabcount)
    {
        var tabbutton = document.createElement("button");            
	tabbutton.setAttribute('id','button'+tabcount);
	tabbutton.setAttribute('type',"button");
	tabbutton.setAttribute('class',"btn btn-info full-width");
	tabbutton.setAttribute('data-toggle',"collapse");
	tabbutton.innerHTML = tab;
	var tabdiv = document.createElement("div");
	tabdiv.setAttribute('id','tabdiv'+tabcount);
	tabdiv.setAttribute('class','collapse');
	var targetdiv = '#tabdiv'+tabcount
	tabbutton.setAttribute('data-target',targetdiv);
	return [tabbutton, tabdiv];

    }

    function createGraphs(tabtitle, chart, index, tabcount, graphcount, imagedata)
    {
 	var chartdiv = document.createElement("div");
	chartdiv.setAttribute('id','figimg'+"_"+tabcount+"_"+graphcount);
	chartdiv.setAttribute('class','box');
        var labeldiv = document.createElement("div");
	var labelid = 'figlabel'+"_"+tabcount+"_"+graphcount;
	labeldiv.setAttribute('id',labelid);
	chartdiv.appendChild(labeldiv);
	labeldiv.innerHTML = tabtitle;
	var img = imagedata["data"][index];
	$('#'+labelid).addClass("heading-secondary")
        var imgdiv = document.createElement("img");
	imgdiv.setAttribute('src',"data:image/png;base64,"+img)
	chartdiv.appendChild(imgdiv);
	return chartdiv;
    }

    function loadCharts(retdata)
    {
        document.getElementById("chartLabel").innerHTML = retdata["charttype"];
	$('#chartLabel').addClass("heading-primary")
	var tabs = retdata["tabs"];
	var order = retdata["order"];
	var graphs = retdata["names"];
	var chartArea = document.getElementById("chartArea");
	var tabcount = 1;
	for(var tab in tabs)
        {
	    const [tabbutton, tabdiv] = createtab(tab, tabcount);
    	    chartArea.appendChild(tabbutton);
	    chartArea.appendChild(tabdiv);
	    chartArea.appendChild(document.createElement("br"));
	    chartArea.appendChild(document.createElement("br"));
            for(var order in tabs[tab])
	    {
                var graphcount = 1;
                var tabtitle = tabs[tab][order];
		var chart = tab+tabtitle;
		var index = retdata["order"][chart];
		var chartdiv = createGraphs(tabtitle, chart, index, tabcount, graphcount, retdata);
	        tabdiv.appendChild(chartdiv);
	        graphcount +=1 ;
		chartdiv.appendChild(document.createElement("br"));

	    }
	    tabcount+=1 ;
        }
    }

    function showError(error)
    {
        $('#chartLabel').innerHTML = error;
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
                window.location.href = '/backoffice';
            }
            //This is to prevent server calls when just the modal actions are called
            //This condition is triggered for eg: for localhost:8001/gka#datemodal?from=12/03/2016&to12/06/2016
            //and not for just localhost:8001/gka#datemodal
            else if(window.location.hash != '#datemodal' && window.location.hash !='#close' && window.location.hash != '#analysis')
            {
                loadData(queryParams, true);
            }
            //This is the do nothing case switch for localhost:8001/gka#datemodal
            else {//do nothing;
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

