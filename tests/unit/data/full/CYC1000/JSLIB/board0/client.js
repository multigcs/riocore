#!/usr/bin/env node


var http = require('http');
var url = require('url');

const rio = require('./rio');
const dgram = require('node:dgram');
const { Buffer } = require('node:buffer');

HTTP_PORT = 8080;
SOURCE_PORT = 2391;
TARGET_PORT = 2390;
TARGET_IP = '127.0.0.1';

rio_rx = {};

const server = dgram.createSocket('udp4');

server.on('error', (err) => {
    console.error(`server error:
${err.stack}`);
    server.close();
});

server.on('listening', () => {
    const address = server.address();
});

server.on('message', (msg, rinfo) => {
    data = msg.slice()
    rio_rx = rio.get_rx(data);
});

function send() {
    message = rio.set_tx(rio.output);
    server.send(message, TARGET_PORT, TARGET_IP, (err) => {
    });
}

server.bind(SOURCE_PORT);

var timer = setInterval(function () {
    send();
}, 10);

console.log(`http server listening ${HTTP_PORT}`);

rio.output["pwmout0"]["dty"] = 0;
rio.output["pwmout0"]["enable"] = 0;
rio.output["stepdir0"]["velocity"] = 0;
rio.output["stepdir0"]["enable"] = 0;
rio.output["bitout0"]["bit"] = 0;
rio.output["bitout1"]["bit"] = 0;

http.createServer(function (req, res) {
    var q = url.parse(req.url, true);
    var filename = "." + q.pathname;
    res.writeHead(200, {'Content-Type': 'text/html'});

    if ("pwmout0.dty" in q.query) {
        rio.output["pwmout0"]["dty"] = parseInt(q.query["pwmout0.dty"]);
    }
    if ("pwmout0.enable" in q.query) {
        rio.output["pwmout0"]["enable"] = parseInt(q.query["pwmout0.enable"]);
    }
    if ("stepdir0.velocity" in q.query) {
        rio.output["stepdir0"]["velocity"] = parseInt(q.query["stepdir0.velocity"]);
    }
    if ("stepdir0.enable" in q.query) {
        rio.output["stepdir0"]["enable"] = parseInt(q.query["stepdir0.enable"]);
    }
    if ("bitout0.bit" in q.query) {
        rio.output["bitout0"]["bit"] = parseInt(q.query["bitout0.bit"]);
    }
    if ("bitout1.bit" in q.query) {
        rio.output["bitout1"]["bit"] = parseInt(q.query["bitout1.bit"]);
    }

    res.write("<form action='/'>");
    res.write("pwmout0.dty: <input type='text' id='pwmout0.dty' name='pwmout0.dty' value='" + String(rio.output["pwmout0"]["dty"]) + "'><br/>");
    res.write("pwmout0.enable: <input type='text' id='pwmout0.enable' name='pwmout0.enable' value='" + String(rio.output["pwmout0"]["enable"]) + "'><br/>");
    res.write("stepdir0.velocity: <input type='text' id='stepdir0.velocity' name='stepdir0.velocity' value='" + String(rio.output["stepdir0"]["velocity"]) + "'><br/>");
    res.write("stepdir0.enable: <input type='text' id='stepdir0.enable' name='stepdir0.enable' value='" + String(rio.output["stepdir0"]["enable"]) + "'><br/>");
    res.write("bitout0.bit: <input type='text' id='bitout0.bit' name='bitout0.bit' value='" + String(rio.output["bitout0"]["bit"]) + "'><br/>");
    res.write("bitout1.bit: <input type='text' id='bitout1.bit' name='bitout1.bit' value='" + String(rio.output["bitout1"]["bit"]) + "'><br/>");
    res.write("  <input type='submit' value='Submit'>");
    res.write("</form>");

    res.write("stepdir0.position = ");
    res.write(String(rio_rx["stepdir0"]["position"]));
    res.write("<br/>");
    res.write("bitin0.bit = ");
    res.write(String(rio_rx["bitin0"]["bit"]));
    res.write("<br/>");

    res.end();
}).listen(HTTP_PORT);

