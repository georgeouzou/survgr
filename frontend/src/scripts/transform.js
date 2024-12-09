import $ from 'jquery';
import Bloodhound from 'corejs-typeahead';
import { get as idb_get } from 'idb-keyval';
import parseDMS from 'parse-dms';

import '../styles/transform.css';
import HATTBLOCK_FEATURES_URL from '../assets/hattblocks.min.geojson';
import { init_map } from './hattblock_map.js';

/*
 * Constants
 */
const NOT_SELECTED_ID = -1;
const ANIM_TIME = 300;
const HATT_NEW_SRID = 1000000;
const HATT_OLD_SRID = 1000008;
const NEW_BESSEL_SRIDS = [1000000, 1000001, 1000002, 1000003, 4815];
const OLD_BESSEL_SRIDS = [1000007, 1000008];
const GEODETIC_SRIDS = [4121,4815,4326,4230,1000004,1000007];
const PROCRUSTES_SRID = 1000006

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

function initProcrustesSelector()
{
  $('#from-srid').on('change', function() {
    const from_srid = $(this).val();
    const to_srid = $('#to-srid').val();
    if (from_srid == PROCRUSTES_SRID) {
      $(`#to-srid option[value="${PROCRUSTES_SRID}"]`).parent().attr('hidden', false);
      $('#to-srid').val(PROCRUSTES_SRID).trigger('change');
      $('#to-srid').attr('disabled', true);
    } else if (to_srid == PROCRUSTES_SRID && from_srid != PROCRUSTES_SRID) {
      $('#to-srid').val(HATT_NEW_SRID).trigger('change');
      $(`#to-srid option[value="${PROCRUSTES_SRID}"]`).parent().attr('hidden', true);
      $('#to-srid').attr('disabled', false);
    }
  });
  // default visibility for procrustes-off
  $(`#from-srid option[value="${PROCRUSTES_SRID}"]`).parent().attr('hidden', true);
  $(`#to-srid option[value="${PROCRUSTES_SRID}"]`).parent().attr('hidden', true);

  idb_get('procrustes_saved_results')
  .then((val) => {
    if (val) {
      $(`#from-srid option[value="${PROCRUSTES_SRID}"]`).parent().attr('hidden', false);
    }
  });
 
}

function initSelectors(){
  // visibility of hatt selection html elements is based
  // on the selected srid
  // SRIDS are defined in transform.py

  function isNewBesselSRID(srid){
    return NEW_BESSEL_SRIDS.indexOf(parseInt(srid)) != -1;
  }
  function isOldBesselSRID(srid){
    return OLD_BESSEL_SRIDS.indexOf(parseInt(srid)) != -1;
  }
  function isAnyBesselSRID(srid){
    return isNewBesselSRID(srid) || isOldBesselSRID(srid);
  }

  $(".srid-selection").on('change', function(){
    // hide or show new bessel hatt selection
    const fromSrid = $("#from-srid").val();
    const toSrid = $("#to-srid").val();

    if (fromSrid == HATT_NEW_SRID || (isNewBesselSRID(fromSrid) && !isAnyBesselSRID(toSrid))) {
      $("#from-hatt").show(ANIM_TIME);
      $("#from-hatt input").prop('disabled', false);
    } else {
      $("#from-hatt").hide(ANIM_TIME);
      $("#from-hatt input").prop('disabled', true);
    }

    if (toSrid == HATT_NEW_SRID || (!isAnyBesselSRID(fromSrid) && isNewBesselSRID(toSrid))) {
      $("#to-hatt").show(ANIM_TIME);
      $("#to-hatt input").prop('disabled', false);
    } else {
      $("#to-hatt").hide(ANIM_TIME);
      $("#to-hatt input").prop('disabled', true);
    }

    // hide or show type of inverse okxe transformation
    if (!isAnyBesselSRID(fromSrid) && isNewBesselSRID(toSrid)) {
      $("#okxe-inverse-options").show(ANIM_TIME);
      $("#okxe-inverse-options select").prop('disabled', false);
    } else {
      $("#okxe-inverse-options").hide(ANIM_TIME);
      $("#okxe-inverse-options select").prop('disabled', true);
    }

    // hide or show old hatt centroid inputs
    if (fromSrid == HATT_OLD_SRID) {
      $("#from-old-hatt").show(ANIM_TIME);
      $("#from-old-hatt input").prop('disabled', false);
    } else {
      $("#from-old-hatt").hide(ANIM_TIME);
      $("#from-old-hatt input").prop('disabled', true);
    }
    if (toSrid == HATT_OLD_SRID) {
      $("#to-old-hatt").show(ANIM_TIME);
      $("#to-old-hatt input").prop('disabled', false);
    } else {
      $("#to-old-hatt").hide(ANIM_TIME);
      $("#to-old-hatt input").prop('disabled', true);
    }

  });

  initProcrustesSelector();

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
  $(".srid-selection").val(HATT_NEW_SRID).trigger('change');
  $("#input-type input").trigger('change');
}


