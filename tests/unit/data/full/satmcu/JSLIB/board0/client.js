#!/usr/bin/env node


var http = require('http');
var url = require('url');

const rio = require('./rio');
const dgram = require('node:dgram');
const { Buffer } = require('node:buffer');

HTTP_PORT = 8080;
SOURCE_PORT = 2391;
TARGET_PORT = 2390;
TARGET_IP = '192.168.11.201';

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

rio.output["stepdir0"]["velocity"] = 0;
rio.output["stepdir0"]["enable"] = 0;
rio.output["stepdir1"]["velocity"] = 0;
rio.output["stepdir1"]["enable"] = 0;
rio.output["stepdir2"]["velocity"] = 0;
rio.output["stepdir2"]["enable"] = 0;
rio.output["pwmout0"]["dty"] = 0;
rio.output["pwmout0"]["enable"] = 0;
rio.output["bitout0"]["bit"] = 0;
rio.output["bitout1"]["bit"] = 0;
rio.output["ledscale0"]["bit"] = 0;
rio.output["ledscale1"]["bit"] = 0;
rio.output["ledscale2"]["bit"] = 0;
rio.output["selectedx"]["bit"] = 0;
rio.output["selectedy"]["bit"] = 0;
rio.output["selectedz"]["bit"] = 0;

