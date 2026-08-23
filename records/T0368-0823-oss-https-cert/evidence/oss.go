package oss

import (
	"context"
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"runtime/pprof"

	"github.com/minio/mux"
	cli "github.com/urfave/cli/v3"
)

var ServerFlags = []cli.Flag{
	&cli.StringFlag{
		Name:  "store",
		Value: STORE_ROOT_DIR,
		// EnvVars: []string{"AIO_OSS_STORE"},
	},
	&cli.StringFlag{
		Name:  "log-path",
		Value: LOG_DIR,
		// EnvVars: []string{"AIO_OSS_STORE"},
	},
	&cli.IntFlag{
		Name:  "port",
		Value: int64(PORT),
		// EnvVars: []string{"AIO_OSS_PORT"},
	},
	&cli.BoolFlag{
		Name:  "profile",
		Value: false,
	},
	&cli.BoolFlag{
		Name:  "profile-http",
		Value: false,
	},
	&cli.StringFlag{
		Name:  "config",
		Value: DEFAULT_RDB_CONFIG_PATH,
		Usage: "rdb.conf 配置文件路径（INI），提供 TLS/算法配置",
	},
	&cli.StringFlag{
		Name:  "cert-dir",
		Value: "",
		Usage: "证书目录，存放按算法前缀命名的证书材料",
	},
	&cli.StringFlag{
		Name:  "tls-algorithm",
		Value: "",
		Usage: "证书算法前缀：ed25519（默认，Go 可加载）/ sm2（国密，Go 不支持→fail-closed）",
	},
	&cli.StringFlag{
		Name:  "cert-path",
		Value: "",
		Usage: "显式服务端证书（PEM），设置后忽略按前缀解析",
	},
	&cli.StringFlag{
		Name:  "key-path",
		Value: "",
		Usage: "显式服务端私钥（PEM），设置后忽略按前缀解析",
	},
}

var serverCmd = &cli.Command{
	Name:   "server",
	Usage:  "start object storage server",
	Action: serverMain,
	Flags:  ServerFlags,
	OnUsageError: func(ctx context.Context, cmd *cli.Command, err error, isSubcommand bool) error {
		panic(err)
	},
}

func registerAPIRouter(router *mux.Router) {
	api := OssServer{}
	router.Methods(http.MethodHead).HandlerFunc(httpTrace(api.HeadHandler))
	router.Methods(http.MethodGet).HandlerFunc(httpTrace(api.GetHandler))
	router.Methods(http.MethodPut).HandlerFunc(httpTrace(api.PutHandler))
	router.Methods(http.MethodPost).HandlerFunc(httpTrace(api.PostHandler))
	router.Methods(http.MethodOptions).HandlerFunc(httpTrace(api.OptionsHandler))
	router.Methods(http.MethodDelete).HandlerFunc(httpTrace(api.DeleteHandler))
	router.NotFoundHandler = http.HandlerFunc(api.NotFoundHandler)
}

func serverMain(ctx context.Context, cmd *cli.Command) error {

	GConfig = NewConfig()
	GConfig.BuildConfig(cmd)
	GConfig.InitStoreRootDir()

	err := os.MkdirAll(GConfig.LogDir, 0755)
	if err != nil {
		panic(err)
	}
	f, err := os.OpenFile(GConfig.LogDir+"/"+GConfig.LogFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		panic(err)
	}

	defer f.Close()

	log.SetOutput(f)

	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)

	log.Println("start server main")

	if GConfig.Profile {
		log.Println("start profile cpu")
		f, err := os.Create("cpu.pprof")
		if err != nil {
			panic(err)
		}
		pprof.StartCPUProfile(f)

		log.Println("start profile mem")
		f, err = os.Create("mem.pprof")
		if err != nil {
			panic(err)
		}
		pprof.WriteHeapProfile(f)

		log.Println("start profile goroutine")
		f, err = os.Create("goroutine.pprof")
		if err != nil {
			panic(err)
		}
		pprof.Lookup("goroutine").WriteTo(f, 2)
	}

	router := mux.NewRouter().SkipClean(true)
	registerAPIRouter(router)
	log.Printf("%+v\n", GConfig)

	if GConfig.ProfileHttp {
		go func() {
			httpProf := "0.0.0.0:6060"
			log.Printf("HTTP pprof listening at %q\n", httpProf)
			log.Println(http.ListenAndServe(httpProf, nil))
		}()
	}

	// TLS / HTTPS：先构建 TLS 配置，证书缺失/非法/算法不支持则 fail-closed 整体启动失败
	tlsCfg, certPath, keyPath, tlsErr := buildServingTLS(GConfig)
	if tlsErr != nil {
		log.Printf("TLS 配置失败（fail-closed），服务不起: %v", tlsErr)
		return tlsErr
	}

	go func() {
		if err := serveHTTPS(GConfig, router, tlsCfg, certPath, keyPath); err != nil {
			log.Println(err)
		}
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	<-c

	if GConfig.Profile {
		pprof.StopCPUProfile()
	}
	return nil
}

func serveHTTPS(config *Config, handler http.Handler, tlsCfg *tls.Config, certPath, keyPath string) error {
	addr := fmt.Sprintf(":%d", config.Port)
	srv := &http.Server{
		Addr:      addr,
		Handler:   handler,
		TLSConfig: tlsCfg,
	}
	return srv.ListenAndServeTLS(certPath, keyPath)
}
