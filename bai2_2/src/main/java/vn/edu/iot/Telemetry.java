package vn.edu.iot;

import java.util.Locale;
import java.util.concurrent.ThreadLocalRandom;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

/** The seven fields required by Part 2. Sensor readings are simulated. */
public record Telemetry(long id, String name, long packetNo, double temperature,
                        double humidity, double tds, double pH) {
    public static Telemetry sample(long packetNo) {
        ThreadLocalRandom random = ThreadLocalRandom.current();
        return new Telemetry(11, "my-java-mqtt-client", packetNo,
                Math.round(random.nextDouble(20, 35) * 10) / 10.0,
                random.nextInt(40, 76), random.nextInt(800, 1201),
                Math.round(random.nextDouble(5, 7) * 10) / 10.0);
    }

    public String toJson() {
        return new JSONObject()
                .put("id", id)
                .put("name", name)
                .put("packet_no", packetNo)
                .put("temperature", temperature)
                .put("humidity", humidity)
                .put("tds", tds)
                .put("pH", pH)
                .toString();
    }

    public static Telemetry fromJson(String payload) {
        JSONTokener tokens = new JSONTokener(payload);
        JSONObject data = new JSONObject(tokens);
        if (tokens.nextClean() != 0) {
            throw new JSONException("Unexpected content after JSON object.");
        }
        // Required getters also reject missing fields and incompatible types.
        return new Telemetry(data.getLong("id"), data.getString("name"),
                data.getLong("packet_no"), data.getDouble("temperature"),
                data.getDouble("humidity"), data.getDouble("tds"), data.getDouble("pH"));
    }

    public String display() {
        return String.format(Locale.ROOT,
                "id=%d, name=%s, packet_no=%d%n"
                        + "   temperature=%.1f, humidity=%.1f, tds=%.1f, pH=%.1f",
                id, name, packetNo, temperature, humidity, tds, pH);
    }
}
