// CDN lib modules
import $ from 'jquery';
import Plotly from 'plotly.js-dist-min';
import Papa from 'papaparse';

// local modules
import './mathjax_config.js';
import { ProcrustesMap, PROCRUSTES_MAP_LAYERS } from './procrustes_map.js';
import '../styles/procrustes.css';

// constants
const ANIM_TIME = 300;

/*
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
    table.appendChild(table_head);
    table.appendChild(table_body);
    $(table).addClass("table");
    $(table).addClass("table-striped");
    return table;
}
*/

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
    let type = collocation_data.type;

    let data = [
        {
            x: intervals,
            y: empirical_cov,
            mode: "lines+markers",
            type: "scatter",
            name: "εμπειρικές τιμές",
        },
        {
            x: intervals,
            y: fitted_cov,
            mode: "lines",
            type: "scatter",
            name: `προσαρμοσμένη ${type}`,
        },
    ];

    let layout = {
        title: "Συνάρτηση συμμεταβλητότητας f<sub>c</sub>(d)",
        xaxis: { title: "Απόσταση(km)" },
        yaxis: { title: "Συμμεταβλητότητα (cm<sup>2</sup>)" },
    }
    Plotly.newPlot("output_cov_plot", data, layout, {staticPlot:true});
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

function update_points_on_map(layer) {

    let map = $('#map').data('map');
    map.clear_points(layer);

    const file = $(`#id_${layer.name}`).prop('files')[0];
    const format = $('#id_points_format input[type=radio]:checked').val();
    const contain_id = format === 'id,xs,ys,xt,yt';

    Papa.parse(file, {
        delimitersToGuess: [' ', ',', ';'],
        skipEmptyLines: 'greedy',
        complete: function(results) {
            const coords = results.data.map(function (line) {
                // remove empty entries
                let entries = line.filter(function (entry) { return /\S/.test(entry); });
                // remove id entry
                if (contain_id) {
                    entries = entries.slice(1);
                }
                return entries.map(function (entry) { return parseFloat(entry); });
            });
            // now we got coordinates like this
            // [[x0, y0, x'0, y'0], [x1, y1, x'1, y'1] ...]
            // try to guess which set if any set is in ggrs87
            const source_coords = coords.map(e => { return e.slice(0, 2); });
            const target_coords = coords.map(e => { return e.slice(2, 4); });
            const source_is_ggrs87 = map.check_if_ggrs87_pointset(source_coords);
            const target_is_ggrs87 = map.check_if_ggrs87_pointset(target_coords);

            if (source_is_ggrs87 || target_is_ggrs87) {
                map.add_points(
                    layer,
                    source_is_ggrs87 ? source_coords : target_coords
                );
            }
        }
    });
}

$('#id_reference_points').change(function() {
    update_points_on_map(PROCRUSTES_MAP_LAYERS.REFERENCE_POINTS);
});
$('#id_validation_points').change(function() {
    update_points_on_map(PROCRUSTES_MAP_LAYERS.VALIDATION_POINTS);
});

// main
$(document).ready(function() {
    $('#id_cov_function_type').hide(); // initial state

    let map = new ProcrustesMap();
    $('#map').data('map', map);

    if ($('#id_reference_points')[0].files.length == 1) {
        update_points_on_map(PROCRUSTES_MAP_LAYERS.REFERENCE_POINTS);
    }
    if ($('#id_validation_points')[0].files.length == 1) {
        update_points_on_map(PROCRUSTES_MAP_LAYERS.VALIDATION_POINTS);
    }
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
