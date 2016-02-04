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
    datumTokenizer: function(obj){
      return normalize(obj.name).split(/[-.]/g);
    },
    queryTokenizer: function(query){
      return normalize(query).split(/[-.\s+]/g);
    },
    identify: function(obj) { return obj.id; },
    prefetch: {
      url: HATTBLOCK_FEATURES_URL,
      // transforms geojson data and create normalized names to use with autocompletion
      transform: function(featureCollection){
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

  // $('.hatt-name').on('typeahead:change', function(e){
  //   // check to which text box is the change happening
  //   engine.search(e.target.value, function(suggestion){
  //     if (suggestion.length == 1){
  //       var hatt = $('.hatt-name').parents('.hatt-selection');
  //       hatt.find('.hatt-id').val(suggestion[0].id);
  //       console.log(hatt.find('.hatt-id').val());
  //     } 
  //   });
  // });
  
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

function initMap(){
  /*
   * Map initialization.
   * Uses a single map instance enabling the user to select graphically 
   * the hatt block of choice. The map is contained within a modal and 
   * the modal is related/bound on the show event to the calling html 
   * container class "hatt-selection" 
   */

  // this is the geojson source used in the map
  var hattblocks = new ol.source.Vector({
    url:HATTBLOCK_FEATURES_URL,
    projection : 'EPSG:4326', // wgs84 ref. system
    format: new ol.format.GeoJSON()
  });
  var view = new ol.View({
      projection: 'EPSG:3857', //spherical merc 
      center: ol.proj.transform([25,38.4],'EPSG:4326','EPSG:3857'),
      zoom: 6
  })
  var map = new ol.Map({
    layers:[
      new ol.layer.Tile({
        source: new ol.source.OSM()
      }),
      new ol.layer.Vector({
        source: hattblocks
      }),
    ],
    target: "map",
    view: view
  });

  selectAction = new ol.interaction.Select();
  map.addInteraction(selectAction);

  // on select feature
  selectAction.getFeatures().on('add', function(e){
    var feature = e.element;
    $('#selected-feature-name').text('Επιλογή: ' + feature.get('name'));
  });
  // on unselect feature
  selectAction.getFeatures().on('remove', function(e){
    $('#selected-feature-name').text('Επιλογή: ');
  });

  var NOT_SELECTED_ID = -1;
  // set hatt id element values to default -1 (nothing selected)
  $('.hatt-id').val(NOT_SELECTED_ID);
  // related bound hatt container (contains the name and id html elements)
  
  /*
   * Modal events
   */
  var bound_hatt;

  $('#mapModal').on('show.bs.modal', function (e){
    // get the related hatt container element and store it to the modal instance
    bound_hatt = $(e.relatedTarget).parents('.hatt-selection');
    // change the title of the modal based on bound hatt container
    var title = bound_hatt.find('label').text();
    $(this).find('.modal-title').text(title);
    // clear previous selected feature if exists
    var selectedFeatures = selectAction.getFeatures();
    selectedFeatures.clear();
    // and select again based on related id value
    var id = parseInt(bound_hatt.find('.hatt-id').val());  
    if (id != -1){
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

  $('#mapModal').on('shown.bs.modal', function(e) {
    // BUG: this is needed because i use map inside of a modal
    map.updateSize();
    
    if (selectAction.getFeatures().getLength() > 0){
      var pan = ol.animation.pan({
        duration: 1000,
        source: (view.getCenter())
      });
      map.beforeRender(pan);
      view.setCenter(ol.proj.transform([25,38.4],'EPSG:4326','EPSG:3857'));
    } 
  });

  $('#mapModal').on('hide.bs.modal', function(e) {
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

// on document load
$(function() { 
  initBloodhound();
  initMap();
  // $('.typeahead').bind('typeahead:select', function(ev, suggestion) {
  //   console.log(suggestion);
  // });

  var params = $('#form-params');
  $(params).submit(function(e){
    e.preventDefault();
    var data = $(params).serialize();
    console.log(data);
  });

});


       // var getParams = function(){
          //   var params = {
          //     from_srid:parseInt($('#from_srid').val()),
          //     to_srid:parseInt($('#to_srid').val()),
          //     from_hatt_id:parseInt($('#from_hatt_id').val()),
          //     to_hatt_id:parseInt($('#to_hatt_id').val())
          //   };
          //   for (var p in params){
          //     if (!params[p]){
          //       delete params[p];
          //     }
          //   }
          //   return params;
          // };


          // $('#input_params').submit(function(e){
          //   e.preventDefault();   
          //   $.ajax({
          //     type: 'POST',
          //     url: $(this).attr('action'),
          //     dataType: 'json',
          //     contentType: 'application/json;charset=utf-8',
          //     data: JSON.stringify({
          //       params:getParams(), 
          //       geometries:getPoints()
          //     })
          //    }).done(function(response){
          //     ;
          //     setPoints(response.geometries);
          //   });  
          // });