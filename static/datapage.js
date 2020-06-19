"use strict";

// Circle pack d3 chart
// rendering chart with data from AJAX request
// data is manipulated from Spotify API call
 $.get('/api/artists', (response) => {

  const packLayout = d3.pack()
  .size([700, 700])
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
  .append('text')
  .text(function(d) { return d.data.name; })
    .attr("font-family", "sans-serif")
    .attr("font-size", "16px")
    .attr("fill", "blue")
    .attr("text-anchor", "middle");
  // .attr("pointer-events", d => !d.children ? "none" : null)
  // .on("mouseover", function() { d3.select(this).attr("stroke", "#000"); })
  // .on("mouseout", function() { d3.select(this).attr("stroke", null); })


nodes.append('text')
  .attr('dy', 10)
  .attr('dx', 0)
  .text(function(d) { return d.children === undefined ? d.data.name : '';}) 
  // .text(function(d) { return d.data.name }) 
      .attr("font-family", "sans-serif")
      .attr("font-size", "12px")
      .attr("fill", "black")
      .attr("text-anchor", "middle");

 });
/////////////////////////////////////////////////////////////////////////////////////////////////////////
 //All genres button toggle

 $('#genres').on('click', () => {
    $.get('/api/genres', (response) => {
      console.log(response.data);
        for (const item in response.data) {
          $('#list-group').append('<li class="list-group-item">', item, ": ", response.data[item], '</li>');
        }
  });
 });

  ///////////////////////////////////////////////////////////////////////////////////////////
  //Viz.js network chart 


    $.get('/api/related-artists', (response) => { 
    // create an array with nodes
    const nodes = response.nodes;

    // create an array with edges
    const edges = response.edges;

    // create a network
    const container = document.getElementById('network-chart');
    const data= {
      nodes: nodes,
      edges: edges,
    };
    const options = {
      interaction:{
        hover:true,
        hoverConnectedEdges:true,
        dragNodes:true,
        selectConnectedEdges:true,
        selectable:true,
      },
      nodes: {
          size:90,
          borderWidth: 1,
          borderWidthSelected: 6,
          color: {
            border: '#000000',
            highlight: {border: '#00CDCD'},
            hover: {border: '#00CDCD'},
          },
          font:{color:'#000000', "size": 40},
      },
      edges: {
        color:{
          color:'#000000',
          highlight: '#00CDCD',
          hover: '#00CDCD',
        },
        hoverWidth: 8,
        width: 3,
        selectionWidth: 6
      },
      physics: {
        barnesHut: {
          //avoidOverlap: 1,
          centralGravity: 0.1,
          gravitationalConstant: -3000,
          springLength: 400,
        },
        repulsion:{
          nodeDistance: 1200,
        },
      },
      // configure: {
      //   enabled: true,
      //   filter: 'physics, layout',
      //   showButton: true
      // },
      // tooltip: {
      //   fontColor: "black",
      //   fontSize: 14, // px
      //   fontFace: "verdana",
      //   color: {
      //     border: "#666",
      //     background: "#FFFFC6"
      //   }
      // },
      width: '700px',
      height: '700px'
    };
    const network = new vis.Network(container, data, options);

//bolds label and highlghts node border on click
    network.on("click", function (params) {
        params.event = "[original event]";
    });

//changes font size, node size, and border width when hovering over node 
    network.on("hoverNode", function (params) {
      const nodeId = params.node;
      const node = network.body.nodes[nodeId];
      node.setOptions({
        size: 100,
        font: {
          size: 70
        },
        borderWidth: 4
      });
    });

//reset node on hover out
    network.on("blurNode", function (params) {
      const nodeId = params.node;
      const node = network.body.nodes[nodeId];
      node.setOptions({
        size: options.nodes.size,
        font: {
          size: options.nodes.font.size
        },
        borderWidth: options.nodes.borderWidth
      });
    });

});

///////////////////////////////////////////////////////////////////////////////////////////////////////
 //Charts.js radar chart config
 const config = {
  type: 'radar',
  data: {
        labels: ['Danceability', 'Energy', 'Speechiness', 'Acousticness', 
        'Instrulmentalness', 'Liveness', 'Valence'],
        //data is instantiated as empty list and is updated with API response when chart renders
        datasets: [
            {
            label: 'Average',
            fill: true,
            backgroundColor: "rgba(255,99,132,0.2)",
            borderColor: "rgba(255,99,132,1)",
            pointBorderColor: "#fff",
            pointBackgroundColor: "rgba(255,99,132,1)",
            pointBorderColor: "#fff",
            data: []
            },
            {
            label: '',
            fill: true,
            backgroundColor: "rgba(179,181,198,0.2)",
            borderColor: "rgba(179,181,198,1)",
            pointBorderColor: "#fff",
            pointBackgroundColor: "rgba(179,181,198,1)",
            data: []
            }
        ]
        },
    options: {
        scale: {
            ticks: {
              beginAtZero: true,
              min: 0,
              max: 1,
              stepSize: 0.1
            },
            scaleLabel: {
              fontSize: 20,
            },
          // legend: {
          //       position: 'left'
          // }
        }
     } 
  };

window.onload = function() {
  //AJAX request to API, update data to response in chart
  $.get('/api/audio', (response) => {
      window.myRadar = new Chart(document.getElementById('radar-chart'), config);
      config.data.datasets[0].data = response.avg;
      config.data.datasets[1].data = response.random_song;
      config.data.datasets[1].label = response.track_name + ' - ' + response.artist_name
      window.myRadar.update();

  }
)
};
    
///////////////////////////////////////////////////////////////////////////////////////////////////    
// Get a random song button
$('#random-song').on('click', () => {
    $.get('/api/random-song', (response) => {

        //remove last dataset in list, add 1 new item
        //chart has issues with previous random song remaining in unexpected ways if you don't do this
        config.data.datasets.splice(-1, 1);

        //create new dataset with new random song
        var randomSong = {
            label: response.track_name + ' - ' + response.artist_name,
            fill: true,
            backgroundColor: "rgba(179,181,198,0.2)",
            borderColor: "rgba(179,181,198,1)",
            pointBorderColor: "#fff",
            pointBackgroundColor: "rgba(179,181,198,1)",
            data: response.random_song
        };

        config.data.datasets.push(randomSong);

        window.myRadar.update();
    }  
)});