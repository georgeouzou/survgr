// ol modules
import 'ol/ol.css';
import { Map, View } from 'ol';
import { 
    Vector as VectorSource, 
    OSM as OSMSource 
} from 'ol/source';
import { 
    VectorImage as VectorImageLayer, 
    Vector as VectorLayer, 
    Tile as TileLayer
} from 'ol/layer';
import GeoJSON from 'ol/format/GeoJSON';
import { Style, Stroke, Fill, Text } from 'ol/style';
import { transform } from 'ol/proj';
import { Select, defaults as get_interaction_defaults, } from 'ol/interaction';
import { getCenter as extent_get_center } from 'ol/extent';

// CDN imports
import $ from 'jquery';

// hattblocks url
import HATTBLOCK_FEATURES_URL from '../assets/hattblocks.min.geojson';

// constants & globals
const NOT_SELECTED_ID = -1;

const GEOMETRY_STYLE = new Style({
    fill: new Fill({
        color: 'rgba(255, 255, 255, 0.6)',
    }),
    stroke: new Stroke({
        color: '#319FD3',
        width: 1,
    }),
});

const GEOMETRY_SELECTED_STYLE = new Style({
    fill: new Fill({
        color: 'rgba(255, 255, 255, 0.8)',
    }),
    stroke: new Stroke({
        color: '#319FD3',
        width: 3,
    }),
});

let LABEL_STYLE = new Style({
    text: new Text({
        font: '13px Calibri,sans-serif',
        fill: new Fill({
            color: '#000',
        }),
        overflow: true,
    }),
});

let FEATURE_STYLE = [GEOMETRY_STYLE, LABEL_STYLE];
let FEATURE_SELECTED_STYLE = [GEOMETRY_SELECTED_STYLE, LABEL_STYLE];

export function init_map() {
    // Map initialization.
    // Uses a single map instance enabling the user to select graphically 
    // the hatt block of choice. The map is contained within a modal and 
    // the modal is related/bound on the show event to the calling html 
    // container class "hatt-selection"

    // this is the geojson source used in the map
    let hattblocks = new VectorSource({
        url: HATTBLOCK_FEATURES_URL,
        format: new GeoJSON({
            dataProjection: 'EPSG:4326'
        }),
    });
    let view = new View({
        projection: 'EPSG:3857', // spherical merc 
        center: transform([25.0,38.4],'EPSG:4326','EPSG:3857'),
        zoom: 6,
        maxZoom: 10
    });

    let only_blocks_layer = new VectorImageLayer({
        source: hattblocks,
        maxZoom: 7,
    });

    let detailed_blocks_layer = new VectorLayer({
        source: hattblocks,
        minZoom: 7,
        declutter: true,
        style: function (feature, resolution) {
            LABEL_STYLE
                .getText()
                .setText(get_hattblock_label(feature, resolution));
            return FEATURE_STYLE;
        },
    });

    let default_interactions_list = get_interaction_defaults({altShiftDragRotate:false, pinchRotate:false});

    let map = new Map({
        layers:[
            new TileLayer({
                source: new OSMSource()
            }),
            only_blocks_layer,
            detailed_blocks_layer,
        ],
        target: "map",
        view: view,
        interactions: default_interactions_list,
    });

    let select_action = new Select({
        style: function (feature, resolution) {
            LABEL_STYLE 
                .getText()
                .setText(get_hattblock_label(feature, resolution));
            return FEATURE_SELECTED_STYLE;
        }
    });
    
    map.addInteraction(select_action);
    // on select feature
    select_action.getFeatures().on('add', (e) => {
        let feature = e.element;
        let name = feature.get('name');
        $('#selected-feature-name').html('Επιλογή φύλλου χάρτη: ' + name);
    });
    // on unselect feature
    select_action.getFeatures().on('remove', () => {
        $('#selected-feature-name').html('Επιλογή φύλλου χάρτη: ');
    });

    // Modal events
    var bound_hatt;

    $('#map-modal').on('show.bs.modal', (e) => {
        // get the related hatt container element and store it to the modal instance
        bound_hatt = $(e.relatedTarget).parents('.hatt-selection');
        // clear previous selected feature if exists
        let selected_features = select_action.getFeatures();
        selected_features.clear();
        // and select again based on related id value
        let id = parseInt(bound_hatt.find('.hatt-id').val());  
        if (id != NOT_SELECTED_ID){
            if (hattblocks.getFeatures().length == 0){
                // CAUTION: the source might not have loaded the features the first time we open the map so...
                hattblocks.on('featuresloadend', () => {
                    selected_features.push(hattblocks.getFeatureById(id));
                });
            } else {
                selected_features.push(hattblocks.getFeatureById(id));       
            }
        }
    });

    $('#map-modal').on('shown.bs.modal', () => {
        // this is needed because i use the map inside of a modal
        map.updateSize();
        // pan view to the selected feature
        if (select_action.getFeatures().getLength() > 0){
            // get xmin, ymin, xmax, ymax of selected feature
            let center = extent_get_center(select_action.getFeatures().item(0).getGeometry().getExtent());
            view.animate({
                center: center
            });
        } 
    });

    $('#map-modal').on('hide.bs.modal', () => {
        // update the selected hatt name and hatt id elements
        if (select_action.getFeatures().getLength() > 0){
            let selected_feature = select_action.getFeatures().pop();
            bound_hatt.find('.hatt-id').val(selected_feature.getId());
            bound_hatt.find('.hatt-name').typeahead('val', selected_feature.get('name'));
        } else {
            bound_hatt.find('.hatt-id').val(NOT_SELECTED_ID);
            bound_hatt.find('.hatt-name').typeahead('val', '');
        }
    });
}

// Utility

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

function get_hattblock_label(feature, resolution) {
    let name = feature.get('name');
    let okxe_id = feature.get('okxe_id');

    if (resolution > 400) {
        return [`#${okxe_id}`, ''];
    }

    let phi = feature.get('cy');
    let lambda = feature.get('cx');
    let [sign_phi, d_phi, m_phi, ] = decdeg2dms(phi);
    let [sign_lambda, d_lambda, m_lambda, ] = decdeg2dms(lambda);


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
