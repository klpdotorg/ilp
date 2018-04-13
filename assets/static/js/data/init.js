'use strict';
(function() {
    klp.init = function() {
      klp.router = new KLPRouter();
      klp.router.init();

      function downloadKLPSchools() {
        window.open(`/media/school-data/primaryschool.csv`, '_self');
      }

      function downloadKLPPreschools() {
        window.open('/media/school-data/preschool.csv', '_self');
      }

      function downloadKLPDISESchools() {
        window.open('/media/school-data/dise-1617.csv', '_self');
      }

      $("#download-schools-button").click(function(){
        klp.auth.requireLogin(downloadKLPSchools);
      });

      $("#download-preschools-button").click(function() {
        klp.auth.requireLogin(downloadKLPPreschools);
      })

      $("#download-diseschools-button").click(function() {
        klp.auth.requireLogin(downloadKLPDISESchools);
      })
    }
})();
