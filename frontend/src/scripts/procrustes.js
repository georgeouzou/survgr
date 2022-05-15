// ol modules
import 'ol/ol.css';
import {
    Map as olMap,
    View as olView,
    Feature as olFeature,
} from 'ol';
import {
    Vector as olVectorSource,
    OSM as olOSMSource
} from 'ol/source';
import {
    Vector as olVectorLayer,
    Tile as olTileLayer,
} from 'ol/layer';
import {
    Circle as olCircle,
    Style as olStyle,
    Stroke as olStroke,
    Fill as olFill
} from 'ol/style';
import * as olExtent from 'ol/extent';
import {
    Point as olPoint
} from 'ol/geom';
import {
    get as ol_proj_get,
    transform as ol_proj_transform,
} from  'ol/proj';
import { register as ol_proj_register } from  'ol/proj/proj4';
import { defaults as ol_get_interaction_defaults } from 'ol/interaction';
import { fromExtent as ol_poly_from_extent } from 'ol/geom/Polygon';

// CDN lib modules
import $ from 'jquery';
import Plotly from 'plotly.js-dist-min';
import proj4 from 'proj4';
import Papa from 'papaparse';

// local modules
import './mathjax_config.js';
import '../styles/procrustes.css';

// constants
const ANIM_TIME = 300;

const FILL_TRANSPARENT = new olFill({
    color: 'rgba(255,255,255,0.4)',
});

const STROKE_BLUE = new olStroke({
    color: '#3399CC',
    width: 4,
});

const STROKE_PURPLE = new olStroke({
    color: '#cc3399',
    width: 4,
});

const REFERENCE_POINT_STYLE = new olStyle({
    image: new olCircle({
        fill: FILL_TRANSPARENT,
        stroke: STROKE_BLUE,
        radius: 7,
    }),
    fill: FILL_TRANSPARENT,
    stroke: STROKE_BLUE,
});

const VALIDATION_POINT_STYLE = new olStyle({
    image: new olCircle({
        fill: FILL_TRANSPARENT,
        stroke: STROKE_PURPLE,
        radius: 7,
    }),
    fill: FILL_TRANSPARENT,
    stroke: STROKE_PURPLE,
});

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

function init_map() {
    const view = new olView({
        projection: 'EPSG:3857', //spherical merc
        center: ol_proj_transform([25,38.4],'EPSG:4326','EPSG:3857'),
        zoom: 6,
    });
    const default_interactions_list = ol_get_interaction_defaults({altShiftDragRotate:false, pinchRotate:false});

    let map = new olMap({
        layers:[
            new olTileLayer({
                source: new olOSMSource()
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

function zoom_in_to_point_extents(ol_map)
{
    let extent = olExtent.createEmpty();
    ol_map.getLayers().forEach(function(l) {
        const source = l.getSource();
        if (source instanceof olVectorSource) {
            olExtent.extend(extent, source.getExtent());
        }
    });
    let zoom_extent = ol_poly_from_extent(extent);
    zoom_extent.scale(1.2);
    ol_map.getView().fit(zoom_extent);
}

function update_points_on_map(layer_name, style) {

    let ol_map = $('#map').data('map');
    remove_layer_from_map(layer_name);

    const file = $(`#id_${layer_name}`).prop('files')[0];
    const format = $('#id_points_format input[type=radio]:checked').val();
    const contain_id = format === 'id,xs,ys,xt,yt';

    const proj_ggrs87 = ol_proj_get('EPSG:2100');
    const proj_web = ol_proj_get('EPSG:3857');

    const ggrs84_lower = [94875.0, 3868409.0];
    const ggrs84_upper = [857398.0, 4630677.0];
    const ggrs84_bounds = olExtent.boundingExtent([ggrs84_lower, ggrs84_upper]);

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
            const source_is_ggrs87 = coords.every(function (p) {
                return olExtent.containsCoordinate(ggrs84_bounds, p.slice(0, 2));

            });
            const target_is_ggrs87 = coords.every(function (p) {
                return olExtent.containsCoordinate(ggrs84_bounds, p.slice(2, 4));
            });
            if (!source_is_ggrs87 && !target_is_ggrs87) return;

            const features = coords.map(function (c) {
                let xy = c.slice(source_is_ggrs87 ? 0 : 2, source_is_ggrs87 ? 2 : 4);
                xy = ol_proj_transform(xy, proj_ggrs87, proj_web);
                return new olFeature({
                    geometry: new olPoint(xy),
                });
            });
            const vector_source = new olVectorSource({
                features: features,
            });
            const vector_layer = new olVectorLayer({
                name: layer_name,
                source: vector_source,
                style: style,
            });
            ol_map.addLayer(vector_layer);

            zoom_in_to_point_extents(ol_map);
        }
    });

}

$('#id_reference_points').change(function() {
    update_points_on_map('reference_points', REFERENCE_POINT_STYLE);
});
$('#id_validation_points').change(function() {
    update_points_on_map('validation_points', VALIDATION_POINT_STYLE);
});

// main
$(document).ready(function() {
    $('#id_cov_function_type').hide(); // initial state
    init_map();
    proj4.defs("EPSG:2100","+proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=-199.87,74.79,246.62,0,0,0,0 +units=m +no_defs");
    ol_proj_register(proj4);

    if ($('#id_reference_points')[0].files.length == 1) {
        update_points_on_map('reference_points', REFERENCE_POINT_STYLE);
    }
    if ($('#id_validation_points')[0].files.length == 1) {
        update_points_on_map('validation_points', VALIDATION_POINT_STYLE);
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
