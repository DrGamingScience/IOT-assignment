package vn.edu.iot;

public class ConfigSmokeTest {
    private static int checks;

    public static void main(String[] args) {
        ClientConfig config = ClientConfig.parse(new String[]{"--mssv", "20231234"});
        check(config.broker().equals("tcp://broker.hivemq.com:1883"));
        check(config.intervalSeconds() == 5);
        check(config.telemetryTopic().equals("it4735e/20231234/telemetry"));
        check(config.subscriptionTopic().equals("it4735e/20231234/#"));
        check(config.statusTopic().equals("it4735e/20231234/status"));
        ClientConfig custom = ClientConfig.parse(new String[]{"--mssv", "test_01", "--interval", "2",
                "--broker", "tcp://localhost:1884"});
        check(custom.intervalSeconds() == 2);
        check(custom.broker().equals("tcp://localhost:1884"));
        reject(new String[0]);
        reject(new String[]{"--mssv"});
        reject(new String[]{"--mssv", "student/#"});
        reject(new String[]{"--mssv", "+"});
        reject(new String[]{"--mssv", "student name"});
        reject(new String[]{"--mssv", "123", "--interval", "0"});
        reject(new String[]{"--mssv", "123", "--interval", "-1"});
        reject(new String[]{"--mssv", "123", "--interval", "abc"});
        reject(new String[]{"--mssv", "123", "--broker", "https://example.com:1883"});
        reject(new String[]{"--mssv", "123", "--broker", "tcp://example.com:1883/path"});
        reject(new String[]{"--mssv", "123", "--unknown", "x"});
        System.out.println("PASS: " + checks + " configuration checks.");
    }

    private static void check(boolean condition) {
        if (!condition) throw new AssertionError("Configuration check failed");
        checks++;
    }

    private static void reject(String[] args) {
        try {
            ClientConfig.parse(args);
            throw new AssertionError("Expected configuration rejection");
        } catch (IllegalArgumentException expected) {
            checks++;
        }
    }
}
