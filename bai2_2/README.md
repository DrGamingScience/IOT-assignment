# Individual MQTT Assignment - Java

Implements Part 2 of the assignment: periodic JSON telemetry at QoS 1, wildcard subscription, error handling, and both encouraged extensions. Requires **JDK 17 or newer**. The default broker is `tcp://broker.hivemq.com:1883`; readings are simulated.

## Run on Windows

Open PowerShell in this folder and replace `YOUR_MSSV` with your actual student ID:

```powershell
cd D:\IOT-asm\bai2_2
.\run.ps1 -Mssv YOUR_MSSV
```

The launcher downloads Eclipse Paho 1.2.5 and JSON-java 20240303 from Maven Central into `lib/`, compiles into `out/`, and runs the client. Maven is not required for this route. First-time dependency downloads need Internet access. If PowerShell blocks scripts, you can use the Maven route below without changing execution policy.

```powershell
# Optional: change the interval, or compile without connecting.
.\run.ps1 -Mssv YOUR_MSSV -IntervalSeconds 3
.\run.ps1 -BuildOnly
```

Alternatively, import `pom.xml` as a Maven project in Eclipse/IntelliJ, or run:

```powershell
mvn test
mvn package
java -jar target/mqtt-assignment-1.0.0.jar --mssv YOUR_MSSV
```

Stop with **Ctrl+C**. Your MSSV is mandatory; the program creates a new unique MQTT client ID on each run. The first `packet_no` is 126, then 127, 128, etc. It resets on a new run. Publishing pauses while disconnected, and initial connection failures retry every five seconds.

## MQTTX / MQTTBox verification

1. Create a TCP connection: host `broker.hivemq.com`, port `1883`, no username/password, and a client ID different from the Java program.
2. Subscribe to `it4735e/YOUR_MSSV/#` with QoS 1. Start Java and observe `/telemetry` JSON and `/status` messages. Confirm increasing packet numbers and all seven fields.
3. Publish this JSON from the tool to `it4735e/YOUR_MSSV/telemetry` at QoS 1. Java should display every field:

```json
{"id":11,"name":"mqttx","packet_no":1,"temperature":25,"humidity":55,"tds":900,"pH":6.5}
```

4. Switch the tool's payload editor to plain text/raw and send `hello` to the same telemetry topic. Java should print `JSON error ... (continuing)`. Send valid JSON again and verify it is processed without restarting.
5. Capture screenshots for your report. Explain the key Java code, then submit the report and source files. These deliverables and the live MQTTX demonstration still need to be completed.

## What the encouraged extensions mean

They are optional features in section d of the PDF. Both are enabled in this implementation:

- **Last Will:** before connecting, Java asks the broker to publish `offline` on `it4735e/YOUR_MSSV/status` if its connection ends unexpectedly. The broker sends it after detecting the loss; it is not necessarily immediate.
- **Retained status:** `online` after connecting and `offline` as Last Will both use the retained flag. The broker stores the latest status and sends it to a new subscriber immediately. Retention applies to status, not telemetry here.
- **Automatic recovery:** Paho reconnects after a lost connection. Every `connectComplete` callback re-subscribes to the wildcard topic, publishes retained `online`, and allows telemetry to resume.

To demonstrate Last Will, keep MQTTX connected and forcibly terminate only this Java process (for example, End task in Task Manager). Wait for `/status` to become `offline`, then reconnect MQTTX and confirm the retained value. A normal Ctrl+C exit explicitly publishes `offline` because clean MQTT disconnection does not trigger Last Will.

To demonstrate reconnect, temporarily disconnect the Java computer's network, then restore it. Check for `Reconnected`, a fresh `Subscribed` log, `online`, and resumed telemetry. A local broker can also be supplied with `--broker tcp://localhost:1883` (or `-Broker` in PowerShell) for controlled tests.

The wildcard subscription receives status too. Java routes `/status` as plain text instead of trying to parse it as telemetry JSON. Run one device instance per MSSV when demonstrating status because both would otherwise write to the same retained topic.

## Code and tests

- `ClientConfig.java`: validates arguments and constructs student-specific topics.
- `Telemetry.java`: generates readings and converts the seven fields to/from JSON.
- `MqttAssignment.java`: MQTT callbacks, publication, reconnect, status, and shutdown.
- `AssignmentTest.java`: checks argument validation, payload parsing, recovery after bad input, and status routing with JUnit.

Unit tests run with `mvn test` and do not require a broker. They do not replace the live MQTTX, Last Will, and reconnect checks above. The public broker is unauthenticated and unencrypted: use synthetic data only.

Verification in this coding session: the configuration class compiled for Java 17 and passed 18 smoke checks; Maven project validation, POM XML parsing, and PowerShell syntax checks passed. Full project compilation, the JUnit suite, and live MQTT checks remain unverified because the Paho/JSON dependencies are not cached and outbound downloads are blocked here. This machine also blocks PowerShell script execution; use the Maven commands above for running the project.

API references: [Paho connection options and Last Will](https://eclipse.dev/paho/files/javadoc/org/eclipse/paho/client/mqttv3/MqttConnectOptions.html), [connection-complete callback](https://eclipse.dev/paho/files/javadoc/org/eclipse/paho/client/mqttv3/MqttCallbackExtended.html).
