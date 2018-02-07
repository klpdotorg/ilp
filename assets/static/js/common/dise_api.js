(function() {
    var base = window.klp.DISE_BASE_URL;//'https://dise.dev.ilp.org.in/api/';
    var DEFAULT_ACADEMIC_YEAR = window.klp.DEFAULT_ACADEMIC_YEAR;//'16-17';
    klp.dise_api = {
        'fetchSchoolInfra': function(diseCode, academicYear) {
            if (typeof(academicYear) === 'undefined') {
                academicYear = DEFAULT_ACADEMIC_YEAR;
            }
            if (!diseCode) {
                var $deferred = $.Deferred();
                //FIXME: Return a proper error, dont resolve with empty object
                setTimeout(function() {
                    $deferred.resolve({});
                }, 0);
                return $deferred;
            }
            var url = base + academicYear + '/school/' + diseCode + '/infrastructure/';
            var params = {
                'format': 'json'
            };
            var $xhr = $.get(url, params);
            return $xhr;
        },

        'queryBoundaryName': function(boundaryName,boundaryType, academicYear) {
            var url = base + academicYear + '/search/';
            //Map the "new" ILP boundary types to the ones the DISE app is expecting
            diseBoundType = ""
            if(boundaryType == 'SD')
                diseBoundType = "district"
            else if(boundaryType == "SB")
                diseBoundType = "block"
            else if(boundaryType == "SC")
                diseBoundType = "cluster"
            var params = {
                'query': boundaryName,
                'type': diseBoundType
            };
            var $xhr = $.get(url, params);
            return $xhr;
        },

        'getBoundaryData': function(boundaryID, boundaryType, academicYear) {
            var url = base + academicYear + '/' + boundaryType + '/' + boundaryID + '/';
            var $xhr = $.get(url);
            return $xhr;
        },

        'getMultipleBoundaryData': function(parentBoundaryName, parentBoundaryType, boundaryType, academicYear){
            var url;
            if (parentBoundaryName == null)
                url = base + academicYear + '/' + boundaryType;
            else
                url = base + academicYear + '/' + parentBoundaryType + '/' +parentBoundaryName + '/' +boundaryType+'s/?basic=no';
            var $xhr = $.get(url);
            return $xhr;
        },

        'getElectedRepData': function(electedrepID, electedrepType, academicYear) {
            var url = base + academicYear + '/' + electedrepType + '/' + electedrepID + '/';
            var $xhr = $.get(url);
            return $xhr;
        }


    };

})();
