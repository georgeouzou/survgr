/*
 * Constants
 */
var NOT_SELECTED_ID = -1;
var ANIM_TIME = 300;
var HATT_SRID = 1000000;
var OLD_GREEK_SRIDS = [1000000, 1000001, 1000002, 1000003, 4815];
var GEODETIC_SRIDS = [4121,4815,4326,4230,1000004];

/*
 * Initializers
 */
function initBloodhound(){

  // hattblock names need normalization for nice autocompletion
  var charMap = {
    "ά": "α",
    "έ": "ε",
    "ί": "ι",
    "ή": "η",
    "ύ": "υ",
    "ό": "ο",
    "ώ": "ω"
  };

  // normalization function that maps certain accented characters
  var normalize = function (input) {
    input = input.replace(/[άέίήύόώ]/gi, function(m){
      return charMap[m.toLowerCase()];
    });
    return input;
  };
  
  var engine = new Bloodhound({
    datumTokenizer: function (obj){
      return normalize(obj.name).split(/[-.]/g);
    },
    queryTokenizer: function (query){
      return normalize(query).split(/[-.\s+]/g);
    },
    identify: function (obj) { return obj.id; },
    prefetch: {
      url: HATTBLOCK_FEATURES_URL,
      // transforms geojson data and create normalized names to use with autocompletion
      transform: function (featureCollection){
        return $.map(featureCollection.features, function(feat){
          return { id: feat.id, name: feat.properties.name }
        })
      }
    }
  });

  // store hatt id when user selects a value from the autosuggestion engine
  $('.hatt-name').on('typeahead:select typeahead:autocomplete', function(e, obj){
    // get the relevant hatt id element and change it's value
    var hatt = $(this).parents('.hatt-selection');
    hatt.find('.hatt-id').val(obj.id);
  });
  
  $('.hatt-name').typeahead({
    // options
    minLength: 1,
    hint: true,
    highlight: false
  },{
    // dataset
    name: 'hattblocks',
    display: 'name',
    source: engine,
  });
}

const geometryStyle = new ol.style.Style({
    fill: new ol.style.Fill({
        color: 'rgba(255, 255, 255, 0.6)',
    }),
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 1,
    }),
});

const geometrySelectedStyle = new ol.style.Style({
    fill: new ol.style.Fill({
        color: 'rgba(255, 255, 255, 0.8)',
    }),
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 3,
    }),
});

const labelStyle = new ol.style.Style({
    text: new ol.style.Text({
        font: '13px Calibri,sans-serif',
        fill: new ol.style.Fill({
            color: '#000',
        }),
        overflow: true,
    }),
});

const featureStyle = [geometryStyle, labelStyle];
const featureSelectedStyle = [geometrySelectedStyle, labelStyle];

