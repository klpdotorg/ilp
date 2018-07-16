(function() {
    klp.init = function() {
        //handle getting partners from the server
        var partnersURL = 'surveys/partners/';
        var partners = klp.api.do(partnersURL)
        partners.done(function(data) {
            console.log("Results:--" , data.results)
            var tpl = swig.compile($('#tpl-primary-partners').html());
            var html = tpl({
                'partners' : data.results
            });
            $('#partner-info-wrapper').html(html);
            console.log("Fetched partners", html)

        });

       
        //get and show SYS info
        // var url = "stories/info/";
        // var url = "surveys/storiesinfo/";
        // var sysCountsXHR = klp.api.do(url);
        // var tplSysCounts = swig.compile($('#tpl-sysCounts').html());
        // sysCountsXHR.done(function(data) {
        //     var html = tplSysCounts(data);
        //     $('#sysCounts').html(html);
        // });

        // //get and show recent stories
        // var url = "surveys/shared-assessments";
        // var params = {
        //     per_page: 6,
        //     verified: 'yes'
        // };
        // var sysXHR = klp.api.do(url, params);
        // var tplSys = swig.compile($('#tpl-sysInfo').html());
        // sysXHR.done(function(data) {
        //     var context = {
        //         'stories': data.institutions
        //     };
        //     console.log("Stories is: ", context)
        //     var html = tplSys(context);
        //     $('#sysInfo').html(html);
        // });

    };
})();