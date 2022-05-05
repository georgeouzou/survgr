const ANIM_TIME = 300;

function generate_reference_coordinate_table(result) {

    let source_coords = result.input.cs_source.coords; // arrays with [x,y]
    let target_coords = result.input.cs_target.coords;
    let transf_coords = result.output.cs_transformed.coords;

    let table_head = document.createElement("thead");
    {
        let coordinate_systems_row = document.createElement("tr");
        let coords_type_row = document.createElement("tr");
        ["Source", "Target", "Transformed"].forEach(function (desc) {
            let c = document.createElement("th");
            c.textContent = desc;
            $(c).attr("colspan", "2");
            $(coordinate_systems_row).append(c);

            let x = document.createElement("th");
            let y = document.createElement("th");
            x.textContent = "X (m)";
            y.textContent = "Y (m)";
            $(coords_type_row).append([x, y]);
        });
        $(table_head).append([coordinate_systems_row, coords_type_row]);
    }

    let table_body = document.createElement("tbody");
    if (source_coords.length == target_coords.length && source_coords.length == transf_coords.length) {
        for (let i = 0; i < source_coords.length; ++i) {
            let source_x = document.createElement("td");
            let source_y = document.createElement("td");
            let target_x = document.createElement("td");
            let target_y = document.createElement("td");
            let transformed_x = document.createElement("td");
            let transformed_y = document.createElement("td");
            source_x.textContent = source_coords[i][0].toFixed(3);
            source_y.textContent = source_coords[i][1].toFixed(3);
            target_x.textContent = target_coords[i][0].toFixed(3);
            target_y.textContent = target_coords[i][1].toFixed(3);
            transformed_x.textContent = transf_coords[i][0].toFixed(3);
            transformed_y.textContent = transf_coords[i][1].toFixed(3);
            let body_row = document.createElement("tr");
            $(body_row).append([source_x, source_y, target_x, target_y, transformed_x, transformed_y]);
            $(table_body).append(body_row);
        }
    }

    let table = document.createElement("table");
    table.appendChild(tableHead);
    table.appendChild(tableBody);
    $(table).addClass("table");
    $(table).addClass("table-striped");
    return table;
}

function generate_statistics_table(name, statistics) {

    let table = document.createElement("table");
    $(table).addClass("table");

    table.innerHTML = `
        <thead>
            <tr>
                <th>${name}</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Min: ${statistics.min.toFixed(3)}</td>
            </tr>
            <tr>
                <td>Max: ${statistics.max.toFixed(3)}</td>
            </tr>
            <tr>
                <td>Mean: ${statistics.mean.toFixed(3)}</td>
            </tr>
            <tr>
                <td>Std: ${statistics.std.toFixed(3)}</td>
            </tr>
        </tbody>
    `;

    return table;
}

function generate_covariance_plot(collocation_data) {
    let intervals = collocation_data.distance_intervals;
    let empirical_cov = collocation_data.empirical_cov;
    let fitted_cov = collocation_data.fitted_cov;

    let data = [
        {
            x: intervals,
            y: empirical_cov,
            mode: "lines+markers",
            type: "scatter",
            name: "empirical",
        },
        {
            x: intervals,
            y: fitted_cov,
            mode: "lines",
            type: "scatter",
            name: "sinc fitted",
        },
    ];

    let layout = {
        title: "Συνάρτηση συμμεταβλητότητας f<sub>c</sub>(d)",
        xaxis: { title: "Απόσταση(km)" },
        yaxis: { title: "Συμμεταβλητότητα (cm<sup>2</sup>)" },
    }
    Plotly.newPlot("output_cov_plot", data, layout, {staticPlot:true});
}

function init_map() {
    const view = new ol.View({
        projection: 'EPSG:3857', //spherical merc
        center: ol.proj.transform([25,38.4],'EPSG:4326','EPSG:3857'),
        zoom: 6,
    });
    const default_interactions_list = ol.interaction.defaults({altShiftDragRotate:false, pinchRotate:false});

    let map = new ol.Map({
        layers:[
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
        ],
        target: "map",
        view: view,
        interactions: default_interactions_list,
    });

    $('#map').data('map', map);
}



