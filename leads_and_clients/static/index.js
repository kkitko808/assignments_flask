$(document).ready (function () {
    var options = {
        title: {
            text: "Customers and number of new leads"
        },
        animationEnabled: true,
        data: [{
            type: "pie",
            startAngle: 40,
            toolTipContent: "<b>{label}</b>: {y}",
            showInLegend: "true",
            legendText: "{label}",
            indexLabelFontSize: 16,
            indexLabel: "{label} - {y}",
            dataPoints: [
                { y: 4, label: "Michael Choi" },
                { y: 3, label: "Joe Smith" },
                { y: 7, label: "Ryan Owen" },
                { y: 7, label: "Masaki Fujimoto" }
            ]
        }]
    };
    var chart = new CanvasJS.Chart("chartContainer", options)
    chart.render()
})