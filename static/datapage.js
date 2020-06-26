"use strict";

// Circle pack d3 chart
// rendering chart with data from AJAX request
// data is manipulated from Spotify API call
$.get('/api/artists', (response) => {
  circlePack(response, '#circle-pack-svg');
 });

//load nested genres zoomable circle pack on page load
 $.get('/api/nested-genres', (response) => {
   zoomableCirclePack(response, '#nested-genres');
 });

 //re-render circle pack chart based on user click for top artists time range
 $('#time-range').on('submit', (evt) => {
  evt.preventDefault();

  const userSelection = {'time_range': $('#artists-time-range').val()};

  $.post('/api/artists/time-range', userSelection, (response) => {
    $('#circle-pack-svg').empty();
    $('#circle-pack-svg').html('Updating.....')
    circlePack(response, '#circle-pack-svg');
  });
 });

 //re-render circle pack chart based on user click for playlist
 $('#playlist').on('submit', (evt) => {
   evt.preventDefault();

   const playlistSelection = {'playlist': $('#playlist-selection').val()}

  $.post('/api/playlist', playlistSelection, (response) => {
    $('#circle-pack-svg').empty();
    circlePack(response, '#circle-pack-svg');
  });
 });
 
/////////////////////////////////////////////////////////////////////////////////////////////////////////
 //All genres button toggle

$('#genres').on('click', () => {
  $.get('/api/genres', (response) => {
      for (const genre in response) {

        // re-set for each iteration
        let artists = "";

        for (const index in response[genre]) {
          const artist = response[genre][index];

          //do not want commas if only 1 item of if last item
          if (response[genre].length === 1 || index == (response[genre].length - 1)) {
            artists += artist;
          } else {
            artists += artist + ', ';
          } 
        }
        $('#list-group').append('<li class="list-group-item">', genre, ": ", artists, '</li>');
      }
});
});

///////////////////////////////////////////////////////////////////////////////////////////
//Viz.js network chart 
$.get('/api/related-artists', (response) => { 
  networkChart(response, 'network-chart');
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
            label: 'Your Average',
            fill: true,
            backgroundColor: "rgba(179,181,198,0.2)",
            borderColor: "rgba(179,181,198,1)",
            pointBorderColor: "#fff",
            pointBackgroundColor: "rgba(179,181,198,1)",
            data: []
            },
            {
            label: '',
            fill: true,
            backgroundColor: "rgba(255,99,132,0.2)",
            borderColor: "rgba(255,99,132,1)",
            pointBorderColor: "#fff",
            pointBackgroundColor: "rgba(255,99,132,1)",
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
////////////////////////////////////////////////////////////////////////////////////////

function circlePack(response, svgID) {
const packLayout = d3.pack()
.size([700, 700])
//space between circles
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

const svg = d3.select(svgID)
.style("cursor", "pointer")

const nodes = d3.select(svgID)
.selectAll('g')
.data(rootNode.descendants()) //returns an array of descendants  
.enter()
.append('g')
.attr('transform', function(d) {return 'translate(' + [d.x, d.y] + ')'});

const color = d3.scaleSequential(d3.interpolateCool).domain([-10,10]);  

nodes.append('circle')
.attr('r', function(d) { return d.r; })
.style("fill", function(d) { return color(d.depth); });

const leaf = nodes.filter(d => !d.children);

leaf.attr("class", "leaf")
.append("clipPath")
.attr("id", function(d) { return "clip-" + d.id; })

//artist labels
leaf.append("text")
  .attr("clip-path", d => d.clipUid)
.selectAll("tspan")
.data(d => d.data.name.split(/(?=[A-Z][a-z])|\s+/g))
.join("tspan")
  .attr("x", 0)
  .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 0.8}em`)
  .text(d => d)
    .attr("font-family", "sans-serif")
    .attr("font-size", "12px")
    .attr("fill", "black")
    .attr("text-anchor", "middle");

const genres = nodes.filter(d => d.children !== undefined);

// const startAngle = Math.PI * 0.1;
// const labelArc = d3.arc()
//         .innerRadius(function(d) { return (d.r - 5); })
//         .outerRadius(function(d) { return (d.r + 10); })
//         .startAngle(startAngle)
//         .endAngle(function(d) {
//           const total = d.data.name.length;
//           const step = charSize / d.r;
//           return startAngle + (total * step);
//         });

// const groupLabels = nodes.selectAll()
//       .enter()
//         .append("g")
//         .attr("class", "group")
//         .attr("transform", function(d) { return `translate(${d.x},${d.y})`; });

// groupLabels
// .append("path")
//   .attr("class", "group-arc")
//   .attr("id", function(d,i) { return `arc${i}`; })
//   .attr("d", labelArc);

// groupLabels
// .append("text")
//   .attr("class", "group-label")
//   .attr("x", 5) 
//   .attr("dy", 7) 
// .append("textPath")
//   .attr("xlink:href", function(d,i){ return `#arc${i}`;})
//   .text(function(d) { return d.data.name ;});

// genres.append('text')
//   .attr('dy', 5)
//   .attr('dx', 7)
//   //.text(function(d) { return d.children === undefined ? '' : d.data.name;}) 
//   .text(function(d) { return d.data.name }) 
//       .attr("font-family", "sans-serif")
//       .attr("font-size", "12px")
//       .attr("fill", "black")
//       .attr("text-anchor", "end")
//       .attr("text-align", "left");

genres.append("title")
    // .text(d => `${d.ancestors().map(d => d.data.name)}`);
    .text(d => d.data.name);
};

function zoomableCirclePack(data, svgID) {


  var svg = d3.select(svgID),
      margin = 20,
      diameter = +svg.attr("width"),
      g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
  
  var color = d3.scaleLinear()
      .domain([-1, 5])
      .range(["hsl(147,80%,80%)", "hsl(228,30%,40%)"])
      .interpolate(d3.interpolateHcl);
  
  var pack = d3.pack()
      .size([diameter - margin, diameter - margin])
      .padding(2);
  
    const root = d3.hierarchy(data)
        .sum(function(d) { return d.value; })
        .sort(function(a, b) { return b.value - a.value; });
  
    var focus = root,
        nodes = pack(root).descendants(),
        view;
  
    var circle = g.selectAll("circle")
      .data(nodes)
      .enter().append("circle")
        .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
        .style("fill", function(d) { return d.children ? color(d.depth) : null; })
        .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); });
  
    var text = g.selectAll("text")
      .data(nodes)
      .enter().append("text")
        .attr("class", "label")
        .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
        .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
        .text(function(d) { return d.data.name; });
  
    var node = g.selectAll("circle,text");
  
    svg
        .style("background", color(-1))
        .on("click", function() { zoom(root); });
  
    zoomTo([root.x, root.y, root.r * 2 + margin]);
  
    function zoom(d) {
      var focus0 = focus; focus = d;
  
      var transition = d3.transition()
          .duration(d3.event.altKey ? 7500 : 750)
          .tween("zoom", function(d) {
            var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
            return function(t) { zoomTo(i(t)); };
          });
  
      transition.selectAll("text")
        .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
          .style("fill-opacity", function(d) { return d.parent === focus ? 1 : 0; })
          .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
          .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });
    }
  
    function zoomTo(v) {
      var k = diameter / v[2]; view = v;
      node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
      circle.attr("r", function(d) { return d.r * k; });
    };
  };  
/////////////////////////////////////////////////////////////////////////////////////////
function networkChart(response, divID) {
    // create an array with nodes
    const nodes = response.nodes;

    // create an array with edges
    const edges = response.edges;

    // create a network
    const container = document.getElementById(divID);
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
};