$('#form_input').submit(function(event) {
    event.preventDefault();
    $('#output_cov_plot').empty();
    $('#output_transformation_params').empty();

    var fd = new FormData($(this)[0]);
    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: fd,
        dataType: "json",
        processData: false,
        contentType: false,
    }).done(function (json_output){
        {
            let transformation = json_output.transformation;
            $("#output_transformation_params").append(
                generate_statistics_table(`${transformation.type} Transformation Reference Statistics`, transformation.statistics)
            );
        }
        {
            let transformation = json_output.transformation;
            if ("validation_statistics" in transformation) {
                $("#output_transformation_params").append(
                    generate_statistics_table(`${transformation.type} Transformation Validation Statistics`, transformation.validation_statistics)
                );
            }
        }

        if ("collocation" in json_output) {
            let collocation = json_output.collocation;
            generate_covariance_plot(collocation);
        }
        if ("residual_correction" in json_output) {
            if ("validation_statistics" in json_output.residual_correction) {
                $("#output_transformation_params").append(
                    generate_statistics_table(`Correction Validation Statistics`, json_output.residual_correction.validation_statistics)
                );
            }
        }

    }).fail(function (jqXHR) {
    });
});


// change visibility of covariance function type
$('#id_residual_correction_type :input[type=radio]').change(function() {
    const COLLOCATION_ID = 1;
    if (this.value == COLLOCATION_ID) {
        $('#id_cov_function_type').show(ANIM_TIME);
    } else {
        $('#id_cov_function_type').hide(ANIM_TIME);
    }
});

function remove_layer_from_map(name) {
    let ol_map = $('#map').data('map');
    let layers_to_remove = [];
    ol_map.getLayers().forEach(function (layer) {
        if (layer.get('name') === name) {
            layers_to_remove.push(layer);
        }
    });
    layers_to_remove.forEach(function (layer) {
        ol_map.removeLayer(layer);
    });
}

$('#id_reference_points').change(function() {
    let ol_map = $('#map').data('map');
    remove_layer_from_map('reference_points');

    const file = $('#id_reference_points').prop('files')[0];
    const format = $('#id_points_format').val();
    const num_entries = format === 'id,xs,ys,xt,yt' ? 5 : 4;

    Papa.parse(file, {
        delimitersToGuess: [' ', ',', ';'],
        skipEmptyLines: 'greedy',
        complete: function(results) {
            const points = results.data.map(function (line) {
                const entries = line.filter(function (entry) { return /\S/.test(entry); });

                const idx_x = num_entries == 5 ? 3 : 2;
                const idx_y = num_entries == 5 ? 4 : 3;
                let coords = [parseFloat(entries[idx_x]), parseFloat(entries[idx_y])];
                coords = ol.proj.transform(coords, 'EPSG:2100', 'EPSG:3857');

                return new ol.Feature({
                    geometry: new ol.geom.Point(coords),
                });
            });

            const vector_source = new ol.source.Vector({
                features: points,
            });

            let vector_layer = new ol.layer.Vector({
                source: vector_source,
            });
            vector_layer.set('name', 'reference_points');

            ol_map.addLayer(vector_layer);
            ol_map.getView().fit(vector_source.getExtent());
        }
    });
});

// main
$(document).ready(function() {
    $('#id_cov_function_type').hide(); // initial state
    init_map();
    proj4.defs("EPSG:2100","+proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=-199.87,74.79,246.62,0,0,0,0 +units=m +no_defs");
    ol.proj.proj4.register(proj4);
});

/*
$("#id_transformation_type > input[type=radio]").change(function() {
    let carousel = bootstrap.Carousel.getOrCreateInstance($("#id_carousel_transformation_type")[0]);
    carousel.to(this.value);
});

$("#id_residual_correction_type > input[type=radio]").change(function() {
    let carousel = bootstrap.Carousel.getOrCreateInstance($("#id_carousel_residual_correction_type")[0]);
    carousel.to(this.value);
});

$("#id_carousel_transformation_type").on("slide.bs.carousel", function (e) {
    let index = e.to;
   // $("#id_transformation_type > input[type=radio]").removeAttr("checked");
    $(`#id_transformation_type > input[type=radio][value=${index}]`).prop("checked", true);
});
*/
