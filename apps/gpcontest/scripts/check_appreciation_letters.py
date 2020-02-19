import pandas as pd
from gpcontest.reports.boundary_details import *
from gpcontest.models import BoundaryCountsAgg

# Read the Excel file
# field_numbers = pd.read_excel('filepath', sheet_name="Sheet1")
# districts = [415, 417, 418, 419, 420, 421, 424, 425, 430, 433, 437, 439, 441]
districts = BoundaryCountsAgg.objects.filter(boundary_id__parent_id=2).filter(boundary_id__boundary_type_id='SD').values_list('boundary_id', flat=True)
blocks = BoundaryCountsAgg.objects.filter(boundary_id__parent_id=415).filter(boundary_id__boundary_type_id='SB').values_list('boundary_id', flat=True)
df_columns = ["district_name", "num_blocks", "num_gps", "num_schools", "num_children"]
df = pd.DataFrame(columns=df_columns)
for district in districts:
    district_dict = get_details(2, int(district),'SD',
                    201906, 202005)
    row = [district, district_dict["district"]["num_blocks"], \
        district_dict["district"]["num_gps"], district_dict["district"]["num_schools"], \
            district_dict["district"]["num_students"]]
    df.loc[df.index.max()+1] = row
df.to_csv("district_counts.csv")    

 
