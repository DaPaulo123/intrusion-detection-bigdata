package org.example;

public record Settings(KafkaSettings kafka, SimulationSettings simulation) {
    // Such a weird way to recreate the .. pattern
    public static final class SettingsBuilder {
        KafkaSettings.KafkaSettingsBuilder kafka;
        SimulationSettings simulation;

        public SettingsBuilder kafka(KafkaSettings.KafkaSettingsBuilder kafka) {
            this.kafka = kafka;
            return this;
        }

        public SettingsBuilder simulation(SimulationSettings simulation) {
            this.simulation = simulation;
            return this;
        }

        public SettingsBuilder settings(Settings settings) {
            this.kafka = new KafkaSettings.KafkaSettingsBuilder().kafka_settings(settings.kafka);
            this.simulation = settings.simulation;
            return this;
        }

        public Settings build() {
            return new Settings(kafka.build(), simulation);
        }
    }
}

