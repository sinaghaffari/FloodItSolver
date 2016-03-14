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
d3.json("/static/uniform_cost.json", function(json) {
    var force = d3.layout.force()
        //.charge(-100)
        //.linkDistance(50)
        .nodes(json.nodes)
        .links(json.links)
        .size([w, h])
        .start();

    var link = vis.selectAll("line.link")
        .data(json.links)
        .enter()
        .append("g")
        .attr("class", "link");


    var lines = link.append("svg:line")
        .style("stroke-width", function(d) {if (d['optimal']) return 3; else return 1})
        .style("stroke", "gray");

    var linktext = link.append("text")
        .attr("dx", 1)
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .text(function(d) {return d.move});

    var node = vis.selectAll("circle.node")
        .data(json.nodes)
        .enter()
        .append("g")
        .attr("class", "node")

        .call(force.drag);

    node.append("svg:circle")
        .attr("r", function(d) {if (d['start']) return 10; else return 5})
        .style("fill", function(d) {if (d['status'] == "open") return "red"; else if (d['start']) return "green"; else return "blue"});

    vis.style("opacity", 1e-6)
        .transition()
        .duration(1000)
        .style("opacity", 1);

    force.on("tick", function() {
        lines.attr("x1", function (d) {return d.source.x;})
            .attr("y1", function (d) {return d.source.y;})
            .attr("x2", function (d) {return d.target.x;})
            .attr("y2", function (d) {return d.target.y;});
        linktext.attr("transform", function(d) {return "translate(" + (d.source.x + d.target.x) / 2 + "," + (d.source.y + d.target.y) / 2 + ")";});
        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });
});