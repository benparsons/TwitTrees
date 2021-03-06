//
//  main.js
//
//  A project template for using arbor.js
//

(function($){

  var Renderer = function(canvas){
    var canvas = $(canvas).get(0)
    var ctx = canvas.getContext("2d");
    var particleSystem

    var that = {
      init:function(system){
        //
        // the particle system will call the init function once, right before the
        // first frame is to be drawn. it's a good place to set up the canvas and
        // to pass the canvas size to the particle system
        //
        // save a reference to the particle system for use in the .redraw() loop
        particleSystem = system

        // inform the system of the screen dimensions so it can map coords for us.
        // if the canvas is ever resized, screenSize should be called again with
        // the new dimensions
        particleSystem.screenSize(canvas.width, canvas.height) 
        particleSystem.screenPadding(80) // leave an extra 80px of whitespace per side
        
        // set up some event handlers to allow for node-dragging
        that.initMouseHandling()
      },
      
      redraw:function(){
        // 
        // redraw will be called repeatedly during the run whenever the node positions
        // change. the new positions for the nodes can be accessed by looking at the
        // .p attribute of a given node. however the p.x & p.y values are in the coordinates
        // of the particle system rather than the screen. you can either map them to
        // the screen yourself, or use the convenience iterators .eachNode (and .eachEdge)
        // which allow you to step through the actual node objects but also pass an
        // x,y point in the screen's coordinate system
        // 
        ctx.fillStyle = "white"
        ctx.fillRect(0,0, canvas.width, canvas.height)
        
        particleSystem.eachEdge(function(edge, pt1, pt2){
          // edge: {source:Node, target:Node, length:#, data:{}}
          // pt1:  {x:#, y:#}  source position in screen coords
          // pt2:  {x:#, y:#}  target position in screen coords

          // draw a line from pt1 to pt2
          ctx.strokeStyle = "rgba(0,0,0, .333)"
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(pt1.x, pt1.y)
          ctx.lineTo(pt2.x, pt2.y)
          ctx.stroke()
        })

        particleSystem.eachNode(function(node, pt){
          // node: {mass:#, p:{x,y}, name:"", data:{}}
          // pt:   {x:#, y:#}  node position in screen coords

          // draw a rectangle centered at pt
          var w = ctx.measureText(node.data.label||"").width + 6
          var label = node.data.label
          if (!(label||"").match(/^[ \t]*$/)){
            pt.x = Math.floor(pt.x)
            pt.y = Math.floor(pt.y)
          }else{
            label = null
          }
          
          // clear any edges below the text label
          // ctx.fillStyle = 'rgba(255,255,255,.6)'
          // ctx.fillRect(pt.x-w/2, pt.y-7, w,14)


          ctx.clearRect(pt.x-w/2, pt.y-7, w,14)

          

          // draw the text
          if (label){
            ctx.font = "bold 11px Arial"
            ctx.textAlign = "center"
            
            // if (node.data.region) ctx.fillStyle = palette[node.data.region]
            // else ctx.fillStyle = "#888888"
            ctx.fillStyle = "#888888"

            // ctx.fillText(label||"", pt.x, pt.y+4)
            ctx.fillText(label||"", pt.x, pt.y+4)
          }
        })    			
      },
      
      initMouseHandling:function(){
        // no-nonsense drag and drop (thanks springy.js)
        var dragged = null;

        // set up a handler object that will initially listen for mousedowns then
        // for moves and mouseups while dragging
        var handler = {
          clicked:function(e){
            var pos = $(canvas).offset();
            _mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)
            dragged = particleSystem.nearest(_mouseP);

            if (dragged && dragged.node !== null){
              // while we're dragging, don't let physics move the node
              dragged.node.fixed = true
            }

            $(canvas).bind('mousemove', handler.dragged)
            $(window).bind('mouseup', handler.dropped)

            return false
          },
          dragged:function(e){
            var pos = $(canvas).offset();
            var s = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)

            if (dragged && dragged.node !== null){
              var p = particleSystem.fromScreen(s)
              dragged.node.p = p
            }

            return false
          },

          dropped:function(e){
            if (dragged===null || dragged.node===undefined) return
            if (dragged.node !== null) dragged.node.fixed = false
            dragged.node.tempMass = 1000
            dragged = null
            $(canvas).unbind('mousemove', handler.dragged)
            $(window).unbind('mouseup', handler.dropped)
            _mouseP = null
            return false
          }
        }
        
        // start listening
        $(canvas).mousedown(handler.clicked);

      },
      
    }
    return that
  }    

  $(document).ready(function(){
    sys = arbor.ParticleSystem(500, 100, 0.1) // create the system with sensible repulsion/stiffness/friction
    sys.parameters({gravity: true}) // use center-gravity to make the graph settle nicely (ymmv)
    sys.renderer = Renderer("#viewport") // our newly created renderer will have its .init() method called shortly by sys...
    
    // add some nodes to the graph and watch it go...

        $("#username").bind('keyup', function(e) {
            var code = (e.keyCode ? e.keyCode : e.which);
            if(code == 13) { //Enter keycode
                $.getJSON('/nr?username=' + $("#username").val(), function(data) {
                  $('#content').html(data.friends.toString());
                  console.log('Load was performed.');
                  $.each(data.friends, function() {
                                     sys.addNode(data.twitter_id, {label: $("#username").val()})
        
                       sys.addNode(this.toString(), {label: this.toString()})
                           sys.addEdge(data.twitter_id,this.toString())
                      nodeslist.push(this.toString())
                      //alert(this);
                  });
                  $("#intro").html("Showing basic twitter friends graph for user " + $("#username").val());
                  setTimeout("getNext()", 5000);
                });
            }
                  
        });
        
        
    
    // or, equivalently:
    //
    // sys.graft({
    //   nodes:{
    //     f:{alone:true, mass:.25}
    //   }, 
    //   edges:{
    //     a:{ b:{},
    //         c:{},
    //         d:{},
    //         e:{}
    //     }
    //   }
    // })
    
  })

})(this.jQuery)
var sys;
var nodeslist = new Array();

        function getNext() {
                if (nodeslist.length == 0)
                {
                    //setTimeout("getNext()", 2000);
                    sys.eachNode(function(node, pt) {
                        if (sys.getEdgesFrom(node).length + sys.getEdgesTo(node).length < 2) {
                            console.log("pruning " + node.toString());
                            sys.pruneNode(node);
                        }
                        //console.log(node.toString());
                    });
                }
                else
                {
                    nextID = nodeslist.pop();
                    
                    $.getJSON('/getConnections?id=' + nextID, function(data) {
                      if (nextID != '23909859')
                      sys.addNode(nextID, {label:data.screen_name});
                      if (nextID != '23909859')
                      if (data.response == '0')
                      {
                          $.each(data.friends, function() {
                                  
                                if (!sys.getNode(this.toString()) )
                               sys.addNode(this.toString(), {label: this.toString()})
                                   sys.addEdge(nextID,this.toString())
                              //nodeslist.push(this.toString())
                          });
                      }
                      else
                      {
                          sys.pruneNode(nextID);
                      }
                            setTimeout("getNext()", 100);
                            console.log(nodeslist.length + " items: " + nodeslist);
                    });
                }
        }
