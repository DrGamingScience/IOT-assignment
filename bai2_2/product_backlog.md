# Product Backlog - Individual MQTT Assignment

Scope: Part 2, pages 2-4 of the [assignment PDF](<../bai2_1/Bài 2. Trao đổi dữ liệu sử dụng giao thức MQTT (VI).pdf>). See [requirements analysis](requirement_analysis.md) for details.

Primary user: the student running and demonstrating the MQTT program. PB01-PB05 and PB08-PB09 have Java implementations; build/runtime verification is tracked in the README. PB06 (MQTTX demonstration) and PB07 (report/submission) remain to do. Must items cover the required submission; Could items are encouraged extensions.

| ID | Priority | Backlog item / user need | Acceptance criteria | Requirement |
| --- | --- | --- | --- | --- |
| PB01 | Must | Configure my student-specific MQTT connection. | Connect to `broker.hivemq.com:1883`; topics contain my MSSV; each client has a unique ID. | R1 |
| PB02 | Must | Create complete simulated sensor messages. | Serialize valid JSON containing `id`, `name`, `packet_no`, `temperature`, `humidity`, `tds`, `pH`. | R2 |
| PB03 | Must | Send readings periodically so a receiver can monitor them. | Publish to `it4735e/<MSSV>/telemetry` at QoS 1, using five seconds as the initial interval; increase the counter by 1 per new send. | R2, R3 |
| PB04 | Must | Receive and understand messages under my topic prefix. | Subscribe to `it4735e/<MSSV>/#` at QoS 1; parse JSON and display all seven fields, including messages returned from my own publisher. | R4 |
| PB05 | Must | Keep the program running when bad data arrives. | Catch and log invalid JSON; raw `hello` followed by valid telemetry produces an error and then correctly displayed readings without restarting. | R5 |
| PB06 | Must | Independently demonstrate both communication directions. | MQTTX/MQTTBox receives program telemetry and publishes sample JSON that the program parses correctly; capture evidence. | R6 |
| PB07 | Must | Explain and submit my work. | Prepare a short report with key source code, explanations, and screenshots covering connection, periodic counter changes, received fields, both tool checks, and recovery after malformed JSON; submit report plus source files. | R7 |
| PB08 | Could | Show whether the device is online. | Retained `online` is published to `/status` after connecting; retained Last Will `offline` appears after unexpected connection loss; status text is handled separately from telemetry JSON. | Optional status |
| PB09 | Could | Recover automatically after a connection interruption. | Reconnect and re-subscribe after each connection; reception and periodic publishing resume. | Optional reconnect |

## Completion checklist

- [ ] PB01-PB07 meet their acceptance criteria using my actual MSSV.
- [ ] Screenshots clearly show the topics, payload fields, counter progression, and continued operation after invalid JSON.
- [ ] Source files and the short report are ready to submit.
- [ ] If PB08/PB09 are implemented, include their demonstration and evidence in the report.
