package oss

import (
	"bufio"
	"crypto/tls"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
)

// rdbTLSConfig 保存从 rdb.conf 解析到的 TLS/算法配置（对齐 rdbcomm sec_resolve 4 层模型）
type rdbTLSConfig struct {
	ossTLSEnable    string // [oss] tls_enable
	ossTLSAlgorithm string // [oss] tls_algorithm
	secTLSEnable    string // [security] tls_enable
	secTLSAlgorithm string // [security] tls_algorithm（全局兜底算法）
	secCertDir      string // [security] cert_dir
}

// parseRDBConfig 最小 INI 解析：仅关注工具段 [oss] 与全局段 [security]；
// 文件缺失/段缺失/格式错误均不报错，返回已解析到的部分（零值）。
func parseRDBConfig(path string) (*rdbTLSConfig, error) {
	cfg := &rdbTLSConfig{}
	if path == "" {
		return cfg, nil
	}
	f, err := os.Open(path)
	if err != nil {
		// 文件缺失：忽略，回退默认值
		return cfg, nil
	}
	defer f.Close()

	section := ""
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") || strings.HasPrefix(line, ";") {
			continue
		}
		if strings.HasPrefix(line, "[") && strings.HasSuffix(line, "]") {
			section = strings.TrimSpace(line[1 : len(line)-1])
			continue
		}
		if section != OSS_TOOL_SECTION && section != SEC_GLOBAL_SECTION {
			continue
		}
		idx := strings.Index(line, "=")
		if idx < 0 {
			continue
		}
		key := strings.TrimSpace(line[:idx])
		val := strings.TrimSpace(line[idx+1:])
		switch section {
		case OSS_TOOL_SECTION:
			switch key {
			case SEC_TOOL_TLS_KEY:
				cfg.ossTLSEnable = val
			case SEC_TOOL_ALGORITHM_KEY:
				cfg.ossTLSAlgorithm = val
			}
		case SEC_GLOBAL_SECTION:
			switch key {
			case SEC_GLOBAL_TLS_KEY:
				cfg.secTLSEnable = val
			case SEC_TOOL_ALGORITHM_KEY:
				cfg.secTLSAlgorithm = val
			case SEC_GLOBAL_CERT_DIR_KEY:
				cfg.secCertDir = val
			}
		}
	}
	return cfg, nil
}

// mapCiphersuiteToPrefix 将算法/套件字符串映射为证书文件名前缀。
// AES 族 → ed25519；SM4/国密(sm2) → sm2（Go 标准库不支持，调用方 fail-closed）；空 → ed25519。
func mapCiphersuiteToPrefix(algo string) string {
	upper := strings.ToUpper(algo)
	switch {
	case strings.Contains(upper, "SM4"), strings.Contains(upper, "SM2"):
		return "sm2"
	case strings.Contains(upper, "AES"), strings.Contains(upper, "ED25519"), algo == "":
		return "ed25519"
	default:
		return "ed25519"
	}
}

// chooseStr 按 CLI > 环境变量 > 配置文件 > 默认值 的优先级选取配置。
// 对齐 C 侧 sec_resolve_str 的 4 层模型：env(第1) > 工具段(第2) > 全局段(第3) > 默认(第4)。
// CLI 视为高于全部配置文件层的显式覆盖（C 工具无独立 CLI 层，故置于最前）。
func chooseStr(cliVal, fileVal, envVal, def string) string {
	if cliVal != "" {
		return cliVal
	}
	if envVal != "" {
		return envVal
	}
	if fileVal != "" {
		return fileVal
	}
	return def
}

// resolveCertPaths 依据 4 层优先级解析证书/私钥路径。
// 显式 --cert-path/--key-path 直接采用；否则按 <cert-dir>/<前缀>_host.crt|key 解析。
func resolveCertPaths(config *Config, rdb *rdbTLSConfig) (certPath, keyPath, prefix string) {
	certDir := chooseStr(config.CertDir, rdb.secCertDir, os.Getenv(RPC_TLS_CERT_DIR_ENV), DEFAULT_CERT_DIR)

	fileAlgo := rdb.ossTLSAlgorithm
	if fileAlgo == "" {
		fileAlgo = rdb.secTLSAlgorithm
	}
	algo := chooseStr(config.TLSAlgorithm, fileAlgo, os.Getenv(OSS_TLS_ALGORITHM_ENV), DEFAULT_TLS_PREFIX)
	prefix = mapCiphersuiteToPrefix(algo)

	if config.CertPath != "" && config.KeyPath != "" {
		return config.CertPath, config.KeyPath, prefix
	}
	certPath = filepath.Join(certDir, prefix+CERT_FILE_SUFFIX)
	keyPath = filepath.Join(certDir, prefix+KEY_FILE_SUFFIX)
	return certPath, keyPath, prefix
}