function initMap() {
    
  // Map initialization.
  // Uses a single map instance enabling the user to select graphically 
  // the hatt block of choice. The map is contained within a modal and 
  // the modal is related/bound on the show event to the calling html 
  // container class "hatt-selection"

  // this is the geojson source used in the map
  var hattblocks = new ol.source.Vector({
    url:HATTBLOCK_FEATURES_URL,
    projection : 'EPSG:4326', // wgs84 ref. system
    format: new ol.format.GeoJSON()
  });
  var view = new ol.View({
      projection: 'EPSG:3857', //spherical merc 
      center: ol.proj.transform([25,38.4],'EPSG:4326','EPSG:3857'),
      zoom: 6,
      maxZoom: 10
  });

  let only_blocks_layer = new ol.layer.VectorImage({
      source: hattblocks,
      maxZoom: 7,
  });

  let detailed_blocks_layer = new ol.layer.Vector({
      source: hattblocks,
      minZoom: 7,
      declutter: true,
      style: function (feature, resolution) {
          labelStyle
              .getText()
              .setText(getHattblockLabel(feature, resolution));
          return featureStyle;
      },
  });


  var default_interactions_list = ol.interaction.defaults({altShiftDragRotate:false, pinchRotate:false});

  var map = new ol.Map({
    layers:[
      new ol.layer.Tile({
        source: new ol.source.OSM()
      }),
      only_blocks_layer,
      detailed_blocks_layer,
    ],
    target: "map",
    view: view,
    interactions: default_interactions_list,
  });

  selectAction = new ol.interaction.Select({
      style: function (feature, resolution) {
          labelStyle
              .getText()
              .setText(getHattblockLabel(feature, resolution));
          return featureSelectedStyle;
      }
  });
  map.addInteraction(selectAction);

  // on select feature
  selectAction.getFeatures().on('add', function (e){
    let feature = e.element;
    let name = feature.get('name');
    $('#selected-feature-name').html('Επιλογή φύλλου χάρτη: ' + name);
  });
  // on unselect feature
  selectAction.getFeatures().on('remove', function (e){
    $('#selected-feature-name').html('Επιλογή φύλλου χάρτη: ');
  });

  /*
   * Modal events
   */
  var bound_hatt;

  $('#map-modal').on('show.bs.modal', function (e){
    // get the related hatt container element and store it to the modal instance
    bound_hatt = $(e.relatedTarget).parents('.hatt-selection');
    // clear previous selected feature if exists
    var selectedFeatures = selectAction.getFeatures();
    selectedFeatures.clear();
    // and select again based on related id value
    var id = parseInt(bound_hatt.find('.hatt-id').val());  
    if (id != NOT_SELECTED_ID){
      if (hattblocks.getFeatures().length == 0){
          // CAUTION: the source might not have loaded the features the first time we open the map so...
          hattblocks.on('change', function(){
            selectedFeatures.push(hattblocks.getFeatureById(id));
          });
      } else {
        selectedFeatures.push(hattblocks.getFeatureById(id));       
      }
    }
  });

  $('#map-modal').on('shown.bs.modal', function (e) {
    // BUG: this is needed because i use the map inside of a modal
    map.updateSize();
    // pan view to the selected feature
    if (selectAction.getFeatures().getLength() > 0){
      // get xmin, ymin, xmax, ymax of selected feature
      var extent = selectAction.getFeatures().item(0).getGeometry().getExtent(); 
      var xy = [(extent[2] + extent[0])/2, (extent[3] + extent[1])/2];
      var pan = ol.animation.pan({
        duration: 3*ANIM_TIME,
        source: view.getCenter()
      });
      map.beforeRender(pan);
      view.setCenter(xy);
    } 
  });

  $('#map-modal').on('hide.bs.modal', function (e) {
    // update the selected hatt name and hatt id elements
    if (!bound_hatt)
      return;
  
    if (selectAction.getFeatures().getLength() > 0){
      var selectedFeature = selectAction.getFeatures().pop();
      bound_hatt.find('.hatt-id').val(selectedFeature.getId());
      bound_hatt.find('.hatt-name').typeahead('val', selectedFeature.get('name'));
    } else {
      bound_hatt.find('.hatt-id').val(NOT_SELECTED_ID);
      bound_hatt.find('.hatt-name').typeahead('val', '');
    }
  });
}

function initSelectors(){
  // visibility of hatt selection html elements is based
  // on the selected srid
  // SRIDS are defined in transform.py
  

  function isOldGreek(srid){
    return OLD_GREEK_SRIDS.indexOf(parseInt(srid)) != -1;
  }

  $(".srid-selection").on('change', function(){
    // hide or show hatt selection
    fromSrid = $("#from-srid").val();
    toSrid = $("#to-srid").val();

    if (fromSrid == HATT_SRID || (isOldGreek(fromSrid) && !isOldGreek(toSrid))) {
      $("#from-hatt").show(ANIM_TIME);
      $("#from-hatt input").prop('disabled', false);
    } else {
      $("#from-hatt").hide(ANIM_TIME);
      $("#from-hatt input").prop('disabled', true);
    }

    if (toSrid == HATT_SRID || (!isOldGreek(fromSrid) && isOldGreek(toSrid))) {
      $("#to-hatt").show(ANIM_TIME);
      $("#to-hatt input").prop('disabled', false);
    } else {
      $("#to-hatt").hide(ANIM_TIME);
      $("#to-hatt input").prop('disabled', true);
    }
  });

  //change visibility of csv format options on input-type radio change
  $('#input-type input').on('change', function() {
   if (getInputType() == 'geojson'){
    $('.csv-format').hide(ANIM_TIME);
    $('.csv-format select').prop('disabled', true);
   } else {
    $('.csv-format').show(ANIM_TIME);
    $('.csv-format select').prop('disabled', false);
   }
  });

  // change labels of csv fields based on srid coordinate type
  $("#from-srid").on('change', function(){
    var template = ($.inArray(parseInt($("#from-srid").val()), GEODETIC_SRIDS) != -1) ? 
      ["λ, φ","λ, φ, h","id, λ, φ","id, λ, φ, h", "φ, λ","φ, λ, h","id, φ, λ","id, φ, λ, h"] : 
      ["Ε, Ν","Ε, Ν, h","id, Ε, Ν","id, Ε, Ν, h", "N, E", "N, E, h","id, N, E","id, N, E, h",];
    
    $("#csv-fields option").each(function(i){
      this.text = template[i];
    });
  });
   
  // select manually default hatt srid on startup
  $(".srid-selection").val(HATT_SRID).trigger('change');
  $("#input-type input").trigger('change');
}

