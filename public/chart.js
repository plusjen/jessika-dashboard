$(document).ready(function() {
    
    var data = {
	    labels : dataLabels,
	    
	    datasets : [
		    {
			    borderColor : "#67a9cf",
			    yAxisID: "y-axis-0",
			    label: "Conversations",
			    fill : false,
			    data : dataAxis0,
		    }, 
		    {
			    borderColor : "#878787",
			    yAxisID: "y-axis-1",
			    label: "Messages",
			    fill : false,
			    data : dataAxis1,
		    }
	    ]
    };
    var options = {
            responsive: true,
            maintainAspectRatio: true,
            legend: {
                display: false
             },
            scales: {
              yAxes: [{
                position: "left",
                "id": "y-axis-0",
                scaleLabel: {
                    display: true,
                    labelString: 'Ongoing Conversations', 
                    fontColor: "#67a9cf", 
                    fontSize: 16
                  },
                  gridLines: {
                    display: false,
                  },
                  ticks: {
                    fontColor: "#67a9cf", 
                  }
                  
              }, {
                position: "right",
                "id": "y-axis-1",
                scaleLabel: {
                    display: true,
                    labelString: 'Messages Sent and Received',
                    fontColor: "#878787", 
                    fontSize: 16
                  },
                ticks: {
                    fontColor: "#878787", 
                  }
              }]
            }
          };

    var context = document.getElementById('chart').getContext('2d');
    context.canvas.width = 900;
    context.canvas.height = 200;
    var lineChart = new Chart(context, {type: 'line', data: data, options: options});

})
