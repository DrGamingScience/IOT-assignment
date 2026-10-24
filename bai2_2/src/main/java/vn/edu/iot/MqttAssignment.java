package vn.edu.iot;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.json.JSONException;

/** One program performs both publishing and subscribing, including both optional extensions. */
public final class MqttAssignment implements AutoCloseable {
    private static final int QOS = 1;
    private static final long MQTT_TIMEOUT_MS = 15_000;
    private final ClientConfig config;
    private final MqttAsyncClient client;
    private final ScheduledExecutorService worker = Executors.newSingleThreadScheduledExecutor();
    private final AtomicBoolean closing = new AtomicBoolean();
    private final CountDownLatch stopped = new CountDownLatch(1);
    private volatile boolean ready;
    // Only the single worker thread changes this counter. It resets on a new program run.
    private long nextPacketNo = 126;

    MqttAssignment(ClientConfig config) throws MqttException {
        this.config = config;
        String clientId = "java-" + UUID.randomUUID();
        client = new MqttAsyncClient(config.broker(), clientId, new MemoryPersistence());
        client.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean reconnect, String serverURI) {
                ready = false;
                System.out.println((reconnect ? "Reconnected to " : "Connected to ") + serverURI);
                // SUBACK/PUBACK must be awaited off the Paho callback thread.
                try {
                    worker.execute(MqttAssignment.this::prepareSession);
                } catch (RejectedExecutionException e) {
                    if (!closing.get()) {
                        System.err.println("Cannot prepare session: " + e.getMessage());
                    }
                }
            }

