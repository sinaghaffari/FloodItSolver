/**
 * Created by sinag on 2016-03-11.
 */
var colord = {
    0: 'rgba(255, 000, 000, 0.8',
    1: 'rgba(000, 255, 000, 0.8)',
    2: 'rgba(000, 000, 255, 0.8)',
    3: 'rgba(255, 255, 000, 0.8)',
    4: 'rgba(255, 000, 255, 0.8)',
    5: 'rgba(000, 255, 255, 0.8)'
};
var vis = d3.select("#graph").append("svg");
var w = 600,
    h = 500,
    r = 3;

vis.attr("width", w).attr("height", h);
d3.json("/static/a_star.json", function(json) {
    console.log(100/(json.nodes.length * 0.05));
    var force = d3.layout.force()
        .charge(function() {return -400/(json.nodes.length * 0.05)})
        .linkDistance(function() {return 100/(json.nodes.length * 0.05)})
        .nodes(json.nodes)
        .links(json.links)
        .size([w, h])
        .start();

    var link = vis.selectAll(".link")
        .data(json.links)
        .enter()
        .append("g")
        .attr("class", "link");


    var lines = link.append("svg:line")
        .style("stroke-width", function(d) {return d['optimal'] ? 5 : 2})
        .style("stroke", function(d) {return colord[d.move]});


    var node = vis.selectAll(".node")
        .data(json.nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(force.drag);

    var circles = node.append("svg:circle")
        .attr("r", r)
        .style("stroke", function(d) {return d['start'] ? "rgba(0, 0, 0, 1)" : "black"})
        .style("stroke-width", function(d) {return d['start'] ? 2 : 0})
        .style("fill", function(d) {if (d['status'] == "open") return "red"; else if (d['start']) return "green"; else return "blue"});

    force.on("tick", function() {
        node.attr("transform", function(d) { return "translate(" + (d.x = Math.max(r, Math.min(w - r, d.x))) + "," + (d.y = Math.max(r, Math.min(h - r, d.y))) + ")"; });
        lines.attr("x1", function (d) {return d.source.x;})
            .attr("y1", function (d) {return d.source.y;})
            .attr("x2", function (d) {return d.target.x;})
            .attr("y2", function (d) {return d.target.y;});
    });
});