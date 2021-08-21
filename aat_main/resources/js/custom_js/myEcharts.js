$(document).ready(function () {
    let yourPieChart = echarts.init(document.getElementById("yourPieChart"));
    let yourPieChartOption = {
        title: {
            text: 'yourPieChartTitle'
        },
        series: [
            {
                type: 'pie',
                radius: '75%',
                data: [
                    {value: 50, name: 'satisfied'},
                    {value: 20, name: 'fair'},
                    {value: 30, name: 'dissatisfied'}
                ]
            }
        ]
    };
    yourPieChart.setOption(yourPieChartOption);
})