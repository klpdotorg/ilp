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
	$('#divdistrict').hide()
	$('#divblock').hide()

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

	    if(radioValue == 'corelation'|| radioValue=='actualgpvsassessed' || radioValue == 'mappedschoolvsassessed')
	    {
		$('#divyear').show();
		$('#divblock').show();
		$('#divdistrict').show();
	    }
	    if(radioValue == 'cohorts')
	    {
		$('#divyear').hide();
                $("#year").val("");
		$('#divblock').hide();
                $("#selectblock").val("");
		$('#divdistrict').hide();
                $("#selectdistrict").val("");
	    }
	    if(radioValue == 'summarycounts')
	    {
		$('#divyear').hide();
		$('#year').val("");
		$('#divblock').show();
		$('#divdistrict').show();
	    }
	    if(radioValue == 'outliers'|| radioValue=='questionperformance')
	    {
		$('#divyear').show()
		$('#divblock').hide()
		$('#selectblock').val("");
		$('#divdistrict').hide()
                $("#selectdistrict").val("");
	    }
	

        });


        $('#search_button').click(function(e){
            $('#chartArea').empty();
            $('#chartLabel').empty();

            var district_id = $("#selectdistrict").val(),
                block_id = $("#selectblock").val(),
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
		if(["corelation","actualgpvsassessed","mappedschoolvsassessed","outliers","questionperformance"].includes(graphtype))
		{
			if(! year)
			{
			    year = '2019-2020';
			}
		}
		if(year)
		{
			url += '&year='+year
		}
                if(block_id) {
                        url += '&boundary_id=' + block_id;
                } else if(district_id) {
                        url += '&boundary_id=' + district_id;
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

    function createtab(parentdiv, tab, tabcount, tabtitle, level)
    {
	parentdiv.appendChild(document.createElement("br"));
        var tabbutton = document.createElement("button");            
	tabbutton.setAttribute('id','button'+tabcount);
	tabbutton.setAttribute('type',"button");
	if(level == 0)
	{
	   tabbutton.setAttribute('class',"btn btn-info");
	   tabbutton.setAttribute('style',"background-color:DeepSkyBlue; width:100%; margin:0 auto; align-items: center; justify-content: center;text-align:center;");
	}
	else if(level == 1)
	{
	   tabbutton.setAttribute('class',"btn btn-info");
	   tabbutton.setAttribute('style',"background-color:DarkTurquoise; width:70%; margin:0 auto;text-align:center;align-items: center; justify-content: center;");
	}
	else if(level == 2)
	{
	   tabbutton.setAttribute('class',"btn btn-info");
	   tabbutton.setAttribute('style',"background-color:Plum; width:40%; margin:0 auto;text-align:center;align-items: center; justify-content: center;");
	}
        else if(level == 3)
	{
	   tabbutton.setAttribute('class',"btn btn-info");
	   tabbutton.setAttribute('style',"background-color:LightGreen; width:25%; margin:0 auto;text-align:center;align-items: center; justify-content: center;");
	}
	tabbutton.setAttribute('data-toggle',"collapse");
	tabbutton.innerHTML = tabtitle;
	var tabdiv = document.createElement("div");
	tabdiv.setAttribute('id','tabdiv'+tabcount);
	tabdiv.setAttribute('class','collapse');
	tabdiv.setAttribute('style','text-align:center;align-items: center; justify-content: center;');
	var targetdiv = '#tabdiv'+tabcount
	tabbutton.setAttribute('data-target',targetdiv);
    	parentdiv.appendChild(tabbutton);
	parentdiv.appendChild(tabdiv);
	parentdiv.appendChild(document.createElement("br"));
	return [tabbutton, tabdiv];

    }

    function createErrorDiv(errormsg)
    {
	var errorDiv = document.createElement("div");
	errorDiv.innerHTML = errormsg;
	return errorDiv
    }

    function createGraphs(tabtitle, tabcount, graphcount, image)
    {
 	var chartdiv = document.createElement("div");
	chartdiv.setAttribute('id','figimg'+"_"+tabcount+"_"+graphcount);
	chartdiv.setAttribute('class','box');
        var labeldiv = document.createElement("div");
	var labelid = 'figlabel'+"_"+tabcount+"_"+graphcount;
	labeldiv.setAttribute('id',labelid);
	chartdiv.appendChild(labeldiv);
	labeldiv.innerHTML = tabtitle;
	var img = image;
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
	var maintabs = tabs["names"];
	var subtabs = {};
	var commonsubtabpresent = false;
	var commonsubtabs = {}
	var images = retdata["data"];
	var names = retdata["names"];
	var yearid = retdata["year"].toString();
	var year_char = retdata["year_char"].toString();
	var boundaryid = retdata["boundaryid"].toString();
	if( "commonsubtabs" in tabs )
	{
	    commonsubtabpresent = true;
	    commonsubtabs = tabs["commonsubtabs"];
	}
	var subtabcount = 1;
	var graphcount = 1;
	for(var tab in maintabs)
        {
	    var tabname = maintabs[tab]["substr"];
	    var tabtitle = maintabs[tab]["title"];
	    if( ! isEmpty(retdata["boundary"]) )
            {
                tabtitle += " "+retdata["boundary"]["name"].toUpperCase();
	    }
	    if( yearid != "")
	    {
                tabtitle += " (For year: "+year_char+")";
	    }
	    const [tabbutton, tabdiv] = createtab(chartArea, tabname, tabcount, tabtitle, 0);

	    if("subtabs" in maintabs[tab])
	    {
		createsubtab(tabdiv, tabbutton, tabcount, maintabs[tab]["subtabs"],maintabs[tab]["usecommontab"], commonsubtabpresent, commonsubtabs, subtabcount,"","", images, names, yearid, boundaryid, 1);
		subtabcount += 1;
	    }
	    else if(commonsubtabpresent && maintabs[tab]["usecommontab"])
	    {
                createsubtab(tabdiv, tabbutton, tabcount, {}, true, commonsubtabpresent, commonsubtabs, subtabcount, tabtitle , tabname, images, names, yearid, boundaryid, 1);
		subtabcount += 1;
	    }
	    else
	    {
		var imagename = tabname;
		if(boundaryid != "")
		{
			imagename = imagename+"_"+boundaryid;
		}
		if(yearid != "" )
		{
			imagename = imagename+"_"+yearid;
		}
		var index = names[imagename]
		var image = images[index]
		if( image == null )
		{
		    var errorDiv = createErrorDiv("No image");
	            tabdiv.appendChild(errorDiv);
		}
		else
		{
	            var chartdiv = createGraphs(tabtitle, tabcount, graphcount, image);
	            tabdiv.appendChild(chartdiv);
	            graphcount +=1 ;
		}
	    }
	    tabcount+=1 ;
	}
    }

    function isEmpty(obj) {
	      return Object.keys(obj).length === 0;
    }


    function createsubtab(parentdiv, parentbutton, parentcount, subtabs, usecommontab, commonsubtrabpresent, commonsubtabs, subtabcount, currenttitle, currentname, images, names, yearid, boundaryid, level)
    {
	var subtabpresent = false
	if( isEmpty(subtabs) )
	{
            var subtabnames = commonsubtabs["names"];
            if ("subtabs" in commonsubtabs && usecommontab)
	    {
	        subtabpresent = true;
		var sub_subtabs = commonsubtabs["subtabs"];
	    }
	}
	else
	{
            var subtabnames = subtabs["names"];
            if ("subtabs" in subtabs)
	    {
	        subtabpresent = true;
		var sub_subtabs = subtabs["subtabs"];
	    }
	    else if( ! isEmpty(commonsubtabs) )
	    {
	        subtabpresent = true;
		var sub_subtabs = commonsubtabs;
	    }
	}
        for(var index in subtabnames)
	{
	    var graphcount = 0;
            var subtabname = subtabnames[index]["substr"];
	    var subtabtitle = subtabnames[index]["title"];
	    //if(currenttitle == "")
	    //{
	        subtabtitle = subtabtitle;
	    //}
	    //else
	    //{
	        //subtabtitle = currenttitle +" - "+ subtabtitle;
	    //}
	    subtabname = currentname + subtabname;
	    const [subtabbutton, subtabdiv] = createtab(parentdiv, subtabname, parentcount.toString()+"_"+subtabcount.toString(), subtabtitle, level);
	    subtabcount += 1;
	    if( subtabpresent == true)
	    {
                createsubtab(subtabdiv, subtabbutton, subtabcount, sub_subtabs, usecommontab, false, {}, subtabcount, subtabtitle, subtabname, images, names, yearid, boundaryid, level+1)
	    }
	    else
	    {
                var graphcount = 1;
                var tabtitle = currenttitle;
	        var tabname = currentname;
		var imagename = subtabname;
		if(boundaryid != "")
		{
			imagename = imagename+"_"+boundaryid;
		}
		if(yearid != "" )
		{
			imagename = imagename+"_"+yearid;
		}
		var index = names[imagename]
		var image = images[index]
                if( image == null )
		{
		    var errorDiv = createErrorDiv("No image");
	            subtabdiv.appendChild(errorDiv);
		}
		else
		{
	            var chartdiv = createGraphs(tabtitle, subtabcount, graphcount, image);
	            subtabdiv.appendChild(chartdiv);
	            graphcount +=1 ;
		}
	        subtabdiv.appendChild(document.createElement("br"));
		subtabtitle = currenttitle;
		subtabname = currentname;
	    }
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
                window.location.href = '/backoffice/dataanalysis';
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

