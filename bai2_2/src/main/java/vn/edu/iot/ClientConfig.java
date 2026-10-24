package vn.edu.iot;

import java.net.URI;

/** Command-line options; MSSV is required so no one accidentally uses a shared topic. */
public record ClientConfig(String studentId, String broker, int intervalSeconds) {
    public static final String DEFAULT_BROKER = "tcp://broker.hivemq.com:1883";

    public ClientConfig {
        if (studentId == null || !studentId.matches("[A-Za-z0-9_-]+")) {
            throw new IllegalArgumentException("MSSV must contain only letters, digits, '_' or '-'.");
        }
        if (intervalSeconds < 1) {
            throw new IllegalArgumentException("Interval must be a positive number of seconds.");
        }
        URI uri = URI.create(broker);
        if (!"tcp".equals(uri.getScheme()) || uri.getHost() == null
                || uri.getPort() < 1 || uri.getPort() > 65535
                || uri.getUserInfo() != null || uri.getQuery() != null || uri.getFragment() != null
                || (uri.getPath() != null && !uri.getPath().isEmpty())) {
            throw new IllegalArgumentException("Broker must be tcp://host:port (for example, "
                    + DEFAULT_BROKER + ").");
        }
    }

    public static ClientConfig parse(String[] args) {
        String studentId = null;
        String broker = DEFAULT_BROKER;
        int interval = 5;
        for (int i = 0; i < args.length; i++) {
            String option = args[i];
            if (!option.equals("--mssv") && !option.equals("--broker") && !option.equals("--interval")) {
                throw new IllegalArgumentException("Unknown option: " + option);
            }
            if (i + 1 == args.length || args[i + 1].startsWith("--")) {
                throw new IllegalArgumentException("Missing value for " + option);
            }
            String value = args[++i];
            switch (option) {
                case "--mssv" -> studentId = value;
                case "--broker" -> broker = value;
                case "--interval" -> {
                    try {
                        interval = Integer.parseInt(value);
                    } catch (NumberFormatException e) {
                        throw new IllegalArgumentException("Interval must be a positive integer.");
                    }
                }
                default -> throw new IllegalArgumentException("Unknown option: " + option);
            }
        }
        return new ClientConfig(studentId, broker, interval);
    }

    public String telemetryTopic() {
        return "it4735e/" + studentId + "/telemetry";
    }

    public String subscriptionTopic() {
        return "it4735e/" + studentId + "/#";
    }

    public String statusTopic() {
        return "it4735e/" + studentId + "/status";
    }
}