// buildTLSConfig 校验并构造受限的 *tls.Config（MinVersion=TLS1.2，仅 AES256-GCM 套件）。
func buildTLSConfig(certPath, keyPath string) (*tls.Config, error) {
	if _, err := tls.LoadX509KeyPair(certPath, keyPath); err != nil {
		return nil, fmt.Errorf("cannot load certificate/key pair (%s, %s): %w", certPath, keyPath, err)
	}
	return &tls.Config{
		MinVersion: tls.VersionTLS12,
		CipherSuites: []uint16{
			// 优先 AES256-GCM
			tls.TLS_AES_256_GCM_SHA384,
			tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
			tls.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
			// HTTP/2 必需套件（仍属 AES-GCM，非弱 CBC）
			tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
			tls.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
		},
	}, nil
}

// buildServingTLS 解析配置并构建启动用 TLS 配置；任何失败均返回 error（fail-closed）。
func buildServingTLS(config *Config) (tlsCfg *tls.Config, certPath, keyPath string, err error) {
	rdb, parseErr := parseRDBConfig(config.ConfigPath)
	if parseErr != nil {
		return nil, "", "", parseErr
	}
	certPath, keyPath, _ = resolveCertPaths(config, rdb)
	tlsCfg, err = buildTLSConfig(certPath, keyPath)
	if err != nil {
		return nil, certPath, keyPath, err
	}
	return tlsCfg, certPath, keyPath, nil
}

// parseEnableStr 宽松布尔解析：1/true/yes/on（大小写不敏感）为真；
// 其余非空值视为已配置但为假；空/纯空白表示未配置（回退下一层）。
func parseEnableStr(s string) (val, configured bool) {
	s = strings.ToLower(strings.TrimSpace(s))
	if s == "" {
		return false, false
	}
	switch s {
	case "1", "true", "yes", "on":
		return true, true
	default:
		return false, true
	}
}

// knownFalseToken 判断是否为显式合法假值；用于区分"有意关闭"与"疑似拼写错误"，
// 后者按关闭处理但需要告警，避免运维误以为加密链路已启用。
func knownFalseToken(s string) bool {
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "0", "false", "no", "off":
		return true
	}
	return false
}

// resolveEnableValue 解析单个配置源的开关键值；已配置但为可疑假值时告警后仍按关闭处理。
func resolveEnableValue(source, val string) (enabled, configured bool) {
	v, ok := parseEnableStr(val)
	if ok && !v && !knownFalseToken(val) {
		log.Printf("警告: %s=%q 非真值(期望 1/true/yes/on)，按关闭处理，服务将以明文 HTTP 启动", source, val)
	}
	return v, ok
}

// resolveTLSEnabled 解析 HTTPS 开关，优先级对齐 chooseStr 的 4 层模型：
// CLI 显式(--tls/--no-tls) > OSS_TLS_ENABLE_ENV > rdb.conf [oss] mtls_enable >
// [security] tls_enable > 默认关闭（HTTP）。
func resolveTLSEnabled(config *Config) bool {
	if config.TLSSpecified {
		return config.TLSValue
	}
	if v, ok := resolveEnableValue("环境变量 "+OSS_TLS_ENABLE_ENV, os.Getenv(OSS_TLS_ENABLE_ENV)); ok {
		return v
	}
	rdb, _ := parseRDBConfig(config.ConfigPath)
	if v, ok := resolveEnableValue("rdb.conf [oss] "+SEC_TOOL_TLS_KEY, rdb.ossTLSEnable); ok {
		return v
	}
	if v, ok := resolveEnableValue("rdb.conf [security] "+SEC_GLOBAL_TLS_KEY, rdb.secTLSEnable); ok {
		return v
	}
	return false
}