            @Override
            public void connectionLost(Throwable cause) {
                ready = false;
                System.err.println("Connection lost: " + (cause == null ? "unknown reason" : cause.getMessage())
                        + ". Automatic reconnect is enabled; publishing is paused.");
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) {
                String payload = new String(message.getPayload(), StandardCharsets.UTF_8);
                System.out.println(formatReceived(config.statusTopic(), topic, payload));
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                // Publishing below waits for QoS 1 delivery confirmation on the worker thread.
            }
        });
        System.out.println("Client ID: " + clientId);
        System.out.println("Telemetry topic: " + config.telemetryTopic());
        System.out.println("Press Ctrl+C to stop.");
    }

    private MqttConnectOptions connectionOptions() {
        MqttConnectOptions options = new MqttConnectOptions();
        options.setMqttVersion(MqttConnectOptions.MQTT_VERSION_3_1_1);
        options.setCleanSession(true);
        options.setConnectionTimeout(10);
        options.setKeepAliveInterval(15);
        options.setAutomaticReconnect(true);
        // The broker sends this retained message if the connection ends unexpectedly.
        options.setWill(config.statusTopic(), "offline".getBytes(StandardCharsets.UTF_8), QOS, true);
        return options;
    }

    void run() throws InterruptedException {
        // Paho's automatic reconnect handles losses AFTER a successful connection.
        // Retry the first connection ourselves as well.
        while (!closing.get() && !client.isConnected()) {
            try {
                client.connect(connectionOptions()).waitForCompletion(MQTT_TIMEOUT_MS);
            } catch (MqttException e) {
                if (closing.get()) {
                    return;
                }
                System.err.println("Initial connection failed: " + e.getMessage() + ". Retrying in 5 seconds.");
                Thread.sleep(5_000);
            }
        }
        if (!closing.get()) {
            worker.scheduleWithFixedDelay(this::publishTelemetry, 0, config.intervalSeconds(), TimeUnit.SECONDS);
            stopped.await();
        }
    }

    private void prepareSession() {
        if (closing.get() || !client.isConnected()) {
            return;
        }
        try {
            // Clean sessions lose subscriptions; repeat this on EVERY connectComplete callback.
            var subscription = client.subscribe(config.subscriptionTopic(), QOS);
            subscription.waitForCompletion(MQTT_TIMEOUT_MS);
            if (subscription.getGrantedQos()[0] == 128) {
                throw new MqttException(MqttException.REASON_CODE_SUBSCRIBE_FAILED);
            }
            System.out.println("Subscribed: " + config.subscriptionTopic() + " (QoS 1)");
            client.publish(config.statusTopic(), "online".getBytes(StandardCharsets.UTF_8), QOS, true)
                    .waitForCompletion(MQTT_TIMEOUT_MS);
            System.out.println(">> Published retained online to " + config.statusTopic());
            ready = client.isConnected() && !closing.get();
        } catch (MqttException e) {
            ready = false;
            System.err.println("Session setup failed: " + e.getMessage());
            if (!closing.get()) {
                worker.schedule(this::prepareSession, 2, TimeUnit.SECONDS);
            }
        }
    }

    private void publishTelemetry() {
        if (closing.get() || !ready || !client.isConnected()) {
            return;
        }
        Telemetry reading = Telemetry.sample(nextPacketNo);
        try {
            var delivery = client.publish(config.telemetryTopic(),
                    reading.toJson().getBytes(StandardCharsets.UTF_8), QOS, false);
            // Count a new accepted publish once, even if confirmation is delayed or duplicated.
            nextPacketNo++;
            delivery.waitForCompletion(MQTT_TIMEOUT_MS);
            System.out.println(">> Published packet_no=" + reading.packetNo()
                    + " to " + config.telemetryTopic() + " (QoS 1 confirmed)");
        } catch (MqttException e) {
            System.err.println("Publish not confirmed: " + e.getMessage() + ". Program continues.");
        }
    }

    /** Catch bad messages here so a JSON error never escapes into Paho's network callbacks. */
    static String formatReceived(String statusTopic, String topic, String payload) {
        if (topic.equals(statusTopic)) {
            return "<< Status on " + topic + ": " + payload;
        }
        try {
            return "<< Received on " + topic + System.lineSeparator() + "   " + Telemetry.fromJson(payload).display();
        } catch (JSONException e) {
            return "JSON error on " + topic + ": " + e.getMessage() + " (continuing)";
        }
    }

    @Override
    public void close() {
        if (!closing.compareAndSet(false, true)) {
            return;
        }
        ready = false;
        worker.shutdownNow();
        try {
            if (client.isConnected()) {
                // A normal MQTT disconnect does not trigger Last Will; announce offline ourselves.
                client.publish(config.statusTopic(), "offline".getBytes(StandardCharsets.UTF_8), QOS, true)
                        .waitForCompletion(3_000);
                client.disconnect(1_000).waitForCompletion(3_000);
            }
        } catch (MqttException e) {
            System.err.println("Shutdown: " + e.getMessage());
        } finally {
            try {
                // Reset transport state even if a graceful disconnect failed.
                client.disconnectForcibly(0, 1_000);
            } catch (MqttException e) {
                System.err.println("Disconnect cleanup: " + e.getMessage());
            }
            try {
                client.close(true);
            } catch (MqttException e) {
                System.err.println("Close cleanup: " + e.getMessage());
            }
            stopped.countDown();
        }
    }

    public static void main(String[] args) {
        if (Arrays.asList(args).contains("--help")) {
            usage();
            return;
        }
        ClientConfig config;
        try {
            config = ClientConfig.parse(args);
        } catch (IllegalArgumentException e) {
            System.err.println(e.getMessage());
            usage();
            System.exit(2);
            return;
        }
        try (MqttAssignment app = new MqttAssignment(config)) {
            Thread shutdownHook = new Thread(app::close, "mqtt-shutdown");
            Runtime.getRuntime().addShutdownHook(shutdownHook);
            try {
                app.run();
            } finally {
                app.close();
                try {
                    Runtime.getRuntime().removeShutdownHook(shutdownHook);
                } catch (IllegalStateException ignored) {
                    // The JVM is already running the shutdown hook.
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (MqttException e) {
            System.err.println("Cannot create MQTT client: " + e.getMessage());
            System.exit(1);
        }
    }

    private static void usage() {
        System.out.println("Usage: java -jar mqtt-assignment-1.0.0.jar --mssv YOUR_MSSV"
                + " [--interval 5] [--broker tcp://broker.hivemq.com:1883]");
    }
}
