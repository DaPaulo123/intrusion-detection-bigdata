package org.example;

import io.github.wasabithumb.jtoml.JToml;
import io.github.wasabithumb.jtoml.document.TomlDocument;
import io.github.wasabithumb.jtoml.except.TomlException;

import java.nio.file.Path;
import java.util.List;

import static java.lang.System.getenv;

public final class Addons {
    public static Settings get_config() throws TomlException {
        JToml toml = JToml.jToml();
        TomlDocument doc = toml.read(Path.of("./settings.toml"));
        Settings config_settings = toml.fromToml(Settings.class, doc);
        Settings.SettingsBuilder custom_config = new Settings.SettingsBuilder().settings(config_settings);

        // Where is Optional when we need it
        String sys_kafka_server = null;
        try {
            sys_kafka_server = getenv("KAFKA_BOOTSTRAP_SERVERS");
        } catch (Exception _) {
        }
        if (sys_kafka_server != null && !sys_kafka_server.isEmpty()) {
            custom_config.kafka.bootstrap_servers(sys_kafka_server);
        }

        return custom_config.build();

    }
}
