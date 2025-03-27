package config

import (
	"fmt"
	"os"
	"time"

	"github.com/spf13/viper"
)

type (
	Config struct {
		App   `mapstructure:"app"`
		HTTP  `mapstructure:"http"`
		Mongo `mapstructure:"mongo"`
	}

	App struct {
		Name     string `mapstructure:"name"`
		Version  string `mapstructure:"version"`
		LogLevel string `mapstructure:"log_level"`
	}

	HTTP struct {
		Addr string `mapstructure:"addr"`
		Port string `mapstructure:"port"`
	}
	Mongo struct {
		User           string `mapstructure:"user"`
		Password       string `mapstructure:"password"`
		Host           string `mapstructure:"host"`
		Port           string `mapstructure:"port"`
		Database       string `mapstructure:"database"`
		MigrationsPath string `mapstructure:"migrations_path"`

		RetryConnectionAttempts int           `mapstructure:"retry_connection_attempts"`
		RetryConnectionTimeout  time.Duration `mapstructure:"retry_connection_timeout"`
	}
)

func New() (*Config, error) {
	cfg := Config{}
	v := viper.New()
	v.SetConfigName("config")
	v.SetConfigType("yaml")
	v.AddConfigPath("config/")

	err := v.ReadInConfig()
	if err != nil {
		return nil, fmt.Errorf("fatal error reading config file: %s", err)
	}

	// Заменяем переменные окружения в значениях
	for _, k := range v.AllKeys() {
		anyValue := v.Get(k)
		str, ok := anyValue.(string)
		if !ok {
			continue
		}
		replaced := os.ExpandEnv(str)
		v.Set(k, replaced)
	}

	err = v.Unmarshal(&cfg)
	if err != nil {
		return nil, fmt.Errorf("fatal error unmarshalling config: %w", err)
	}

	return &cfg, nil
}