http.createServer(function (req, res) {
    var q = url.parse(req.url, true);
    var filename = "." + q.pathname;
    res.writeHead(200, {'Content-Type': 'text/html'});

    if ("stepdir0.velocity" in q.query) {
        rio.output["stepdir0"]["velocity"] = parseInt(q.query["stepdir0.velocity"]);
    }
    if ("stepdir0.enable" in q.query) {
        rio.output["stepdir0"]["enable"] = parseInt(q.query["stepdir0.enable"]);
    }
    if ("stepdir1.velocity" in q.query) {
        rio.output["stepdir1"]["velocity"] = parseInt(q.query["stepdir1.velocity"]);
    }
    if ("stepdir1.enable" in q.query) {
        rio.output["stepdir1"]["enable"] = parseInt(q.query["stepdir1.enable"]);
    }
    if ("stepdir2.velocity" in q.query) {
        rio.output["stepdir2"]["velocity"] = parseInt(q.query["stepdir2.velocity"]);
    }
    if ("stepdir2.enable" in q.query) {
        rio.output["stepdir2"]["enable"] = parseInt(q.query["stepdir2.enable"]);
    }
    if ("pwmout0.dty" in q.query) {
        rio.output["pwmout0"]["dty"] = parseInt(q.query["pwmout0.dty"]);
    }
    if ("pwmout0.enable" in q.query) {
        rio.output["pwmout0"]["enable"] = parseInt(q.query["pwmout0.enable"]);
    }
    if ("bitout0.bit" in q.query) {
        rio.output["bitout0"]["bit"] = parseInt(q.query["bitout0.bit"]);
    }
    if ("bitout1.bit" in q.query) {
        rio.output["bitout1"]["bit"] = parseInt(q.query["bitout1.bit"]);
    }
    if ("ledscale0.bit" in q.query) {
        rio.output["ledscale0"]["bit"] = parseInt(q.query["ledscale0.bit"]);
    }
    if ("ledscale1.bit" in q.query) {
        rio.output["ledscale1"]["bit"] = parseInt(q.query["ledscale1.bit"]);
    }
    if ("ledscale2.bit" in q.query) {
        rio.output["ledscale2"]["bit"] = parseInt(q.query["ledscale2.bit"]);
    }
    if ("selectedx.bit" in q.query) {
        rio.output["selectedx"]["bit"] = parseInt(q.query["selectedx.bit"]);
    }
    if ("selectedy.bit" in q.query) {
        rio.output["selectedy"]["bit"] = parseInt(q.query["selectedy.bit"]);
    }
    if ("selectedz.bit" in q.query) {
        rio.output["selectedz"]["bit"] = parseInt(q.query["selectedz.bit"]);
    }

    res.write("<form action='/'>");
    res.write("stepdir0.velocity: <input type='text' id='stepdir0.velocity' name='stepdir0.velocity' value='" + String(rio.output["stepdir0"]["velocity"]) + "'><br/>");
    res.write("stepdir0.enable: <input type='text' id='stepdir0.enable' name='stepdir0.enable' value='" + String(rio.output["stepdir0"]["enable"]) + "'><br/>");
    res.write("stepdir1.velocity: <input type='text' id='stepdir1.velocity' name='stepdir1.velocity' value='" + String(rio.output["stepdir1"]["velocity"]) + "'><br/>");
    res.write("stepdir1.enable: <input type='text' id='stepdir1.enable' name='stepdir1.enable' value='" + String(rio.output["stepdir1"]["enable"]) + "'><br/>");
    res.write("stepdir2.velocity: <input type='text' id='stepdir2.velocity' name='stepdir2.velocity' value='" + String(rio.output["stepdir2"]["velocity"]) + "'><br/>");
    res.write("stepdir2.enable: <input type='text' id='stepdir2.enable' name='stepdir2.enable' value='" + String(rio.output["stepdir2"]["enable"]) + "'><br/>");
    res.write("pwmout0.dty: <input type='text' id='pwmout0.dty' name='pwmout0.dty' value='" + String(rio.output["pwmout0"]["dty"]) + "'><br/>");
    res.write("pwmout0.enable: <input type='text' id='pwmout0.enable' name='pwmout0.enable' value='" + String(rio.output["pwmout0"]["enable"]) + "'><br/>");
    res.write("bitout0.bit: <input type='text' id='bitout0.bit' name='bitout0.bit' value='" + String(rio.output["bitout0"]["bit"]) + "'><br/>");
    res.write("bitout1.bit: <input type='text' id='bitout1.bit' name='bitout1.bit' value='" + String(rio.output["bitout1"]["bit"]) + "'><br/>");
    res.write("ledscale0.bit: <input type='text' id='ledscale0.bit' name='ledscale0.bit' value='" + String(rio.output["ledscale0"]["bit"]) + "'><br/>");
    res.write("ledscale1.bit: <input type='text' id='ledscale1.bit' name='ledscale1.bit' value='" + String(rio.output["ledscale1"]["bit"]) + "'><br/>");
    res.write("ledscale2.bit: <input type='text' id='ledscale2.bit' name='ledscale2.bit' value='" + String(rio.output["ledscale2"]["bit"]) + "'><br/>");
    res.write("selectedx.bit: <input type='text' id='selectedx.bit' name='selectedx.bit' value='" + String(rio.output["selectedx"]["bit"]) + "'><br/>");
    res.write("selectedy.bit: <input type='text' id='selectedy.bit' name='selectedy.bit' value='" + String(rio.output["selectedy"]["bit"]) + "'><br/>");
    res.write("selectedz.bit: <input type='text' id='selectedz.bit' name='selectedz.bit' value='" + String(rio.output["selectedz"]["bit"]) + "'><br/>");
    res.write("  <input type='submit' value='Submit'>");
    res.write("</form>");

    res.write("stepdir0.position = ");
    res.write(String(rio_rx["stepdir0"]["position"]));
    res.write("<br/>");
    res.write("stepdir1.position = ");
    res.write(String(rio_rx["stepdir1"]["position"]));
    res.write("<br/>");
    res.write("stepdir2.position = ");
    res.write(String(rio_rx["stepdir2"]["position"]));
    res.write("<br/>");
    res.write("bitin0.bit = ");
    res.write(String(rio_rx["bitin0"]["bit"]));
    res.write("<br/>");
    res.write("bitin1.bit = ");
    res.write(String(rio_rx["bitin1"]["bit"]));
    res.write("<br/>");
    res.write("bitin2.bit = ");
    res.write(String(rio_rx["bitin2"]["bit"]));
    res.write("<br/>");
    res.write("bitin3.bit = ");
    res.write(String(rio_rx["bitin3"]["bit"]));
    res.write("<br/>");
    res.write("bitin4.bit = ");
    res.write(String(rio_rx["bitin4"]["bit"]));
    res.write("<br/>");
    res.write("bitin5.bit = ");
    res.write(String(rio_rx["bitin5"]["bit"]));
    res.write("<br/>");
    res.write("bitin6.bit = ");
    res.write(String(rio_rx["bitin6"]["bit"]));
    res.write("<br/>");
    res.write("bitin7.bit = ");
    res.write(String(rio_rx["bitin7"]["bit"]));
    res.write("<br/>");
    res.write("uartsub0.timeout = ");
    res.write(String(rio_rx["uartsub0"]["timeout"]));
    res.write("<br/>");
    res.write("mpgestop.bit = ");
    res.write(String(rio_rx["mpgestop"]["bit"]));
    res.write("<br/>");
    res.write("scale0.bit = ");
    res.write(String(rio_rx["scale0"]["bit"]));
    res.write("<br/>");
    res.write("scale1.bit = ");
    res.write(String(rio_rx["scale1"]["bit"]));
    res.write("<br/>");
    res.write("scale2.bit = ");
    res.write(String(rio_rx["scale2"]["bit"]));
    res.write("<br/>");
    res.write("selectx.bit = ");
    res.write(String(rio_rx["selectx"]["bit"]));
    res.write("<br/>");
    res.write("selecty.bit = ");
    res.write(String(rio_rx["selecty"]["bit"]));
    res.write("<br/>");
    res.write("selectz.bit = ");
    res.write(String(rio_rx["selectz"]["bit"]));
    res.write("<br/>");
    res.write("lbutton.bit = ");
    res.write(String(rio_rx["lbutton"]["bit"]));
    res.write("<br/>");
    res.write("cbutton.bit = ");
    res.write(String(rio_rx["cbutton"]["bit"]));
    res.write("<br/>");
    res.write("rbutton.bit = ");
    res.write(String(rio_rx["rbutton"]["bit"]));
    res.write("<br/>");

    res.end();
}).listen(HTTP_PORT);

