package org.example;

import io.github.wasabithumb.jtoml.JToml;
import io.github.wasabithumb.jtoml.document.TomlDocument;
import io.github.wasabithumb.jtoml.except.TomlException;

import java.nio.file.Path;

public class Addons {
    public static Config get_config() throws TomlException {
        JToml toml = JToml.jToml();
        TomlDocument doc = toml.read(Path.of("./config.toml"));
        return toml.fromToml(Config.class, doc);
    }
}
