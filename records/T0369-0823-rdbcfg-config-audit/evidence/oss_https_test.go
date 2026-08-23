package oss

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"io"
	"math/big"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// newTestCert 生成自签 ED25519 证书/私钥到临时文件，返回路径。
func newTestCert(t *testing.T) (certPath, keyPath string) {
	t.Helper()
	_, priv, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		t.Fatalf("生成密钥失败: %v", err)
	}
	tmpl := x509.Certificate{
		SerialNumber:          big.NewInt(1),
		Subject:               pkix.Name{CommonName: "localhost"},
		NotBefore:             time.Now().Add(-time.Hour),
		NotAfter:              time.Now().Add(time.Hour),
		DNSNames:              []string{"localhost"},
		KeyUsage:              x509.KeyUsageDigitalSignature,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
	}
	der, err := x509.CreateCertificate(rand.Reader, &tmpl, &tmpl, priv.Public(), priv)
	if err != nil {
		t.Fatalf("创建证书失败: %v", err)
	}
	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der})
	keyPEM, err := x509.MarshalPKCS8PrivateKey(priv)
	if err != nil {
		t.Fatalf("编码私钥失败: %v", err)
	}
	keyPEMBlock := pem.EncodeToMemory(&pem.Block{Type: "PRIVATE KEY", Bytes: keyPEM})

	dir := t.TempDir()
	certPath = filepath.Join(dir, "host.crt")
	keyPath = filepath.Join(dir, "host.key")
	if err := os.WriteFile(certPath, certPEM, 0600); err != nil {
		t.Fatalf("写证书失败: %v", err)
	}
	if err := os.WriteFile(keyPath, keyPEMBlock, 0600); err != nil {
		t.Fatalf("写私钥失败: %v", err)
	}
	return certPath, keyPath
}

func TestMapCiphersuiteToPrefix(t *testing.T) {
	cases := map[string]string{
		"":                                "ed25519",
		"ed25519":                         "ed25519",
		"TLS_AES_256_GCM_SHA384":          "ed25519",
		"TLS_ECDHE_RSA_AES256_GCM_SHA384": "ed25519",
		"TLS_SM4_GCM_SM3":                 "sm2",
		"sm2":                             "sm2",
	}
	for in, want := range cases {
		if got := mapCiphersuiteToPrefix(in); got != want {
			t.Errorf("mapCiphersuiteToPrefix(%q)=%q, want %q", in, got, want)
		}
	}
}

func TestParseRDBConfig(t *testing.T) {
	dir := t.TempDir()
	cfgPath := filepath.Join(dir, "rdb.conf")
	content := `[oss]
mtls_enable = 1
tls_algorithm = TLS_AES_256_GCM_SHA384

[security]
tls_enable = 1
ciphersuites = TLS_SM4_GCM_SM3
cert_dir = /opt/aio/cfg/certs
`
	if err := os.WriteFile(cfgPath, []byte(content), 0600); err != nil {
		t.Fatal(err)
	}
	cfg, err := parseRDBConfig(cfgPath)
	if err != nil {
		t.Fatalf("parseRDBConfig error: %v", err)
	}
	if cfg.ossTLSAlgorithm != "TLS_AES_256_GCM_SHA384" {
		t.Errorf("ossTLSAlgorithm=%q", cfg.ossTLSAlgorithm)
	}
	if cfg.secCiphersuites != "TLS_SM4_GCM_SM3" {
		t.Errorf("secCiphersuites=%q", cfg.secCiphersuites)
	}
	if cfg.secCertDir != "/opt/aio/cfg/certs" {
		t.Errorf("secCertDir=%q", cfg.secCertDir)
	}

	// 文件缺失：不报错，返回零值
	miss, err := parseRDBConfig(filepath.Join(dir, "nope.conf"))
	if err != nil || miss.secCertDir != "" {
		t.Errorf("缺失文件应返回零值 cfg, got %+v err=%v", miss, err)
	}
}

