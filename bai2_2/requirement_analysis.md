# Requirements Analysis - Individual MQTT Assignment

Source: [Assignment PDF](<../bai2_1/Bài 2. Trao đổi dữ liệu sử dụng giao thức MQTT (VI).pdf>), **Part 2, pages 2-4**. Part 1 is the separate group lab.

## Objective and scope

Build a program that publishes simulated sensor readings and subscribes to MQTT messages through a public broker. The same program may perform both roles; the individual task does not require two separate programs. No physical sensors or graphical interface are specified.

## Mandatory requirements

| ID | Requirement | Acceptance check |
| --- | --- | --- |
| R1 | Connect to `broker.hivemq.com:1883` over TCP. Use your MSSV in topics and a unique client ID for every client. | Program connects successfully; MQTTX uses a different client ID. |
| R2 | Publish a JSON object to `it4735e/<MSSV>/telemetry` with **QoS 1**. Include `id`, `name`, `packet_no`, `temperature`, `humidity`, `tds`, and `pH` (exact spelling/case). | MQTTX receives all seven fields on the correct topic. |
| R3 | Publish periodically and increase `packet_no` by 1 after each send. | Consecutive new messages show, for example, 126, 127, 128. Five seconds is the PDF's example interval. |
| R4 | Subscribe to `it4735e/<MSSV>/#`, parse received JSON, and display all seven fields. The setup guide specifies subscription QoS 1. | Display readings from the program itself and from MQTTX. |
| R5 | Catch malformed JSON, print an error, and continue running. | Send raw `hello`, then valid JSON from MQTTX; an error appears and the later valid message is processed. |
| R6 | Verify both directions with MQTTX or MQTTBox. | Tool receives program telemetry; program receives and correctly parses tool-published JSON. |
| R7 | Submit a short report and source-code files. | Report explains key code and includes screenshots of execution and results for the requirements. |

Example payload (values are examples, not fixed constants):

```json
{"id":11,"name":"my-mqtt-client","packet_no":126,"temperature":30,"humidity":60,"tds":1100,"pH":5.0}
```

## Optional extensions

- Retained device status on `it4735e/<MSSV>/status`: configure Last Will as `offline` and publish retained `online` after connecting.
- Automatically reconnect and subscribe again after every connection.

If status is implemented, route its plain-text messages separately before parsing telemetry JSON because the wildcard subscription also receives `/status`.

## Implementation decisions and constraints

- **Implementation choice:** Java 17+ with Eclipse Paho MQTT 1.2.5 and JSON-java. Both optional extensions are included; they remain optional in the assignment rubric.
- Replace `<MSSV>` with your actual student ID. Use synthetic readings only: the broker has no authentication, and port 1883 is unencrypted.
- QoS 1 can produce duplicate deliveries; assess the counter on new published messages. Persistence across restarts is not specified.
- A five-second interval and starting counter of 126 are reasonable defaults. The PDF does not specify a deadline or report file format.
