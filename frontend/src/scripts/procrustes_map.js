// ol modules
import 'ol/ol.css';
import { Map, View, Feature } from 'ol';
import {
    Vector as VectorSource,
    OSM as OSMSource
} from 'ol/source';
import {
    Vector as VectorLayer,
    Tile as TileLayer,
} from 'ol/layer';
import { Circle, Style, Stroke, Fill } from 'ol/style';
import * as Extent from 'ol/extent';
import { Point } from 'ol/geom';
import {
    get as proj_get,
    transform as proj_transform,
} from  'ol/proj';
import { register as proj_register } from  'ol/proj/proj4';
import { defaults as interaction_get_defaults } from 'ol/interaction';
import { fromExtent as poly_from_extent } from 'ol/geom/Polygon';

// CDN lib modules
import proj4 from 'proj4';

// constants
const FILL_TRANSPARENT = new Fill({
    color: 'rgba(255,255,255,0.4)',
});

const STROKE_BLUE = new Stroke({
    color: '#3399CC',
    width: 4,
});

const STROKE_PURPLE = new Stroke({
    color: '#cc3399',
    width: 4,
});

const REFERENCE_POINT_STYLE = new Style({
    image: new Circle({
        fill: FILL_TRANSPARENT,
        stroke: STROKE_BLUE,
        radius: 7,
    }),
    fill: FILL_TRANSPARENT,
    stroke: STROKE_BLUE,
});

const VALIDATION_POINT_STYLE = new Style({
    image: new Circle({
        fill: FILL_TRANSPARENT,
        stroke: STROKE_PURPLE,
        radius: 7,
    }),
    fill: FILL_TRANSPARENT,
    stroke: STROKE_PURPLE,
});

export const PROCRUSTES_MAP_LAYERS = {
    REFERENCE_POINTS: {
        style: REFERENCE_POINT_STYLE,
        name: 'reference_points',
    },
    VALIDATION_POINTS: {
        style: VALIDATION_POINT_STYLE,
        name: 'validation_points',
    },
};

export class ProcrustesMap
{
    #map;

    constructor() {
        proj4.defs(
            "EPSG:2100",
            "+proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80\
            +towgs84=-199.87,74.79,246.62,0,0,0,0 +units=m +no_defs"
        );
        proj_register(proj4);

        let view = new View({
            projection: 'EPSG:3857', //spherical merc
            center: proj_transform([25,38.4],'EPSG:4326','EPSG:3857'),
            zoom: 6,
        });
        let default_interactions_list = interaction_get_defaults({
            altShiftDragRotate:false,
            pinchRotate:false
        });

        let map = new Map({
            target: "map",
            view: view,
            interactions: default_interactions_list,
        });

        this.#map = map;
    }

    #remove_all_layers_from_map() {
        this.#map.setLayers([]);
    }

    #remove_layer_from_map(name) {
        let layers_to_remove = [];
        this.#map.getLayers().forEach(layer => {
            if (layer.get('name') === name) {
                layers_to_remove.push(layer);
            }
        });
        layers_to_remove.forEach(layer => {
            this.#map.removeLayer(layer);
        });
    }

    #zoom_in_to_point_extents() {
        let extent = Extent.createEmpty();
        this.#map.getLayers().forEach(layer => {
            const source = layer.getSource();
            if (source instanceof VectorSource) {
                Extent.extend(extent, source.getExtent());
            }
        });
        let zoom_extent = poly_from_extent(extent);
        zoom_extent.scale(1.2);
        this.#map.getView().fit(zoom_extent);
    }

    check_if_ggrs87_pointset(coords) {
        // bounds found in: https://epsg.io/2100
        const ggrs84_lower = [94874.71, 3859448.36];
        const ggrs84_upper = [892934.13, 4631226.44];
        const ggrs84_bounds = Extent.boundingExtent([ggrs84_lower, ggrs84_upper]);
        const is_ggrs87 = coords.every(p => {
            return Extent.containsCoordinate(ggrs84_bounds, p);
        });
        return is_ggrs87;
    }

    clear() {
        this.#remove_all_layers_from_map()
    }

    add_background_tiles() {
        const osm_layer = new TileLayer({
            source: new OSMSource()
        });
        this.#map.addLayer(osm_layer);
    }

    add_points(layer, coords, local_crs) {
        if (coords.length == 0)
            return;

        if (local_crs === undefined) {
            coords.forEach(xy => {
                xy[0] -= local_crs[0];
                xy[1] -= local_crs[1];
            });
        }

        const proj_from = local_crs === undefined ?
            proj_get('EPSG:3857') :
            proj_get('EPSG:2100');
        const proj_to = proj_get('EPSG:3857');

        const features = coords.map(xy => {
            xy = proj_transform(xy, proj_from, proj_to);
            return new Feature({
                geometry: new Point(xy),
            });
        });
        const vector_source = new VectorSource({
            features: features,
        });
        const vector_layer = new VectorLayer({
            name: layer.name,
            source: vector_source,
            style: layer.style,
        });
        this.#map.addLayer(vector_layer);
        this.#zoom_in_to_point_extents();
    }

}


