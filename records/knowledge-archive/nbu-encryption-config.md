# NBU 加密配置速查

> 复用来源：records/0727-nbu-encryption-review/, records/0727-nbu-kb-research/

## 传输加密（DTE）

```bash
# 全局模式: 0=preferred_off, 1=preferred_on, 2=enforced
nbseccmd -setsecurityconfig -dteglobalmode 1

# 介质服务器级别
nbseccmd -setsecurityconfig -dtemediamode on -mediaserver <host>

# 查看状态
nbseccmd -getsecurityconfig -dteglobalmode
```

## 客户端存储加密

```bash
# 创建密钥文件
bpkeyutil -create

# 客户端配置 (bp.conf)
CRYPT_KIND = STANDARD
CRYPT_ALLOW = REQUIRED
CRYPT_CIPHER = AES-256-CFB
```

## MSDP 加密

```bash
# 无 KMS: contentrouter.cfg 加 encrypt
ServerOptions=fast,verify_data_read,encrypt

# 有 KMS
setting encryption enable-kms kms_server=<host> key_group=<组名>
```

## 关键约束

- DTE enforced 模式下不可关闭
- 版本 < 9.1 的主机自动降级 DTE
- 客户端加密小文件场景 CPU 负载高
- KMS 密钥丢失 = 对应备份永久不可恢复
