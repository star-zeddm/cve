漏洞库
https://github.com/zhaopeiym/quartzui

认证绕过 - 硬编码密钥导致的 Token 伪造
1.使用硬编码密钥生成token
https://github.com/zhaopeiym/quartzui/blob/dev/QuartzNetAPI/Host/Common/EncryptDecryptExtension.cs

private static readonly string des3key = ConfigurationManager.GetTryConfig("DES3Key", "73495773n~@^v&B6");

2.认证逻辑仅验证 Token 解密后的日期是否为当天
https://github.com/zhaopeiym/quartzui/blob/dev/QuartzNetAPI/Host/Filters/AuthorizationFilter.cs

var time = token.DES3Decrypt().ToDateTime();
if (DateTime.Now.Date == time.Date)
    return Task.CompletedTask;

