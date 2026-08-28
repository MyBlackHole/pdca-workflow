set_xmakever("2.3.6")
-- -- 目前 rpc 还不满足要求，先注释掉
set_warnings("all", "error")
set_languages("c99", "cxx11")
add_cxflags("-Wno-error=deprecated-declarations", "-fno-strict-aliasing")
add_mxflags("-Wno-error=deprecated-declarations", "-fno-strict-aliasing")

add_rules("mode.release", "mode.debug")


-- add_includedirs("fsbackup_kernel_4.x/device")
rpc_version = "3.6.4.27"
fsdaemon_version = rpc_version
rdbcomm_version = "1.0.2.5"
s3tools_version = "1.0.1.4"
libobk_version = "1.0.1.7"
dmsbtex_version = "1.1.0.7"
bwlimit_version = "1.0.0.1"
s3tools_version_old = "1.5.0.8"
tls_keygen_version = "1.0.0.6"
rpc_keygen_version = "1.0.0.0"
fsbackup_kernel_version = "3.3.1.6"
xbsa_version = "1.1.1.7"
oss_version = "1.0.0.0"
-- s3tool_version_old = "1.0.0.2"


set_configvar("S3TOOLS_VERSION_OLD", s3tools_version_old)
set_configvar("S3TOOL_VERSION_OLD", s3tools_version_old)
set_configvar("RPC_VERSION", rpc_version)
set_configvar("FSDAEMON_VERSION", fsdaemon_version)
set_configvar("RDBCOMM_VERSION", rdbcomm_version)
set_configvar("S3TOOLS_VERSION", s3tools_version)
set_configvar("LIBOBK_VERSION", libobk_version)
set_configvar("DMSBTEX_VERSION", dmsbtex_version)
set_configvar("BWLIMIT_VERSION", bwlimit_version)
set_configvar("TLS_KEYGEN_VERSION", tls_keygen_version)
set_configvar("RPC_KEYGEN_VERSION", rpc_keygen_version)
set_configvar("FSBACKUP_KERNEL_VERSION", fsbackup_kernel_version)
set_configvar("XBSA_VERSION", xbsa_version)
set_configvar("OSS_VERSION", oss_version)
add_configfiles("version.h.in", "version.log.in")
add_includedirs("$(builddir)/")

user = "black"
arch = os.arch()
if arch == "x86_64" then
    arch = "x86_64"
elseif arch == "i386" then
    arch = "x86_64"
elseif arch == "aarch64" then
    arch = "aarch64"
elseif arch == "arm64" then
    arch = "aarch64"
end

lib_dir = "lib_" .. arch

-- F-139: 国密 TLS 采用 OpenSSL 4 单库方案（见 docs/adr/ADR-0001）, 本地源码包目录
-- 注意：URL 指向项目根目录，xmake 会按 packages/<首字母>/<名> 结构搜索本地包
add_repositories("local-repo " .. os.scriptdir())

includes("libs")
includes("bwlimit")
includes("s3-tool")
includes("dmsbtex")
includes("libobk")
includes("rpc")
includes("fs-backup")
includes("huanweicloun-sdk-s3-data-backup")
includes("rdbcomm")
includes("s3tools")
includes("rpc-keygen")
includes("xbsa")
includes("oss")

target("makeFsbackup")
    set_prefixdir("bin", {bindir = ""})
    set_kind("binary")
    add_files("main.go")
    version_name = "makeFsbackup.version"
    add_configfiles("version.in", {filename = version_name})
    add_installfiles("$(builddir)/" .. version_name)
    local _kernel_ver = fsbackup_kernel_version
    before_build(function (target)
        io.writefile("fsbackup_kernel_4.x/version.h", '#define VERSION "' .. _kernel_ver .. '"\n')
    end)
