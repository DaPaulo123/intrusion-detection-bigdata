package org.example;

import java.util.List;

public record KafkaSettings(List<String> bootstrap_servers, int retries, String acks) {
    public static final class KafkaSettingsBuilder {
        private List<String> bootstrap_servers;
        private int retries;
        private String acks;

        public KafkaSettingsBuilder bootstrap_servers(String... servers) {
            this.bootstrap_servers = List.of(servers);
            return this;
        }

        public KafkaSettingsBuilder retries(int retries) {
            this.retries = retries;
            return this;
        }

        public KafkaSettingsBuilder acks(String acks) {
            this.acks = acks;
            return this;
        }

        public KafkaSettingsBuilder kafka_settings(KafkaSettings original) {
            this.bootstrap_servers = original.bootstrap_servers;
            this.retries = original.retries;
            this.acks = original.acks;
            return this;
        }

        public KafkaSettings build() {
            return new KafkaSettings(bootstrap_servers, retries, acks);
        }
    }
}
