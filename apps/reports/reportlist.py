from .reports import GPMathContestReport, SchoolReport, ClusterReport, BlockReport, DistrictReport
reportlist = {"GPMathContestReport": GPMathContestReport,
              "SchoolReport":SchoolReport,
              "ClusterReport":ClusterReport,
              "BlockReport":BlockReport,
              "DistrictReport":DistrictReport
}
param_ids = { "GPMathContestReport": "gp_name",
              "SchoolReport":"school_code",
              "ClusterReport":"cluster_name",
              "BlockReport":"block_name",
              "DistrictReport":"district_name"
}
