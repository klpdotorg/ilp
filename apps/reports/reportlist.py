from .reports import GPMathContestReport, SchoolReport, ClusterReport, BlockReport, DistrictReport, GPMathContestReportSummarized, SchoolReportSummarized, ClusterReportSummarized, BlockReportSummarized, DistrictReportSummarized
reportlist = {"GPMathContestReport": GPMathContestReport,
              "SchoolReport":SchoolReport,
              "ClusterReport":ClusterReport,
              "BlockReport":BlockReport,
              "DistrictReport":DistrictReport,
              "GPMathContestReportSummarized":GPMathContestReportSummarized,
              "SchoolReportSummarized":SchoolReportSummarized,
              "ClusterReportSummarized":ClusterReportSummarized,
              "BlockReportSummarized":BlockReportSummarized,
              "DistrictReportSummarized":DistrictReportSummarized,
}
param_ids = { "GPMathContestReport": "gp_name",
              "SchoolReport":"school_code",
              "ClusterReport":"cluster_name",
              "BlockReport":"block_name",
              "DistrictReport":"district_name"
}
