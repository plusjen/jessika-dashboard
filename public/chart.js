$(document).ready(function() {

    var chartHandler = function (jsonData) {
    
        var data = {
	        labels : jsonData['this month'].labels, //dataLabels,
	        datasets : [
		        {
			        borderColor : "#67a9cf",
			        yAxisID: "y-axis-0",
			        label: "Conversations",
			        fill : false,
			        data : jsonData['this month'].axis0, //dataAxis0,
		        }, 
		        {
			        borderColor : "#878787",
			        yAxisID: "y-axis-1",
			        label: "Messages",
			        fill : false,
			        data : jsonData['this month'].axis1, //dataAxis1,
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

        var dropdownItems = ['this week', 'last week', 'this month', 'last month', 'this quater', 'this year'];
        
        $.each(dropdownItems, function(ind, item) {
          $('#chart-dropdown').append( $('<li>').append( $('<a>').attr('href','#').append(item) ) );
        });
        
        $(".dropdown-menu li a").click(function(){
            var selText = $(this).text();
            $(this).parents('.dropdown').find('.dropdown-toggle').html(selText+' <span class="caret"></span>');
            // change chart
        });
    
    };
    
    $.getJSON(datafile, function(dataItems) {
        var jsonData = dataItems;
        chartHandler(dataItems);
        
    });
    

})
