'use strict';

// Dit is de website van Yitro
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let localIp;
let htmlTemps, htmlLight, htmlMoisture;
let htmlChart;

let data1, data2, data3, data4, data5, data6, data7, data8, data9, data10;

const showTemperaturen = function (Temps) {
  let teller = 0;
  let avgTemp = 0;
  for (const temp of Temps) {
    teller += 1;
    avgTemp += temp;
  }
  htmlTemps.innerHTML = `<a href="history.html?DeviceId=6" class="c-link-cta">
        <div>Temperatuur: <br />${(avgTemp / teller).toFixed(2)} °C</div>
      </a>`;
};

const showLight = function (lights) {
  let teller = 0;
  let avgLight = 0;
  for (const light of lights) {
    teller += 1;
    avgLight += light;
  }
  htmlLight.innerHTML = `<a href="history.html?DeviceId=1" class="c-link-cta">
   <div>Lichtsterkte: <br />${(avgLight / teller).toFixed(2)} %</div>
 </a>`;
};

const showMoisture = function (moisture) {
  htmlMoisture.innerHTML = `<a href="history.html?DeviceId=9" class="c-link-cta">
  <div>Vochtigheid grond: <br />${moisture} %</div>
</a>`;
};

const showDataChart = function (data) {
  console.log(data);
  let labels = [];
  let dataChart = data.waardes;
  drawChart(labels, dataChart);
};

const drawChart = function (labels, data) {
  var options = {
    chart: {
      id: 'myChart',
      type: 'line',
    },
    stroke: {
      curve: 'straight',
    },
    dataLabels: {
      enabled: false,
    },
    series: [
      {
        name: 'Sensor data',
        data: data,
      },
    ],
    labels: labels,
    noData: {
      text: 'Loading...',
    },
  };

  var chart = new ApexCharts(document.querySelector('.js-chart'), options);
  chart.render();
};

const getHistory = function (deviceId) {
  getDataSensors(deviceId);
};

const datasens = function (data) {
  data1 = data;
  console.log(data1);
};

const getDataSensors = function (sensors) {
  handleData(`${localIp}:5000/api/v1/history/${sensors}`, showDataChart);
};

const listenToUI = function () {
  const button = document.querySelector('.js-btn-pump');
  button.addEventListener('click', function () {
    socket.emit('F2B_activate_pump');
  });
};

const listenToSocket = function () {
  socket.on('connected', function () {
    console.log('verbonden met socket webserver');
    socket.emit('F2B_get_last_temps');
    socket.emit('F2B_get_last_light');
    socket.emit('F2B_get_last_moisture');
  });

  socket.on('B2F_waarde_temperatuur_sensoren', function (lijstTemperaturen) {
    const temperaturen = lijstTemperaturen.temperatuur_sensoren;
    console.log(`Temperaturen: ${temperaturen}`);
    showTemperaturen(temperaturen);
  });

  socket.on('B2F_value_light_sensor', function (listLight) {
    console.log(listLight);
    showLight(listLight.light_sensors);
  });

  socket.on('B2F_value_moisture_sensor', function (moisture) {
    console.log(moisture);
    showMoisture(moisture.moisture_sensor);
  });
};

document.addEventListener('DOMContentLoaded', function () {
  console.info('DOM geladen');
  localIp = `${window.location.protocol}//${window.location.host}`;
  htmlTemps = document.querySelector('.js-temp');
  if (htmlTemps != null) {
    htmlLight = document.querySelector('.js-light');
    htmlMoisture = document.querySelector('.js-ground');
    listenToUI();
    listenToSocket();
  }

  htmlChart = document.querySelector('.js-chart');
  if (htmlChart != null) {
    let urlParams = new URLSearchParams(window.location.search);
    let deviceId = urlParams.get('DeviceId');
    if (deviceId) {
      getHistory(deviceId);
    } else {
      window.location.href = 'index.html';
    }
  }
});