func TestResolveCertPaths(t *testing.T) {
	dir := t.TempDir()
	// 显式 --cert-path/--key-path 直接采用
	cfg := &Config{CertPath: "/a/c.crt", KeyPath: "/a/c.key"}
	cp, kp, prefix := resolveCertPaths(cfg, &rdbTLSConfig{})
	if cp != "/a/c.crt" || kp != "/a/c.key" || prefix != "ed25519" {
		t.Errorf("显式路径未采用: %s %s %s", cp, kp, prefix)
	}

	// 默认前缀解析
	cfg = &Config{}
	cp, kp, prefix = resolveCertPaths(cfg, &rdbTLSConfig{})
	want := filepath.Join(DEFAULT_CERT_DIR, "ed25519_host.crt")
	if cp != want || prefix != "ed25519" {
		t.Errorf("默认解析=%s, want %s", cp, want)
	}

	// rdb.conf [security] cert_dir + 工具段 tls_algorithm=SM4 → sm2 前缀
	cfg = &Config{}
	rdb := &rdbTLSConfig{ossTLSAlgorithm: "TLS_SM4_GCM_SM3", secCertDir: dir}
	cp, kp, prefix = resolveCertPaths(cfg, rdb)
	if prefix != "sm2" {
		t.Errorf("前缀应为 sm2, got %s", prefix)
	}
	if cp != filepath.Join(dir, "sm2_host.crt") {
		t.Errorf("sm2 证书路径=%s", cp)
	}

	// F1：环境变量应高于配置文件（对齐 C sec_resolve_str: env > 工具段 > 全局段）
	t.Setenv(OSS_TLS_ALGORITHM_ENV, "TLS_SM4_GCM_SM3")
	cfg = &Config{}
	rdb = &rdbTLSConfig{ossTLSAlgorithm: "TLS_AES_256_GCM_SHA384", secCertDir: dir}
	_, _, prefix = resolveCertPaths(cfg, rdb)
	if prefix != "sm2" {
		t.Errorf("env 应覆盖配置文件：前缀应为 sm2, got %s", prefix)
	}

	t.Setenv(RPC_TLS_CERT_DIR_ENV, "/env/cert/dir")
	cfg = &Config{}
	rdb = &rdbTLSConfig{secCertDir: dir}
	cp, _, _ = resolveCertPaths(cfg, rdb)
	if !strings.HasPrefix(cp, "/env/cert/dir") {
		t.Errorf("env 证书目录应覆盖配置文件：got %s", cp)
	}
}

func TestBuildTLSConfig(t *testing.T) {
	certPath, keyPath := newTestCert(t)
	tlsCfg, err := buildTLSConfig(certPath, keyPath)
	if err != nil {
		t.Fatalf("buildTLSConfig 合法证书应成功: %v", err)
	}
	if tlsCfg.MinVersion != tls.VersionTLS12 {
		t.Errorf("MinVersion 应为 TLS1.2")
	}

	// AC-3 缺失 fail-closed
	if _, err := buildTLSConfig("/no/such.crt", "/no/such.key"); err == nil {
		t.Error("缺失证书应返回错误")
	}
	// AC-4 非法 fail-closed：证书合法但私钥内容损坏
	badKey := filepath.Join(t.TempDir(), "bad.key")
	if err := os.WriteFile(badKey, []byte("not a key"), 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := buildTLSConfig(certPath, badKey); err == nil {
		t.Error("公私钥不匹配应返回错误")
	}
}

func TestBuildServingTLSFailClosed(t *testing.T) {
	// sm2 前缀证书不存在 → fail-closed
	cfg := &Config{TLSAlgorithm: "sm2"}
	if _, _, _, err := buildServingTLS(cfg); err == nil {
		t.Error("sm2(国密) 证书缺失应 fail-closed")
	}
	// 显式缺失路径 → fail-closed
	cfg = &Config{CertPath: "/x.crt", KeyPath: "/x.key"}
	if _, _, _, err := buildServingTLS(cfg); err == nil {
		t.Error("显式缺失证书应 fail-closed")
	}
}

func TestServeHTTPSHandshake(t *testing.T) {
	certPath, keyPath := newTestCert(t)
	cfg := &Config{CertPath: certPath, KeyPath: keyPath}
	tlsCfg, _, _, err := buildServingTLS(cfg)
	if err != nil {
		t.Fatalf("buildServingTLS 失败: %v", err)
	}

	ts := httptest.NewUnstartedServer(newTestRouter())
	ts.TLS = tlsCfg
	ts.StartTLS()
	defer ts.Close()

	// AC-1 HTTPS 客户端握手成功
	client := &http.Client{Transport: &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}}
	resp, err := client.Get(ts.URL + "/")
	if err != nil {
		t.Fatalf("HTTPS GET 应成功: %v", err)
	}
	resp.Body.Close()

	// AC-2 明文 HTTP 客户端到该端口握手失败（TLS 必需）
	hostPort := strings.TrimPrefix(ts.URL, "https://")
	plain, err := net.Dial("tcp", hostPort)
	if err != nil {
		t.Fatal(err)
	}
	defer plain.Close()
	_ = plain.SetDeadline(time.Now().Add(3 * time.Second))
	if _, err := plain.Write([]byte("GET / HTTP/1.0\r\n\r\n")); err != nil {
		t.Fatal(err)
	}
	buf := make([]byte, 64)
	n, rerr := plain.Read(buf)
	// 明文请求应被拒：读错误，或服务端返回明文 400（非 TLS 成功响应）；绝不应出现成功业务响应
	if rerr == nil && strings.Contains(string(buf[:n]), "ok") {
		t.Error("明文请求不应得到成功响应（无明文 HTTP 服务）")
	}

	// AC-5 弱套件（TLS_RSA_WITH_AES_128_CBC_SHA）握手被拒
	weakConn, err := tls.Dial("tcp", hostPort, &tls.Config{
		InsecureSkipVerify: true,
		MaxVersion:         tls.VersionTLS12,
		CipherSuites:       []uint16{tls.TLS_RSA_WITH_AES_128_CBC_SHA},
	})
	if err == nil {
		weakConn.Close()
		t.Error("弱套件握手应被拒")
	}
}

// newTestRouter 返回一个最小路由，用于握手验证。
func newTestRouter() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, "ok")
	})
	return mux
}
