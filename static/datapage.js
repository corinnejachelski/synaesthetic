"use strict";

// Circle pack d3 chart
// rendering chart with data from AJAX request
// data is manipulated from Spotify API call
 $.get('/api/artists', (response) => {
    console.log(response); 

  const packLayout = d3.pack()
  .size([800, 800])
  //space between hierarchy circles
  .padding(5)

//returns an object with data structure that represents hierarchy
const rootNode = d3.hierarchy(response) 

// call .sum() on the hierarchy object root before applying the pack layout
// This traverses the hierarchy and sets .value on each node to the sum of its children
rootNode.sum(function(d) {
  return d.value;
});

//pack layout adds x, y and r (for radius) properties to each node
packLayout(rootNode);

const svg = d3.select('svg')
.style("cursor", "pointer")

const nodes = d3.select('svg g')
  .selectAll('g')
  .data(rootNode.descendants()) //returns an array of descendants  
  .enter()
  .append('g')
  .attr('transform', function(d) {return 'translate(' + [d.x, d.y] + ')'});

nodes.append('circle')
  .attr('r', function(d) { return d.r; })
  // .attr("pointer-events", d => !d.children ? "none" : null)
  // .on("mouseover", function() { d3.select(this).attr("stroke", "#000"); })
  // .on("mouseout", function() { d3.select(this).attr("stroke", null); })


  nodes.append('text')
  .attr('dy', 10)
  .attr('dx', -20)
  // .text(function(d) { return d.children === undefined ? d.data.name : '';}) 
  .text(function(d) { return d.data.name }) 
      .attr("font-family", "sans-serif")
      .attr("font-size", "12px")
      .attr("fill", "black")
      .attr("text-anchor", "middle");

 });




 // Get a random song button
 $('#random-song').on('click', (evt) => {
    evt.preventDefault();

    $.get('/api/audio', (resonse))
 })

// Charts.js radar chart

$.get('/api/audio', (response) => {
    console.log(response);
    console.log(response.random_song)

    const data = {
    labels: ['Danceability', 'Energy', 'Speechiness', 'Acousticness', 
    'Instrulmentalness', 'Liveness', 'Valence'],
      datasets: [
        {
          label: 'Average',
          fill: true,
          backgroundColor: "rgba(255,99,132,0.2)",
          borderColor: "rgba(255,99,132,1)",
          pointBorderColor: "#fff",
          pointBackgroundColor: "rgba(255,99,132,1)",
          pointBorderColor: "#fff",
          data: response.avg
        },
        {
          label: response.track_name + ' - ' + response.artist_name,
          fill: true,
          backgroundColor: "rgba(179,181,198,0.2)",
          borderColor: "rgba(179,181,198,1)",
          pointBorderColor: "#fff",
          pointBackgroundColor: "rgba(179,181,198,1)",
          data: response.random_song
        }
      ]
    }


    const radarChart = new Chart(
        $('#radar-chart'), 
        {
        type: 'radar',
        data: data,
        options: {
          scale: {
            ticks: {
              beginAtZero: true,
              min: 0,
              max: 1,
              stepSize: 0.1
            } 
          },
          // legend: {
          //       position: 'left'
          // }
        }
    }); 
    
});

          
        

