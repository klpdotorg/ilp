import pandas as pd
from gpcontest.reports.boundary_details import *
from gpcontest.models import BoundaryCountsAgg, GPSchoolParticipationCounts

# Read the Excel file
# field_numbers = pd.read_excel('filepath', sheet_name="Sheet1")
# districts = [415, 417, 418, 419, 420, 421, 424, 425, 430, 433, 437, 439, 441]
districts = BoundaryCountsAgg.objects.filter(boundary_id__parent_id=2).filter(boundary_id__boundary_type_id='SD').values_list('boundary_id', flat=True)
blocks = BoundaryCountsAgg.objects.filter(boundary_id__parent_id_in=districts).filter(boundary_id__boundary_type_id='SB').values_list('boundary_id', flat=True)
gps = gp_school_counts = GPSchoolParticipationCounts.objects.values_list('gp_id', flat=True)
df_columns = ["district_name", "boundary_type", "num_blocks", "num_gps", "num_schools", "num_children"]
df = pd.DataFrame(columns=df_columns)
write_once = False
for district in districts:
    district_dict = get_details(2, int(district),'SD',
                    201906, 202005)
    if not write_once:
        row = [district_dict["state"]["state_name"], "State", \
                district_dict["state"]["num_blocks"], \
                    district_dict["state"]["num_schools"], \
                        district_dict["state"]["num_children"]]
        df.loc[df.index.max() + 1] = row
        write_once = True
    row = [district, "SD", district_dict["district"]["num_blocks"], \
        district_dict["district"]["num_gps"], district_dict["district"]["num_schools"], \
            district_dict["district"]["num_students"]]
    df.loc[df.index.max()+1] = row
df.to_csv("appreciationletters_district_counts.csv")

df_columns = ["block_name", "district_name", "num_blocks", "num_gps", "num_schools", "num_children"]
blocks_df = pd.DataFrame(columns=df_columns)
for block in blocks:
    block_dict = get_details(2,int(block), 'SB', 201906, 202005)
    row = [block, block_dict["block"]["parent_boundary_name"], block_dict["block"]["num_gps"], block_dict["block"]["num_schools"], \
        block_dict["block"]["num_students"]]
    blocks_df.loc[df.index.max() + 1] = row
blocks_df.to_csv("appreciationletters_block_counts.csv")

#Write GP numbers
df_columns = ["gp_name", "block_name", "district_name", "num_schools", "num_children"]
gps_df = pd.DataFrame(columns=df_columns)
for gp in gps:
    gp_dict = get_details(2,int(gp), 'GP', 201906, 202005)
    row = [gp, gp_dict["gp"]["name"], gp_dict["gp"]["district_name"],gp_dict["gp"]["block_name"], gp_dict["gp"]["num_schools"], \
        gp_dict["gp"]["num_students"]]
    gps_df.loc[df.index.max() + 1] = row
gps_df.to_csv("appreciationletters_gp_counts.csv")
