package vn.edu.iot;

import org.json.JSONException;
import org.json.JSONObject;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class AssignmentTest {
    private static final String PAYLOAD = """
            {"id":11,"name":"mqttx","packet_no":1,"temperature":25,"humidity":55,"tds":900,"pH":6.5}
            """;

    @Test
    void studentIdIsRequiredAndCannotChangeTheTopicHierarchy() {
        assertThrows(IllegalArgumentException.class, () -> ClientConfig.parse(new String[0]));
        for (String invalid : new String[]{"", "student/#", "+", "student name"}) {
            assertThrows(IllegalArgumentException.class,
                    () -> ClientConfig.parse(new String[]{"--mssv", invalid}));
        }
        ClientConfig config = ClientConfig.parse(new String[]{"--mssv", "20231234"});
        assertEquals("it4735e/20231234/telemetry", config.telemetryTopic());
        assertEquals("it4735e/20231234/#", config.subscriptionTopic());
        assertEquals("it4735e/20231234/status", config.statusTopic());
        assertEquals(5, config.intervalSeconds());
    }

    @Test
    void rejectsInvalidOptionsBeforeConnecting() {
        for (String interval : new String[]{"0", "-1", "abc", "999999999999"}) {
            assertThrows(IllegalArgumentException.class, () -> ClientConfig.parse(
                    new String[]{"--mssv", "20231234", "--interval", interval}));
        }
        assertThrows(IllegalArgumentException.class,
                () -> ClientConfig.parse(new String[]{"--mssv"}));
        assertThrows(IllegalArgumentException.class,
                () -> ClientConfig.parse(new String[]{"--mssv", "20231234", "--unknown", "x"}));
        assertThrows(IllegalArgumentException.class, () -> ClientConfig.parse(
                new String[]{"--mssv", "20231234", "--broker", "https://example.com:1883"}));
    }

    @Test
    void readsExternalMessagesWithTheExactAssignmentFieldNames() {
        Telemetry reading = Telemetry.fromJson(PAYLOAD);
        assertEquals("mqttx", reading.name());
        assertEquals(1, reading.packetNo());
        assertEquals(6.5, reading.pH());
        assertEquals(reading, Telemetry.fromJson(reading.toJson()));
        JSONObject encoded = new JSONObject(reading.toJson());
        assertEquals(7, encoded.length());
        assertTrue(encoded.has("pH"));
        assertFalse(encoded.has("ph"));
    }

    @Test
    void rejectsMalformedIncompleteAndTrailingContent() {
        for (String invalid : new String[]{"hello", "{", "[]", "{}", PAYLOAD + "hello"}) {
            assertThrows(JSONException.class, () -> Telemetry.fromJson(invalid));
        }
    }

    @Test
    void badMessageDoesNotPreventTheNextMessageFromBeingProcessed() {
        String topic = "it4735e/20231234/telemetry";
        String status = "it4735e/20231234/status";
        String error = MqttAssignment.formatReceived(status, topic, "hello");
        assertTrue(error.contains("JSON error"));
        assertTrue(error.contains("continuing"));
        String valid = MqttAssignment.formatReceived(status, topic, PAYLOAD);
        for (String field : new String[]{"id=11", "name=mqttx", "packet_no=1", "temperature=25.0",
                "humidity=55.0", "tds=900.0", "pH=6.5"}) {
            assertTrue(valid.contains(field), valid);
        }
    }

    @Test
    void statusMessagesAreNotParsedAsTelemetry() {
        String status = "it4735e/20231234/status";
        assertEquals("<< Status on " + status + ": online",
                MqttAssignment.formatReceived(status, status, "online"));
        assertFalse(MqttAssignment.formatReceived(status, status, "offline").contains("JSON error"));
    }
}
