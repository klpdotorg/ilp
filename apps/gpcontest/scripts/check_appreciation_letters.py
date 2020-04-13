import pandas as pd
from gpcontest.reports.boundary_details import *
from gpcontest.models import BoundaryCountsAgg, GPSchoolParticipationCounts

def run():
    # Read the Excel file
    # field_numbers = pd.read_excel('filepath', sheet_name="Sheet1")
    # districts = [415, 417, 418, 419, 420, 421, 424, 425, 430, 433, 437, 439, 441]
    districts = BoundaryCountsAgg.objects.filter(
        boundary_id__parent_id=2).filter(
            yearmonth__gte=201906).filter(yearmonth__lte=202005).filter(
                boundary_id__boundary_type_id='SD').values_list(
                    'boundary_id', flat=True)
    print(districts)
    blocks = BoundaryCountsAgg.objects.filter(
            yearmonth__gte=201906).filter(
                yearmonth__lte=202005).filter(
                    boundary_id__parent_id__in=districts).filter(
                        boundary_id__boundary_type_id='SB').values_list(
                            'boundary_id', flat=True)
    print(blocks)
    gps = GPSchoolParticipationCounts.objects.values_list('gp_id', flat=True)
    df_columns = ["id", "boundary_name", "boundary_type", "num_blocks", "num_gps", "num_schools", "num_children"]
    df = pd.DataFrame(columns=df_columns)
    write_once = False
    for district in districts:
        print("District %s" % district)
        district_dict = get_details(2, int(district),'SD', 201906, 202005)
        if not write_once:
            row = ["NA", district_dict["state"]["state_name"], "State", \
                    "NA", "NA",
                        district_dict["state"]["num_schools"], \
                            district_dict["state"]["num_students"]]
            df.loc[df.index.max() + 1] = row
            write_once = True
        if district_dict and district_dict["district"]:
            row = [district, district_dict["district"]["boundary_name"],"SD", district_dict["district"]["num_blocks"], \
                district_dict["district"]["num_gps"], district_dict["district"]["num_schools"], \
                    district_dict["district"]["num_students"]]
            df.loc[len(df.index) + 1] = row
        print(len(df.index))
    df.to_csv("appreciationletters_district_counts.csv")

    df_columns = ["block_id","block_name", "district_name", "num_gps", "num_schools", "num_children"]
    blocks_df = pd.DataFrame(columns=df_columns)
    for block in blocks:
        block_dict = get_details(2, int(block), 'SB', 201906, 202005)
        if block_dict and block_dict["block"]:
            row = [block, block_dict["block"]["boundary_name"], block_dict["block"]["parent_boundary_name"], block_dict["block"]["num_gps"], block_dict["block"]["num_schools"], \
                block_dict["block"]["num_students"]]
            blocks_df.loc[len(blocks_df.index) + 1] = row
            print(len(blocks_df.index))
    blocks_df.to_csv("appreciationletters_block_counts.csv")

    #Write GP numbers
    df_columns = ["gp_id", "gp_name", "district_name", "block_name", "num_schools", "num_children"]
    gps_df = pd.DataFrame(columns=df_columns)
    print("No of GPs is %s" % len(gps))
    for gp in gps:
        gp_dict = get_details(2, int(gp), 'GP', 201906, 202005)
        if gp_dict:
            row = [gp, gp_dict["gp"]["name"], gp_dict["gp"]["district_name"],gp_dict["gp"]["block_name"], gp_dict["gp"]["num_schools"], \
                gp_dict["gp"]["num_students"]]
            gps_df.loc[len(gps_df.index) + 1] = row
    gps_df.to_csv("appreciationletters_gp_counts.csv")
