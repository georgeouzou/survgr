// CDN lib modules
import $ from 'jquery';
import Plotly from 'plotly.js-dist-min';
import Papa from 'papaparse';
import { get as idb_get, set as idb_set, clear as idb_clear } from 'idb-keyval';

// local modules
import './mathjax_config.js';
import { ProcrustesMap, PROCRUSTES_MAP_LAYERS } from './procrustes_map.js';
import '../styles/procrustes.css';

// constants
const ANIM_TIME = 300;


// copy from backend
const TransformationType = {
	Similarity: 0,
	Affine: 1,
	Polynomial: 2,
};

const ResidualCorrectionType = {
    NoCorrection: 0,
	Collocation: 1,
	Hausbrandt: 2,
};

const CovarianceFunctionType = {
    Sinc: 0,
	Gaussian: 1,
	Exponential: 2,
	Spline: 3,
};

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
function generate_input_example_table() {
    const data = [
        [ 0, 'R', '-2053.94', '-1260.15', '435925.608', '4498716.989'],
        [ 1, 'R', '-1967.90', '-1392.66', '436010.417', '4498583.937'],
        [ 2, 'R', '-2160.13', '-1378.92', '435818.477', '4498599.266'],
        [ 3, 'R', '-1628.33', '-1596.61', '436348.218', '4498377.348'],
        [ 4, 'R', '-2113.55', '-1546.32', '435863.644', '4498431.584'],
        [ 5, 'R', '-1753.39', '-1610.69', '436223.087', '4498364.386'],
        [ 6, 'R', '-2072.28', '-1280.96', '435907.134', '4498696.338'],
        [ 7, 'R', '-1678.26', '-1769.90', '436296.819', '4498204.603'],
        [ 8, 'R', '-1896.61', '-1794.73', '436078.251', '4498181.554'],
        [ 9, 'V', '-1836.68', '-1550.86', '436140.233', '4498424.854'],
        [10, 'V', '-1453.61', '-1688.15', '436522.266', '4498284.378'],
        [11, 'V', '-1923.54', '-1574.84', '436053.504', '4498401.504'],
    ];

    for (let i = 0; i < data.length; ++i) {
        let id = document.createElement("td");
        let is_ref = document.createElement("td");
        let x_src = document.createElement("td");
        let y_src = document.createElement("td");
        let x_dst = document.createElement("td");
        let y_dst = document.createElement("td");
        id.textContent = data[i][0];
        is_ref.textContent = data[i][1];
        x_src.textContent = data[i][2];
        y_src.textContent = data[i][3]; 
        x_dst.textContent = data[i][4]; 
        y_dst.textContent = data[i][5]; 

        let row = document.createElement("tr");
        $(row).append([id, is_ref, x_src, y_src, x_dst, y_dst]);
        $('#id_input_example').append(row);
    }
}

