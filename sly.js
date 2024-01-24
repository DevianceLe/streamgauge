//Initialize the Html Elements
google.load('visualization', '1', { packages: ['corechart', 'controls'] });
var toast = 'wilp1.csv'; //Lol Placeholder
var streamTitle = ''; //Assing Stream

function drawVisualization() {
    var arrayData = 0; 
    var crt_ertdlyYY = 0;
    $.get(toast, function (csvString) {
        // transform the CSV string into a 2-dimensional array

        var arrayData = $.csv.toArrays(csvString, { onParseValue: $.csv.hooks.castToScalar });

        // this new DataTable object holds all the data
        var data = new google.visualization.arrayToDataTable(arrayData);
        // send it
        var crt_ertdlyYY = new google.visualization.ChartWrapper({
            chartType: 'LineChart',
            containerId: 'wat',
            dataTable: data,
            options: {
                height: 500,
                title: streamTitle,
                titleTextStyle: { color: 'Black', fontSize: 24 },
		legend: { position: 'bottom' },
		curveType: 'function',
		"vAxis" : {
			"title": "Stage FT"
			},
            }
        });
        crt_ertdlyYY.draw();
    });
}

function mystreamgauge(v1, v2) {
    toast = "urlgoeshere" + v1 + ".csv";
    streamTitle = v2;
    drawVisualization();
document.getElementById('wat').scrollIntoView();

}