function getInputType(){
  return $('#input-type input:checked').val();
}

function validateInput(){
  const fromSrid = $("#from-srid").val();
  const toSrid = $("#to-srid").val();

  if ((fromSrid == PROCRUSTES_SRID && toSrid != PROCRUSTES_SRID) ||
      (fromSrid != PROCRUSTES_SRID && toSrid == PROCRUSTES_SRID)) {
    $('#output-area').val('Σφάλμα: Οι μετασχηματισμοί Προκρούστη απαιτούν όμοια "Aπό" και "Πρός" συστήματα αναφοράς.');
    return false;
  }

  if ((fromSrid == HATT_NEW_SRID && $("#from-hatt .hatt-id").val() == -1) || 
      (toSrid == HATT_NEW_SRID && $("#to-hatt .hatt-id").val() == -1)) {
    $('#output-area').val("Σφάλμα: Παρακαλώ επιλέξτε φύλλο χάρτη HATT.");
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

function send_transform_form_data(form, form_data) {
  $.ajax({
    type: 'POST',
    url: form.attr('action'),
    data: form_data,
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
}

$('#form-params').submit(function (e){
  e.preventDefault();

  if (!validateInput()) {
    clearOutputAccuracyArea();
    return;
  }

  var fd = new FormData($(this)[0]);
  fd.append("input", new Blob([$('#input-area').val()], { type: "text/plain;charset=utf-8"}));

  if (fd.get('from_srid') == HATT_OLD_SRID) {
    const phi = $('#from-old-hatt-centroid-phi').val();
    const lambda = $('#from-old-hatt-centroid-lambda').val();
    const val = parseDMS(phi + ' ' + lambda);
    fd.append("from_hatt_centroid", JSON.stringify(val));
  }
  if (fd.get('to_srid') == HATT_OLD_SRID) {
    const phi = $('#to-old-hatt-centroid-phi').val();
    const lambda = $('#to-old-hatt-centroid-lambda').val();
    const val = parseDMS(phi + ' ' + lambda);
    fd.append("to_hatt_centroid", JSON.stringify(val));
  }
  
  if (fd.get('from_srid') == PROCRUSTES_SRID) {
    // in this case the select input is disabled, so we set the value explicitly
    fd.set('to_srid', PROCRUSTES_SRID);
    idb_get('procrustes_saved_results')
    .then((val) => {
      fd.append('procrustes', new Blob([JSON.stringify(val)], { type: 'application/json;charset=utf-8'}));
      send_transform_form_data($(this), fd);
    });
  } else {
    send_transform_form_data($(this), fd);
  }  
});

$(".dms-text").on("focus", (e) => {
  let t = $(e.target).val();
  t = t.replace('°', ' ').replace('\'', '');
  $(e.target).val(t);
});

$(".dms-text").on("focusout", (e) => {
  const t = $(e.target).val();
  const dm = t.split(/\s+/);
  const degrees = (dm.length > 0) ? Math.abs(parseInt(dm[0]) || 0) : 0;
  let minutes = (dm.length > 1) ? Math.abs(parseInt(dm[1]) || 0) : 0;
  minutes = Math.max(0, Math.min(59, minutes));
  const is_neg = (dm.length > 0) ? dm[0].startsWith('-') : false;
  const neg_sign = is_neg ? "-" : "";
  $(e.target).val(neg_sign + degrees + "°" + minutes + "'");
});

/*
 * Main
 */
$(function() {
  initBloodhound();
  init_map();
  initSelectors();

  // set hatt id element values to default -1 (nothing selected)
  $('.hatt-id').val(NOT_SELECTED_ID);
});

