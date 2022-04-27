function generateReferenceCoordinateTable(result) {

    let sourceCoords = result.input.cs_source.coords; // arrays with [x,y]
    let targetCoords = result.input.cs_target.coords;
    let transfCoords = result.output.cs_transformed.coords;

    let tableHead = document.createElement("thead");
    {
        let coordinateSystemsRow = document.createElement("tr");
        let coordsTypeRow = document.createElement("tr");
        ["Source", "Target", "Transformed"].forEach(function (desc) {
            let c = document.createElement("th");
            c.textContent = desc;
            $(c).attr("colspan", "2");
            $(coordinateSystemsRow).append(c);

            let x = document.createElement("th");
            let y = document.createElement("th");
            x.textContent = "X (m)";
            y.textContent = "Y (m)";
            $(coordsTypeRow).append([x, y]);
        });
        $(tableHead).append([coordinateSystemsRow, coordsTypeRow]);
    }

    let tableBody = document.createElement("tbody");
    if (sourceCoords.length == targetCoords.length && sourceCoords.length == transfCoords.length) {
        for (let i = 0; i < sourceCoords.length; ++i) {
            let source_x = document.createElement("td");
            let source_y = document.createElement("td");
            let target_x = document.createElement("td");
            let target_y = document.createElement("td");
            let transformed_x = document.createElement("td");
            let transformed_y = document.createElement("td");
            source_x.textContent = sourceCoords[i][0].toFixed(3);
            source_y.textContent = sourceCoords[i][1].toFixed(3);
            target_x.textContent = targetCoords[i][0].toFixed(3);
            target_y.textContent = targetCoords[i][1].toFixed(3);
            transformed_x.textContent = transfCoords[i][0].toFixed(3);
            transformed_y.textContent = transfCoords[i][1].toFixed(3);
            let bodyRow = document.createElement("tr");
            $(bodyRow).append([source_x, source_y, target_x, target_y, transformed_x, transformed_y]);
            $(tableBody).append(bodyRow);
        }
    }

    let table = document.createElement("table");
    table.appendChild(tableHead);
    table.appendChild(tableBody);
    $(table).addClass("table");
    $(table).addClass("table-striped");
    return table;
}

function generateStatisticsTable(name, statistics) {

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

function generateCovariancePlot(collocation_data) {
    let intervals = collocation_data.distance_intervals;
    let empiricalCov = collocation_data.empirical_cov;
    let fittedCov = collocation_data.fitted_cov;

    let data = [
        {
            x: intervals,
            y: empiricalCov,
            mode: "lines+markers",
            type: "scatter",
            name: "empirical",
        },
        {
            x: intervals,
            y: fittedCov,
            mode: "lines",
            type: "scatter",
            name: "sinc fitted",
        },
    ];

    let layout = {
        title: "Covariance Function",
        xaxis: { title: "Distance" },
        yaxis: { title: "Covariance" },
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
        generateCovariancePlot(json_output.collocation);
        //$("#output_transformation_params").append(generateReferenceCoordinateTable(json_output));
        transformation = json_output.transformation;
        $("#output_transformation_params").append(
            generateStatisticsTable(`${transformation.type} Transformation Statistics`, transformation.statistics)
        );
        if ("validation" in json_output) {
            validation = json_output.validation
            $("#output_transformation_params").append(
                generateStatisticsTable(`Validation Statistics`, validation.statistics)
            );
        }
    }).fail(function (jqXHR) {
    });

});
