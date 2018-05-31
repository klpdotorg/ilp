from .reports import GPMathContestReport, SchoolReport, ClusterReport, BlockReport
reportlist = {"GPMathContestReport": GPMathContestReport,
              "SchoolReport":SchoolReport,
              "ClusterReport":ClusterReport,
              "BlockReport":BlockReport}
param_ids = { "GPMathContestReport": "gp_name",
              "SchoolReport":"school_code",
              "ClusterReport":"cluster_name",
              "BlockReport":"block_name"}
