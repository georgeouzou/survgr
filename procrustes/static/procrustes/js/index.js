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
        /*
        intervals = json_output.output.intervals;
        empirical_covs = json_output.output.empirical_covs;
        fitted_covs = json_output.output.fitted_covs;

        let data = [
            {
                x: intervals,
                y: empirical_covs,
                mode: "lines+markers",
                type: "scatter",
                name: "empirical",
            },
            {
                x: intervals,
                y: fitted_covs,
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
        $("#output_transformation_params").append(generateReferenceCoordinateTable(json_output));
        */
        console.log(json_output);
        transformation = json_output.transformation;
        $("#output_transformation_params").append(
            `<table class='table'>
                <thead>
                    <tr>
                        <th>${transformation.type} Transformation Statistics</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Min: ${transformation.statistics.min}</td>
                    </tr>
                    <tr>
                        <td>Max: ${transformation.statistics.max}</td>
                    </tr>
                    <tr>
                        <td>Mean: ${transformation.statistics.mean}</td>
                    </tr>
                    <tr>
                        <td>Std: ${transformation.statistics.std}</td>
                    </tr>
                </tbody>
             </table>
             `
        );
        if ("validation" in json_output) {
            validation = json_output.validation
            $("#output_transformation_params").append(
                `<table class='table'>
                    <thead>
                        <tr>
                            <th>Validation Statistics</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Min: ${validation.statistics.min}</td>
                        </tr>
                        <tr>
                            <td>Max: ${validation.statistics.max}</td>
                        </tr>
                        <tr>
                            <td>Mean: ${validation.statistics.mean}</td>
                        </tr>
                        <tr>
                            <td>Std: ${validation.statistics.std}</td>
                        </tr>
                    </tbody>
                 </table>
                 `
            );
        }
    }).fail(function (jqXHR) {
    });

});
