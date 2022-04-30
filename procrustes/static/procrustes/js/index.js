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
        title: "Covariance Function",
        xaxis: { title: "Distance (km)" },
        yaxis: { title: "Covariance (cm<sup>2</sup>)" },
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
            if ("validation_statistics" in collocation) {
                $("#output_transformation_params").append(
                    generate_statistics_table(`Collocation Validation Statistics`, collocation.validation_statistics)
                );
            }
        }
    }).fail(function (jqXHR) {
    });

});
