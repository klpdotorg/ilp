update assessments_question set key ='Area of Shapes' where id in (544,545,543,546);
update assessments_question set key='Decimals' where id in (437);
update assessments_question set key='Fractions' where id in (343);
update assessments_question set key='Word Problems' where id in (346,339,538);

update assessments_question set lang_options='{ବର୍ଗାକୃତି,ପ୍ଳେଟ୍
ସଂଖ୍ୟା ରେଖା ଓ ପୋଷାକ କ୍ଲିପ୍‍,ଆବାକସ୍‍,ଦଶ ଆଧାର ବ୍ଲକ୍‍
 ଓ ସ୍ଥାନୀୟମାନ ମ୍ୟାଟ୍,
ସ୍ଥାନୀୟମାନ ପଟି
,ଭଗ୍ନାଂଶ ଆକୃତି,ଭଗ୍ନାଂଶ ପଟି,ଦଶମିକ ସେଟ୍,
ଦଶମିକ ସଂଖ୍ୟାର ସ୍ଥାନୀୟମାନ ପଟି,ଲୁଡୁ ଗୋଟି,ମାପ ଫିତା,ଜିଓ ବୋର୍ଡ଼,ଘଣ୍ଟା ଓ କୋଣ ମାପକ ଯନ୍ତ୍ର,ତରାଜୁ,ଘନବସ୍ତୁ ଢାଙ୍କୁଣୀ ସହିତ,
ଖେଳଣା ନୋଟ୍,ଟାନ୍ଗ୍ରାମ୍‍,ଗଣିତ ଧାରଣା କାର୍ଡ଼}' where id in (578,579);

update assessments_answergroup_institution set institution_id=20167 where id in (655101,655102,655103,659847,659848,659849);
