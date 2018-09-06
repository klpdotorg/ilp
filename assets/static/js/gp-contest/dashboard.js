var districtURL = generateDistrictIframeURL();
var districtBlockURL = generateDistrictBlockIframeUrl();
var districtClassURL = generateDistrictClassIframeURL();
var blockVillageURL = generateBlockVillageIframeURL();


updateDistrictIframeURL(districtURL)
updateDistrictBlockIframeURL(districtBlockURL);
updateDistrictClassIframeURL(districtClassURL);
updateBlockVillageIframeURL(blockVillageURL);

function getSelectedValues(el) {
  return Array(...el.options).reduce((acc, option) => {
    if (option.selected === true) {
      acc.push(option.value);
    }
    return acc;
  }, []);
}

function updateDistrictBlockParams(params) {
  const preselect_filters = JSON.stringify(params.preselect_filters);
  const form_data = JSON.stringify(params.form_data);

  const url = `${districtBlockParams.url}?preselect_filters=${preselect_filters}&form_data=${form_data}&standalone=${params.standalone}&height=${params.height}`;
  updateDistrictBlockIframeURL(url);
}

function updateBlockVillageParams(params) {
  const preselect_filters = JSON.stringify(params.preselect_filters);
  const form_data = JSON.stringify(params.form_data);

  const url = `${blockVillageParams.url}?preselect_filters=${preselect_filters}&form_data=${form_data}&standalone=${params.standalone}&height=${params.height}`;
  updateBlockVillageIframeURL(url);
}

function setDistrictFilter() {
  const el = document.getElementById("districtFilter");
  const values = getSelectedValues(el);
  const params1 = blockVillageParams.params;
  const params2 = districtBlockParams.params;

  params1.form_data.filters[0].val = values
  params2.form_data.filters[0].val = values
  params1.preselect_filters['1'].District = values
  params2.preselect_filters['1'].District = values

  updateDistrictBlockParams(params2);
  updateBlockVillageParams(params1);
}

function setBlockFilter() {
  const el = document.getElementById("blockFilter");
  const values = getSelectedValues(el);
  const params1 = blockVillageParams.params;
  const params2 = districtBlockParams.params;

  params1.form_data.filters[1].val = values
  params2.form_data.filters[1].val = values
  params1.preselect_filters['2'].Block = values
  params2.preselect_filters['2'].Block = values

  updateDistrictBlockParams(params2);
  updateBlockVillageParams(params1);
}

function setVillageFilter() {
  const el = document.getElementById("villageFilter");
  const values = getSelectedValues(el);
  const params1 = blockVillageParams.params;
  const params2 = districtBlockParams.params;

  params1.form_data.filters[2].val = values
  params2.form_data.filters[2].val = values

  updateDistrictBlockParams(params2);
  updateBlockVillageParams(params1);
}

// This function generate the iframe url for district block graph.
function generateDistrictBlockIframeUrl() {
  const params = districtBlockParams.params;
  const preselect_filters = JSON.stringify(params.preselect_filters);
  const form_data = JSON.stringify(params.form_data);

  return `${districtBlockParams.url}?preselect_filters=${preselect_filters}&form_data=${form_data}&standalone=${params.standalone}&height=${params.height}`;
}

// This function generate the iframe url for district graph.
function generateDistrictIframeURL() {
  const params = districtParams.params;
  const form_data = JSON.stringify(params.form_data);

  return `${districtParams.url}?form_data=${form_data}&standalone=${params.standalone}&height=${params.height}`;
}

// This function generate the iframe url for district class graph.
function generateDistrictClassIframeURL() {
  const params = districtClassParams.params;
  const form_data = JSON.stringify(params.form_data);

  return `${districtClassParams.url}?form_data=${form_data}&standalone=${params.standalone}&height=${params.height}`;
}

// This function generate the iframe url for block village graph.
function generateBlockVillageIframeURL() {
  const params = blockVillageParams.params;
  const form_data = JSON.stringify(params.form_data);

  return `${blockVillageParams.url}?form_data=${form_data}&standalone=${params.standalone}&height=${params.height}`;
}

function updateDistrictBlockIframeURL(url) {
  var iframe = document.getElementById('district-block-graph');
  iframe.src = url;
}

function updateDistrictIframeURL(url) {
  var iframe = document.getElementById('district-graph');
  iframe.src = url;
}

function updateDistrictClassIframeURL(url) {
  var iframe = document.getElementById('district-class-graph');
  iframe.src = url;
}

function updateBlockVillageIframeURL(url) {
  var iframe = document.getElementById('block-village-graph');
  iframe.src = url;
}