/*
 *  Utility
 */
function decdeg2dms(dd) {
    let is_positive = dd >= 0;
    dd = Math.abs(dd);
    let seconds = dd*3600.0;
    let minutes = Math.floor(seconds/60.0);
    seconds = seconds % 60.0
    let degrees = Math.floor(minutes/60.0)
    minutes = minutes % 60.0
    let sign = is_positive ? '' :  '-';
    return [sign,degrees,minutes,seconds];
}

function getHattblockLabel(feature, resolution) {
    let name = feature.get('name');
    let okxe_id = feature.get('okxe_id');

    if (resolution > 400) {
        return [`#${okxe_id}`, ''];
    }

    let phi = feature.get('cy');
    let lambda = feature.get('cx');
    let [sign_phi, d_phi, m_phi, s_phi] = decdeg2dms(phi);
    let [sign_lambda, d_lambda, m_lambda, s_lambda] = decdeg2dms(lambda);


    let info1 = ` Φo ${sign_phi}${d_phi}\u00B0${m_phi}`;
    let info2 = ` Λo ${sign_lambda}${d_lambda}\u00B0${m_lambda}'`;

    return [
        `#${okxe_id}`, '',
        '\n', '',
        ` ${name}`, '',
        '\n', '',
        info1, 'italic 11px Calibri, sans-serif',
        '\n', '',
        info2, 'italic 11px Calibri, sans-serif',
    ];
}

function getInputType(){
  return $('#input-type input:checked').val();
}

function validateInput(){
  fromSrid = $("#from-srid").val();
  toSrid = $("#to-srid").val();
  if ((fromSrid == HATT_SRID && $("#from-hatt .hatt-id").val() == -1) || 
    (toSrid == HATT_SRID && $("#to-hatt .hatt-id").val() == -1)) {
    $('#output-area').val("Παρακαλώ επιλέξτε φύλλο χάρτη HATT.");
    return false;
  }
  return true;
}

function clearOutputAccuracyArea()
{
  $('#output-accuracy-area').hide(ANIM_TIME);
}

function fillOutputAccuracyArea(transform_steps) 
{
  var steps = transform_steps.map(function (i) { return "<li>"+String(i)+"</li>"; });
  $('#output-accuracy-area').hide(ANIM_TIME, function() {
    $('#output-accuracy-area').empty();
    $('#output-accuracy-area').append("<h3>Βήματα και ακρίβειες υπολογισμών:</h3><ul>" + steps.join('') + "</ul>");
    $('#output-accuracy-area').show(ANIM_TIME);
  });
}

/*
 * Main
 */
$(function() { 
  initBloodhound();
  initMap();
  initSelectors();

  // set hatt id element values to default -1 (nothing selected)
  $('.hatt-id').val(NOT_SELECTED_ID);

  $('#form-params').submit(function (e){
    e.preventDefault();
    
    if (!validateInput()) return;
    console.log($(this).serialize());

    var fd = new FormData($(this)[0]);
    fd.append("input", new Blob([$('#input-area').val()], { type: "text/plain;charset=utf-8"}));
    
    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: fd,
      dataType: "json",
      processData: false, // this is not to url-encode the fd object
      contentType: false // this is how it automatically computes the boundary
    }).done(function (json_output){
      if (json_output.type == "csv") {
        $('#output-area').val(json_output.result);
      } else if (json_output.type == "geojson") {
        $('#output-area').val(JSON.stringify(json_output.result));
      }
      fillOutputAccuracyArea(json_output.steps)
    }).fail(function (jqXHR) {
      $('#output-area').val(jqXHR.responseText);
      clearOutputAccuracyArea();
    });
  });
});

