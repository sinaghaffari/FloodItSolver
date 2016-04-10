/**
 * Created by sinag on 2016-03-11.
 */
var colord = {
    0: '#ff0000',
    1: '#00ff00',
    2: '#0000ff',
    3: '#ffff00',
    4: '#ff00ff',
    5: '#00ffff'
};

var vis = d3.select("#graph").append("svg");
var w = 1500,
    h = 900;

vis.attr("width", w).attr("height", h);
d3.json("/static/force.json", function(json) {
    var force = d3.layout.force()
        .charge(function() {return -400/(json.nodes.length * 0.05)})
        .linkDistance(function() {return 10})
        .nodes(json.nodes)
        .links(json.links)
        .size([w, h])
        .start();

    var link = vis.selectAll("line.link")
        .data(json.links)
        .enter().append("svg:line")
        .attr("class", "link")
        .style("stroke-width", function(d) {if (d['shortest']) return 3; else return 1})
        .style("stroke", function(d) {if (d['shortest']) return "black"; else return "black"});

    var node = vis.selectAll("circle.node")
        .data(json.nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(force.drag);

    var t = node.append("svg:circle")
        .attr("r", function(d) {if (d['root']) return 10; else return 5;})
        .style("fill", function(d) {return colord[d['color']]});

    node.append("text")
        .attr("dx", "-.35em")
        .attr("dy", ".35em")
        .text(function(d) {if (d['root']) return "U"; else return "";});

    vis.style("opacity", 1e-6)
        .transition()
        .duration(1000)
        .style("opacity", 1);

    force.on("tick", function() {
        link.attr("x1", function (d) {return d.source.x;})
            .attr("y1", function (d) {return d.source.y;})
            .attr("x2", function (d) {return d.target.x;})
            .attr("y2", function (d) {return d.target.y;});

        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });
});