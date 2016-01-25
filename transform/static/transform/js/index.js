$(function() {
  var hattblockSource = new ol.source.Vector({
    url: HATTBLOCK_FEATURES_URL,
    format: new ol.format.GeoJSON()
  });


  
  var map = new ol.Map({
    layers:[
      new ol.layer.Tile({
        source: new ol.source.OSM()
      }),
      new ol.layer.Vector({
        source: hattblockSource
      })
    ],
    target: "map",
    view: new ol.View({
      projection: 'EPSG:4326', // wgs84,
      center: [25,37],
      zoom: 6
    })
  });

  $("#map").on("click", function(e){
    console.log(hattblockSource.getFeatures().length);
  });

  var charMap = {
    "ά": "α",
    "έ": "ε",
    "ί": "ι",
    "ή": "η",
    "ύ": "υ",
    "ό": "ο",
    "ώ": "ω"
  };

  var normalize = function (input) {
    input = input.replace(/[άέίήύόώ]/gi, function(m){
      return charMap[m.toLowerCase()];
    });
    return input;
  };
  var states = ['Άβδηρα', 'Αγαθονήσιον', 'Αγ.Ειρήνη', 'Αγιά', 'Άγ.Κήρυκος',
    'Αγ.Μαρίνα', 'Άγ.Ματθαίος', 'Αγ.Νικόλαος-Βόρ.', 'Αγ.Νικόλαος-Νότ.', 'Άγ.Νικόλαος-Κρήτης', 'Hawaii',
     'Αγ.Παρασκευή', 'Άγ.Πέτρος', 'Αγιόφυλλον'];

  var queryTokenizer = function (query) {
    return normalize(query).split(/[-.\s+]/g);
  };

  var engine = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
      //datumTokenizer: datumTokenizer,
      queryTokenizer: queryTokenizer,
      local: $.map(hattblockSource.getFeatures(), function (feat) {
          return {
              id: feat.id,
               // Normalize the name - use this for searching
              name: normalize(feat.name).replace(/[-.]/g, ' '),
              // Include the original name - use this for display purposes
              displayName: name
          };
      })
  });

  $('.typeahead').typeahead({
    // options
    minLength: 1,
    hint: true,
    highlight: false
  },{
    // dataset
    name: 'hattblocks',
    display: 'displayName',
    source: engine,
  });

  $('.typeahead').bind('typeahead:select', function(ev, suggestion) {
    console.log(suggestion);

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