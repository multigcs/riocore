#!/usr/bin/env node


const rio = require('./rio');
const dgram = require('node:dgram');
const { Buffer } = require('node:buffer');

SOURCE_PORT = 2391;
TARGET_PORT = 2390;
TARGET_IP = '127.0.0.1';

const server = dgram.createSocket('udp4');

server.on('error', (err) => {
    console.error(`server error:
${err.stack}`);
    server.close();
});

server.on('listening', () => {
    const address = server.address();
    console.log(`server listening ${address.address}:${address.port}`);
});

server.on('message', (msg, rinfo) => {
    console.log(`server got: ${msg} from ${rinfo.address}:${rinfo.port}`);
    data = msg.slice()
    console.log(data);
    rio_rx = rio.get_rx(data);
    console.log("stepdir0.position = ", rio_rx["stepdir0"]["position"]);
    console.log("stepdir1.position = ", rio_rx["stepdir1"]["position"]);
    console.log("stepdir2.position = ", rio_rx["stepdir2"]["position"]);
});

function send() {
    rio.output["stepdir0"]["velocity"] = 0;
    rio.output["stepdir0"]["enable"] = 0;
    rio.output["stepdir1"]["velocity"] = 0;
    rio.output["stepdir1"]["enable"] = 0;
    rio.output["stepdir2"]["velocity"] = 0;
    rio.output["stepdir2"]["enable"] = 0;
    rio.output["board0_wled"]["0_green"] = 0;
    rio.output["board0_wled"]["0_blue"] = 0;
    rio.output["board0_wled"]["0_red"] = 0;

    message = rio.set_tx(rio.output);
    console.log(message);
    server.send(message, TARGET_PORT, TARGET_IP, (err) => {
        console.log("send ok");
    });
}

server.bind(SOURCE_PORT);

var timer = setInterval(function () {
    send();
}, 10);

