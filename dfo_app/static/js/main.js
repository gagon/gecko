

var socket = io.connect('http://' + document.domain + ':' + location.port);




var ipr_chart=Highcharts.chart('ipr_chart', {

      title: {
          text: ''
      },

      yAxis: {
          title: {
              text: "Pwf, " + uom.pres
          }
      },
      xAxis: {
          title: {
              text: conf.rate_type + " Rate, " + uom.rate
          }
      },
      legend: {

      },

      plotOptions: {

      },

      // series: [{
      //     name: 'Installation',
      //     data: []
      // }],



  });

  var ipr
  $( document ).on( "click", "#calc_ipr_btn", function() {
    var pi_val = $("#pi_val").text();
    var pres_val = $("#pres_val").text();
    var gor_val = $("#gor_val").text();
    var wct_val = $("#wct_val").text();
    var pb_val = $("#pb_val").text();
    socket.emit('calc_ipr',{"pi_val":pi_val,"pres_val":pres_val,"gor_val":gor_val,"wct_val":wct_val,"pb_val":pb_val});
  });



  socket.on('ipr_calcd', function(data) {
    clear_ipr_chart(ipr_chart)
    ipr=data.ipr;
    ipr_chart.addSeries({
      "name":"IPR",
      "data":ipr["pq"],
    },false);
    ipr_chart.redraw();
  });



  $( document ).on( "click", "#calc_pwf_rate_btn", function() {
    var pwf_val = $("#pwf_val").val();
    var rate_val = $("#rate_val").val();
    if (pwf_val>0 && rate_val==""){
      socket.emit('calc_ipr_pwf_rate',{"type":"rate","val":pwf_val})
    }else if(pwf_val=="" && rate_val>0){
      socket.emit('calc_ipr_pwf_rate',{"type":"pwf","val":rate_val})
    }
  });


  $( document ).on( "click", "#clear_pwf_rate_btn", function() {
    $("#pwf_val").val("");
    $("#rate_val").val("");
    clear_chart_last_left(ipr_chart)
  });

  function clear_ipr_chart(chart){
    var seriesLength = chart.series.length;
    for( var i = seriesLength-1; i == 0; i--){
      chart.series[i].remove();
    }
  }



  socket.on('ipr_rate_calcd', function(data) {
    if (data.point["rate"]>0){
      $("#rate_val").val(data.point["rate"]);
      data.point["pwf"]=parseFloat($("#pwf_val").val())
    }else{
      $("#pwf_val").val(data.point["pwf"]);
      data.point["rate"]=parseFloat($("#rate_val").val())
    }

    clear_ipr_chart(ipr_chart)

    ipr_chart.addSeries({
      "name":"Calculated",
      "data":[[data.point["rate"],data.point["pwf"]]],
      "color":"black",
      "marker":{
          "symbol":"square",
          "radius":5
        }
    },false);

    ipr_chart.redraw();

  });


$(document).ready(function() {
  $(':checkbox').change(function(){

    var check_id=$(this).closest('tr').find("[name=id]").text();

    if(this.checked){

      var bhp = parseFloat($(this).closest('tr').find("[name=bhp]").text());
      var rate = parseFloat($(this).closest('tr').find("[name=rate]").text());

      ipr_chart.addSeries({
        "name":check_id,
        "id":check_id,
        "data":[[rate,bhp]],
        // "color":"blue",
        "lineWidth": 0,
        "marker":{
            "symbol":"triangle",
            "radius":7
          }
      },false);
      ipr_chart.redraw();
    }else{
        ipr_chart.get(check_id).remove();
    }

  });
});

  // $(table).children('tr').each(function () { // loop through rows
  //         if ($(this).find("[name=ro]").is(":checked")){
  //           wellname=$(this).find("[name=wellname]").text() // get wellname
  //           wellcombs=data["well_data"][wellname]["connection"]["routes"].length;
  //           comb_num=comb_num*wellcombs;
  //         }
  //       })


  // $( document ).on( "click", "#calc_pwf_rate_btn", function() {
  //   var pwf_val = $("#pwf_val").val();
  //   var rate_val = $("#rate_val").val();
  //   if (pwf_val>0 && rate_val==""){
  //     socket.emit('calc_ipr_pwf_rate',{"type":"rate","val":pwf_val})
  //   }else if(pwf_val=="" && rate_val>0){
  //     socket.emit('calc_ipr_pwf_rate',{"type":"pwf","val":rate_val})
  //   }
  // });