function generate_statistics_table(name, statistics) {
    let table = document.createElement("table");
    $(table).addClass("table");

    table.innerHTML = `
        <thead>
            <tr>
                <th>${name} (m)</th>
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

    let col = document.createElement("div");
    $(col).addClass("col-sm-4");
    $(col).append(table);
    return col;
}

function generate_covariance_plot(covariance_data) {

    const cov_function_names  = {
        [CovarianceFunctionType.Sinc]: 'sinc',
        [CovarianceFunctionType.Gaussian]: 'gaussian',
        [CovarianceFunctionType.Exponential]: 'exponential',
        [CovarianceFunctionType.Spline]: 'spline'
    };
    let intervals = covariance_data.distance_intervals;
    let empirical_cov = covariance_data.empirical;
    let fitted_cov = covariance_data.fitted;
    let cov_function_name = cov_function_names[covariance_data.function_type];

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
            name: `προσαρμοσμένη ${cov_function_name}`,
        },
    ];

    let layout = {
        title: `Συνάρτηση συμμεταβλητότητας ${cov_function_name}(d)`,
        xaxis: { title: "Απόσταση(km)" },
        yaxis: { title: "Συμμεταβλητότητα (cm<sup>2</sup>)" },
        font: {
            family: 'Ubuntu',
        }
    }
    Plotly.newPlot("output_cov_plot", data, layout, {staticPlot:true});
}

function clear_results_block() {
    $('#output_statistics').empty();
    $('#output_cov_plot').empty();
    $('.results-block').hide();
}

function fill_results_block(json_output) {
    const transformation_names = {
        [TransformationType.Similarity]: 'μετασχηματισμό ομοιότητας',
        [TransformationType.Affine]: 'αφινικό μετασχηματισμό',
        [TransformationType.Polynomial]: 'πολυωνυμικό μετασχηματισμό',
    };
    const residual_correction_names = {
        [ResidualCorrectionType.Hausbrandt]: 'διόρθωση Hausbrandt',
        [ResidualCorrectionType.Collocation]: 'σημειακή προσαρμογή',
    };

    const transformation = json_output.transformation;
    const transformation_name = transformation_names[transformation.type];
    {
        $("#output_statistics").append(
            generate_statistics_table(
                `Στατιστικά υπολοίπων Reference με ${transformation_name}`,
                transformation.reference_statistics)
        );
    }
    {
        if ("validation_statistics" in transformation) {
            $("#output_statistics").append(
                generate_statistics_table(
                    `Στατιστικά υπολοίπων Validation με ${transformation_name}`,
                    transformation.validation_statistics)
            );
        }
    }

    const residual_correction = json_output.residual_correction;
    if (residual_correction.type === ResidualCorrectionType.Collocation) {
        let collocation = residual_correction.collocation;
        generate_covariance_plot(collocation.covariance);
    }
    if (residual_correction.type != ResidualCorrectionType.NoCorrection) {
        const residual_correction_name = residual_correction_names[residual_correction.type];
        if ("validation_statistics" in residual_correction) {
            $("#output_statistics").append(
                generate_statistics_table(`Στατιστικά υπολοίπων Validation με ${residual_correction_name}`, residual_correction.validation_statistics)
            );
        }
    }

    $('.results-block').show();
}

$('#form_input').submit(function(event) {
    event.preventDefault();
    clear_results_block();

    var fd = new FormData($(this)[0]);
    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: fd,
        dataType: "json",
        processData: false,
        contentType: false,
    }).done(function (json_output){
        fill_results_block(json_output);

        $('#id_btn_results_save').attr('disabled', true);
        idb_set('procrustes_latest_results', json_output)
        .then(() => {
            $('#id_btn_results_save').removeAttr('disabled');
        });
    });
});

$('#id_btn_results_save').on('click', () => {
    idb_get('procrustes_latest_results')
    .then((val) => {
        idb_set('procrustes_saved_results', val);
    });
});

$('#id_btn_results_clear').on('click', () => {
    idb_clear();
    clear_results_block();
});

// change visibility of covariance function type
$('#id_residual_correction_type').change(function() {
    const COLLOCATION_ID = 1;
    if (this.value == COLLOCATION_ID) {
        $('#id_cov_function_type').parent().show(ANIM_TIME);
        $('#id_collocation_noise').parent().show(ANIM_TIME);
    } else {
        $('#id_cov_function_type').parent().hide(ANIM_TIME);
        $('#id_collocation_noise').parent().hide(ANIM_TIME);
    }
});

function update_points_on_map() {

    let map = $('#map').data('map');
    map.clear();

    const file = $(`#id_reference_points`).prop('files')[0];

    Papa.parse(file, {
        delimitersToGuess: [' ', '\t', ',', ';'],
        skipEmptyLines: 'greedy',
        complete: function(results) {
            let coords = results.data.map(function (line) {
                // remove empty entries
                let entries = line.filter(function (entry) { return /\S/.test(entry); });
                if (entries.length != 6) {
                    throw Error("CSV format is invalid")
                }
                return {
                    id: entries[0],
                    is_ref: entries[1] == 'R',
                    x_src: parseFloat(entries[2]),
                    y_src: parseFloat(entries[3]),
                    x_dst: parseFloat(entries[4]),
                    y_dst: parseFloat(entries[5]),
                }
            });
            // now we got coordinates like this
            // [{id, is_ref, x0, y0, x'0, y'0}, {id, is_ref, x1, y1, x'1, y'1}, ...]
            // try to guess which set if any set is in ggrs87
            const source_coords = coords.map(e => { return [e.x_src, e.y_src]; });
            const target_coords = coords.map(e => { return [e.x_dst, e.y_dst]; });
            const source_is_ggrs87 = map.check_if_ggrs87_pointset(source_coords);
            const target_is_ggrs87 = map.check_if_ggrs87_pointset(target_coords);
            const use_ggrs87 = source_is_ggrs87 || target_is_ggrs87;
            // check if at least one of the input points are in ggrs87
            // so we can use a background tiled map
            if (use_ggrs87) {
                map.add_background_tiles();
            } else {
                // in case we do not get ggrs87 data use the src coords and
                // a local coordinate system based on them
                const centroid_x = coords.reduce((accum, xy) => accum + xy.x_src, 0.0) / coords.length;
                const centroid_y = coords.reduce((accum, xy) => accum + xy.y_src, 0.0) / coords.length;
                coords.forEach(xy => {
                    xy.x_src -= centroid_x;
                    xy.y_src -= centroid_y;
                });
            }

            const ref_coords = coords
                .filter(e => { return e.is_ref; })
                .map(e => { return target_is_ggrs87 ? [e.x_dst, e.y_dst] : [e.x_src, e.y_src]; })
            const val_coords = coords
                .filter(e => { return !e.is_ref; })
                .map(e => { return target_is_ggrs87 ? [e.x_dst, e.y_dst] : [e.x_src, e.y_src]; })
            map.add_points(
                PROCRUSTES_MAP_LAYERS.REFERENCE_POINTS,
                ref_coords,
                use_ggrs87
            );
            map.add_points(
                PROCRUSTES_MAP_LAYERS.VALIDATION_POINTS,
                val_coords,
                use_ggrs87
            );
        }
    });
}

$('#id_reference_points').change(function() {
    update_points_on_map();
});

// main
$(function() {
    // initial state
    $('#id_cov_function_type').parent().hide(); 
    $('#id_collocation_noise').parent().hide();

    let map = new ProcrustesMap();
    $('#map').data('map', map);

    generate_input_example_table();

    if ($('#id_reference_points')[0].files.length == 1) {
        update_points_on_map();
    }
});

